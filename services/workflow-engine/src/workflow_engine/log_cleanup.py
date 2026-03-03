from __future__ import annotations

import asyncio
import os
from datetime import datetime, timedelta, timezone
from typing import Any

from .logging import configure_logger

logger = configure_logger("log-cleanup")


def parse_iso8601(value: str) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def cutoff_for_days(retention_days: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=retention_days)


async def cleanup_valkey_stream(client: Any, retention_days: int) -> int:
    cutoff = cutoff_for_days(retention_days)
    start_id = "-"
    deleted = 0

    while True:
        items = await client.xrange("logs:stream", min=start_id, max="+", count=500)
        if not items:
            break

        delete_ids: list[str] = []
        for item_id, pairs in items:
            mapped: dict[str, str] = {}
            for idx in range(0, len(pairs), 2):
                if idx + 1 < len(pairs):
                    mapped[pairs[idx]] = pairs[idx + 1]

            dt = parse_iso8601(mapped.get("timestamp", ""))
            if dt and dt < cutoff:
                delete_ids.append(item_id)

        if delete_ids:
            deleted += await client.xdel("logs:stream", *delete_ids)

        if len(items) < 500:
            break
        start_id = items[-1][0]

    return deleted


def cleanup_postgres(retention_days: int) -> int:
    import psycopg

    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        return 0
    cutoff = cutoff_for_days(retention_days)

    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM jobs WHERE created_at < %s", (cutoff,))
            jobs_deleted = cur.rowcount
            cur.execute("DELETE FROM ingested_records WHERE observed_at < %s", (cutoff,))
            ingested_deleted = cur.rowcount
            cur.execute("DELETE FROM analysis_results WHERE analyzed_at < %s", (cutoff,))
            analysis_deleted = cur.rowcount
        conn.commit()

    return jobs_deleted + ingested_deleted + analysis_deleted


def cleanup_clickhouse(retention_days: int) -> int:
    import clickhouse_connect

    host = os.getenv("CLICKHOUSE_HOST", "clickhouse")
    port = int(os.getenv("CLICKHOUSE_PORT", "8123"))
    database = os.getenv("CLICKHOUSE_DB", "webup")
    user = os.getenv("CLICKHOUSE_USER", "default")
    password = os.getenv("CLICKHOUSE_PASSWORD", "")

    cutoff = cutoff_for_days(retention_days).strftime("%Y-%m-%d %H:%M:%S")

    client = clickhouse_connect.get_client(
        host=host,
        port=port,
        username=user,
        password=password,
        database=database,
    )
    client.command(f"ALTER TABLE {database}.logs_stream DELETE WHERE timestamp < toDateTime64('{cutoff}', 3)")
    # ClickHouse mutations are async; return 0 as immediate deleted count is not available.
    return 0


async def run_cleanup_once(retention_days: int) -> dict[str, int]:
    import redis.asyncio as redis

    r = redis.from_url(os.getenv("VALKEY_URL", "redis://valkey:6379/0"), decode_responses=True)
    valkey_deleted = await cleanup_valkey_stream(r, retention_days)
    postgres_deleted = cleanup_postgres(retention_days)
    clickhouse_deleted = cleanup_clickhouse(retention_days)

    summary = {
        "valkey_deleted": valkey_deleted,
        "postgres_deleted": postgres_deleted,
        "clickhouse_deleted": clickhouse_deleted,
    }
    logger.info("cleanup_completed", retention_days=retention_days, **summary)
    return summary


async def main() -> None:
    retention_days = int(os.getenv("LOG_RETENTION_DAYS", "14"))
    interval_seconds = int(os.getenv("CLEANUP_INTERVAL_SECONDS", str(24 * 60 * 60)))

    while True:
        try:
            await run_cleanup_once(retention_days)
        except Exception as exc:  # noqa: BLE001
            logger.error("cleanup_failed", error=str(exc))
        await asyncio.sleep(interval_seconds)


if __name__ == "__main__":
    asyncio.run(main())

from __future__ import annotations

import asyncio
import json
import os
import uuid
from datetime import datetime, timezone

import redis.asyncio as redis
import structlog

from .registry import INGESTOR_REGISTRY

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso", key="timestamp"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ]
)
logger = structlog.get_logger().bind(service_name="ingestor-fleet")


async def emit_log(client: redis.Redis, *, trace_id: str, job_id: str, message: str, severity: str = "info") -> None:
    await client.xadd(
        "logs:stream",
        {
            "trace_id": trace_id,
            "service_name": "ingestor-fleet",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "severity": severity,
            "job_id": job_id,
            "message": message,
        },
        maxlen=20000,
        approximate=True,
    )


async def main() -> None:
    client = redis.from_url(os.getenv("VALKEY_URL", "redis://valkey:6379/0"), decode_responses=True)
    stream_id = "0-0"

    while True:
        events = await client.xread({"ingestor:tasks": stream_id}, block=5000, count=20)
        for _, messages in events:
            for msg_id, fields in messages:
                stream_id = msg_id
                job_config = json.loads(fields["job_config"])
                job_id = job_config["job_id"]
                trace_id = fields.get("trace_id") or str(uuid.uuid4())

                plugin_name = job_config["ingestor_plugin"]
                plugin_cls = INGESTOR_REGISTRY.get(plugin_name)
                if plugin_cls is None:
                    await emit_log(client, trace_id=trace_id, job_id=job_id, message=f"Unknown plugin: {plugin_name}", severity="error")
                    continue

                ingestor = plugin_cls()
                raw = await ingestor.fetch(job_config)
                normalized = ingestor.normalize(raw)

                await client.xadd(
                    "ingestor:results",
                    {
                        "job_id": job_id,
                        "trace_id": trace_id,
                        "records": json.dumps(normalized),
                    },
                )
                await emit_log(client, trace_id=trace_id, job_id=job_id, message=f"Ingested {len(normalized)} records")
                logger.info("ingestion_complete", job_id=job_id, trace_id=trace_id, count=len(normalized))


if __name__ == "__main__":
    asyncio.run(main())

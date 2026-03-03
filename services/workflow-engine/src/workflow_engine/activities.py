from __future__ import annotations

import json
import os
import uuid
from typing import Any

import redis.asyncio as redis
from temporalio import activity

from .logging import configure_logger

logger = configure_logger("workflow-engine")


async def _emit_log(message: str, trace_id: str, job_id: str, severity: str = "info") -> None:
    client = redis.from_url(os.getenv("VALKEY_URL", "redis://valkey:6379/0"), decode_responses=True)
    await client.xadd(
        "logs:stream",
        {
            "trace_id": trace_id,
            "service_name": "workflow-engine",
            "severity": severity,
            "timestamp": activity.info().scheduled_time.isoformat(),
            "job_id": job_id,
            "message": message,
        },
        maxlen=20000,
        approximate=True,
    )


@activity.defn(name="run_ingestor")
async def run_ingestor(job_config: dict[str, Any]) -> list[dict[str, Any]]:
    trace_id = str(uuid.uuid4())
    await _emit_log("Dispatching ingestor task", trace_id, job_config["job_id"])

    client = redis.from_url(os.getenv("VALKEY_URL", "redis://valkey:6379/0"), decode_responses=True)
    payload = json.dumps(job_config)
    await client.xadd("ingestor:tasks", {"job_id": job_config["job_id"], "trace_id": trace_id, "job_config": payload})

    # Stub data until fleet implements synchronous callback/response stream.
    return [
        {
            "record_id": "sample-1",
            "domain": job_config["ingestor_plugin"],
            "payload": {"price": 123.45, "symbol": "WEBUP"},
            "source": "stub",
        }
    ]


@activity.defn(name="run_analyzer")
async def run_analyzer(payload: dict[str, Any]) -> dict[str, Any]:
    job_config = payload["job_config"]
    trace_id = str(uuid.uuid4())
    await _emit_log("Dispatching analyzer task", trace_id, job_config["job_id"])

    client = redis.from_url(os.getenv("VALKEY_URL", "redis://valkey:6379/0"), decode_responses=True)
    await client.xadd(
        "analyzer:tasks",
        {
            "job_id": job_config["job_id"],
            "trace_id": trace_id,
            "task": json.dumps(payload),
        },
    )

    return {"summary": "Analyzer dispatched", "model": job_config["analyzer_plugin"]["model"]}

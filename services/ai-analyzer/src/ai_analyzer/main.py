from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime, timezone
from typing import Any

import httpx
import redis.asyncio as redis
import structlog
from fastapi import FastAPI
from pydantic import BaseModel

from .prompt_factory import build_prompt

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso", key="timestamp"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ]
)
logger = structlog.get_logger().bind(service_name="ai-analyzer")

app = FastAPI(title="AI Analyzer")


class AnalyzeRequest(BaseModel):
    provider: str
    model: str
    temperature: float
    prompt_template_id: str
    payload: dict[str, Any]


async def analyze_with_provider(req: AnalyzeRequest) -> dict[str, Any]:
    prompt = build_prompt(req.prompt_template_id, json.dumps(req.payload))
    timeout_seconds = float(os.getenv("ANALYZER_TIMEOUT_SECONDS", "180"))
    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        if req.provider == "ollama":
            ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
            response = await client.post(
                f"{ollama_host}/api/generate",
                json={
                    "model": req.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": req.temperature},
                },
            )
            response.raise_for_status()
            data = response.json()
            text = data.get("response", "")
        else:
            base_url = os.getenv("OPENAI_BASE_URL", "http://ollama:11434/v1")
            api_key = os.getenv("OPENAI_API_KEY", "dev-key")
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": req.model,
                    "temperature": req.temperature,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            response.raise_for_status()
            data = response.json()
            text = data["choices"][0]["message"]["content"]

    return {"model": req.model, "provider": req.provider, "result": text}


@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    return await analyze_with_provider(req)


async def emit_log(client: redis.Redis, trace_id: str, job_id: str, message: str, severity: str = "info") -> None:
    await client.xadd(
        "logs:stream",
        {
            "trace_id": trace_id,
            "service_name": "ai-analyzer",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "severity": severity,
            "job_id": job_id,
            "message": message,
        },
        maxlen=20000,
        approximate=True,
    )


async def consume_tasks() -> None:
    client = redis.from_url(os.getenv("VALKEY_URL", "redis://valkey:6379/0"), decode_responses=True)
    stream_id = "0-0"

    while True:
        events = await client.xread({"analyzer:tasks": stream_id}, block=5000, count=20)
        for _, messages in events:
            for msg_id, fields in messages:
                stream_id = msg_id
                payload = json.loads(fields["task"])
                job_config = payload["job_config"]
                req = AnalyzeRequest(
                    provider=job_config["analyzer_plugin"]["provider"],
                    model=job_config["analyzer_plugin"]["model"],
                    temperature=job_config["analyzer_plugin"]["temperature"],
                    prompt_template_id=job_config["analyzer_plugin"]["prompt_template_id"],
                    payload={"records": payload["data"]},
                )
                try:
                    # Retry once for transient cold-start/model-load failures.
                    try:
                        result = await analyze_with_provider(req)
                    except Exception:  # noqa: BLE001
                        result = await analyze_with_provider(req)
                    await client.xadd(
                        "analyzer:results",
                        {
                            "job_id": job_config["job_id"],
                            "trace_id": fields.get("trace_id", ""),
                            "result": json.dumps(result),
                        },
                    )
                    await emit_log(client, fields.get("trace_id", ""), job_config["job_id"], "Analysis complete")
                except Exception as exc:  # noqa: BLE001
                    details = str(exc) or repr(exc)
                    logger.error("analysis_failed", error=details, job_id=job_config["job_id"])
                    await emit_log(
                        client,
                        fields.get("trace_id", ""),
                        job_config["job_id"],
                        f"Analysis failed: {details}",
                        severity="error",
                    )


@app.on_event("startup")
async def startup() -> None:
    asyncio.create_task(consume_tasks())

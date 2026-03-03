from __future__ import annotations

import asyncio
import json
import os

import redis.asyncio as redis
from temporalio.client import Client
from temporalio.exceptions import WorkflowAlreadyStartedError

from .workflows import PipelineWorkflow


async def main() -> None:
    client = await Client.connect(os.getenv("TEMPORAL_ADDRESS", "temporal:7233"))
    r = redis.from_url(os.getenv("VALKEY_URL", "redis://valkey:6379/0"), decode_responses=True)

    stream_id = os.getenv("PIPELINE_STREAM_START_ID", "$")
    while True:
        results = await r.xread({"pipeline:events": stream_id}, block=5000, count=50)
        for _, messages in results:
            for msg_id, fields in messages:
                stream_id = msg_id
                if fields.get("type") != "job.trigger":
                    continue
                job_config = json.loads(fields["job_config"])
                try:
                    await client.start_workflow(
                        PipelineWorkflow.run,
                        job_config,
                        id=f"pipeline-{job_config['job_id']}-{msg_id}",
                        task_queue="pipeline-task-queue",
                    )
                except WorkflowAlreadyStartedError:
                    continue


if __name__ == "__main__":
    asyncio.run(main())

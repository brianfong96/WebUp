from __future__ import annotations

import asyncio
import os

from temporalio.client import Client
from temporalio.worker import Worker

from .activities import run_analyzer, run_ingestor
from .workflows import PipelineWorkflow


async def main() -> None:
    address = os.getenv("TEMPORAL_ADDRESS", "temporal:7233")
    client = await Client.connect(address)

    worker = Worker(
        client,
        task_queue="pipeline-task-queue",
        workflows=[PipelineWorkflow],
        activities=[run_ingestor, run_analyzer],
    )

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())

from __future__ import annotations

from datetime import timedelta
from typing import Any
from temporalio.common import RetryPolicy
from temporalio import workflow


@workflow.defn
class PipelineWorkflow:
    @workflow.run
    async def run(self, job_config: dict[str, Any]) -> dict[str, Any]:
        raw_data = await workflow.execute_activity(
            "run_ingestor",
            job_config,
            start_to_close_timeout=timedelta(seconds=120),
            retry_policy=RetryPolicy(maximum_attempts=job_config["pipeline_settings"]["max_retries"] + 1),
        )

        analyses = await workflow.execute_activity(
            "run_analyzer",
            {"job_config": job_config, "data": raw_data},
            start_to_close_timeout=timedelta(seconds=120),
        )

        return {"job_id": job_config["job_id"], "raw_count": len(raw_data), "analysis": analyses}

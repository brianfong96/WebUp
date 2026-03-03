from __future__ import annotations

from datetime import datetime, timezone

from ..base import BaseIngestor


class MedicalIngestor(BaseIngestor):
    domain = "medical"

    async def fetch(self, job_config: dict) -> list[dict]:
        return [
            {
                "trial_id": "NCT00000000",
                "status": "active",
                "captured_at": datetime.now(timezone.utc).isoformat(),
            }
        ]

    def normalize(self, raw: list[dict]) -> list[dict]:
        return [
            {
                "record_id": f"medical-{idx}",
                "domain": self.domain,
                "payload": row,
                "source": "medical-plugin",
            }
            for idx, row in enumerate(raw)
        ]

from __future__ import annotations

from datetime import datetime, timezone

from ..base import BaseIngestor


class FinanceIngestor(BaseIngestor):
    domain = "finance"

    async def fetch(self, job_config: dict) -> list[dict]:
        # Playwright-ready stub. Replace with real navigation and extraction.
        return [
            {
                "symbol": "WEBUP",
                "price": 123.45,
                "captured_at": datetime.now(timezone.utc).isoformat(),
            }
        ]

    def normalize(self, raw: list[dict]) -> list[dict]:
        return [
            {
                "record_id": f"finance-{idx}",
                "domain": self.domain,
                "payload": row,
                "source": "finance-plugin",
            }
            for idx, row in enumerate(raw)
        ]

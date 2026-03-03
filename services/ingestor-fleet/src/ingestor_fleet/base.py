from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseIngestor(ABC):
    domain: str

    @abstractmethod
    async def fetch(self, job_config: dict[str, Any]) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def normalize(self, raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
        raise NotImplementedError

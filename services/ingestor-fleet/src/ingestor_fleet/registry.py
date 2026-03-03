from __future__ import annotations

from .base import BaseIngestor
from .plugins.finance import FinanceIngestor
from .plugins.medical import MedicalIngestor


INGESTOR_REGISTRY: dict[str, type[BaseIngestor]] = {
    "finance": FinanceIngestor,
    "medical": MedicalIngestor,
}

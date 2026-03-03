from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "services/ingestor-fleet/src"))

from ingestor_fleet.registry import INGESTOR_REGISTRY


def test_ingestor_plugins_registered() -> None:
    assert "finance" in INGESTOR_REGISTRY
    assert "medical" in INGESTOR_REGISTRY


def test_plugin_normalization_shape() -> None:
    finance = INGESTOR_REGISTRY["finance"]()
    normalized = finance.normalize([{"symbol": "WEBUP", "price": 1.0}])
    assert normalized
    row = normalized[0]
    assert set(row.keys()) == {"record_id", "domain", "payload", "source"}

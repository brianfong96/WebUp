from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "services/workflow-engine/src"))

from workflow_engine.log_cleanup import cutoff_for_days, parse_iso8601


def test_parse_iso8601_handles_zulu() -> None:
    dt = parse_iso8601("2026-03-03T10:00:00Z")
    assert dt is not None
    assert dt.tzinfo is not None


def test_cutoff_for_days_in_past() -> None:
    cutoff = cutoff_for_days(7)
    now = datetime.now(timezone.utc)
    assert now - cutoff >= timedelta(days=6, hours=23)

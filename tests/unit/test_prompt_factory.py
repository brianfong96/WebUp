from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "services/ai-analyzer/src"))

from ai_analyzer.prompt_factory import build_prompt


def test_prompt_factory_includes_payload() -> None:
    prompt = build_prompt("finance-v1", '{"x":1}')
    assert "financial analysis assistant" in prompt.lower()
    assert '"x":1' in prompt


def test_prompt_factory_fallback_template() -> None:
    prompt = build_prompt("unknown-template", "{}")
    assert "analyze the json input" in prompt.lower()

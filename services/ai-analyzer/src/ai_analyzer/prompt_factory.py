from __future__ import annotations

PROMPT_TEMPLATES = {
    "finance-v1": "You are a financial analysis assistant. Summarize trends and anomalies from the input JSON.",
    "medical-v1": "You are a clinical research assistant. Summarize key updates, statuses, and safety implications.",
    "default-v1": "Analyze the JSON input and produce a concise risk-prioritized summary.",
}


def build_prompt(template_id: str, payload_json: str) -> str:
    system = PROMPT_TEMPLATES.get(template_id, PROMPT_TEMPLATES["default-v1"])
    return f"{system}\n\nInput:\n{payload_json}\n\nOutput format: bullet points with confidence scores."

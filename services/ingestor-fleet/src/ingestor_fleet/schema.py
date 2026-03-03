UNIFORM_RECORD_SCHEMA = {
    "type": "object",
    "required": ["record_id", "domain", "payload", "source"],
    "properties": {
        "record_id": {"type": "string"},
        "domain": {"type": "string"},
        "payload": {"type": "object"},
        "source": {"type": "string"},
    },
}

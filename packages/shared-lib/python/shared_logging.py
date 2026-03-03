from __future__ import annotations

import sys
import structlog


def create_logger(service_name: str):
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso", key="timestamp"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
    )
    return structlog.get_logger().bind(service_name=service_name)

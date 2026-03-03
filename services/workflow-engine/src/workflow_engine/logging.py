from __future__ import annotations

import sys
import logging

try:
    import structlog
except ModuleNotFoundError:  # pragma: no cover
    structlog = None


def configure_logger(service_name: str):
    if structlog is None:
        logger = logging.getLogger(service_name)
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S%z",
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso", key="timestamp"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )
    return structlog.get_logger().bind(service_name=service_name)

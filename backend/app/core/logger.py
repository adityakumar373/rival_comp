# app/core/logger.py
"""
Structured logging for the application.

Usage:
    from app.core.logger import get_logger
    logger = get_logger(__name__)
    logger.info("competitor_created", extra={"competitor_id": str(comp.id)})
"""

import json
import logging
import sys
from datetime import datetime, timezone

from app.core.config import settings


class JsonFormatter(logging.Formatter):
    """Formats log records as single-line JSON for easy ingestion by
    log aggregators (CloudWatch, Loki, etc.) in production."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include any extra fields passed via `extra={...}`
        reserved = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__.keys())
        for key, value in record.__dict__.items():
            if key not in reserved and key not in payload:
                payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


def _configure_root_logger() -> None:
    root = logging.getLogger()
    if root.handlers:
        # Already configured (e.g. re-imported under uvicorn --reload)
        return

    root.setLevel(settings.LOG_LEVEL)

    handler = logging.StreamHandler(sys.stdout)
    if settings.LOG_JSON:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
            )
        )

    root.addHandler(handler)


_configure_root_logger()


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

import sys
import pytz
import json
import logging
from typing import Any, Dict
from datetime import datetime

from app.core.config import env
from app.common.constants import Constants

class JSONFormatter(logging.Formatter):
    """Format log records as structured JSON for production use."""

    def format(self, record: logging.LogRecord) -> str:
        print(env.time_zone)
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.now(pytz.timezone(Constants.TIME_ZONE)).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "pathname": record.pathname,
            "lineno": record.lineno,
        }

        if hasattr(record, "extra"):
            log_obj.update(record.extra)

        return json.dumps(log_obj)


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger instance."""

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    environment = env.app_env

    handler = logging.StreamHandler(sys.stdout)

    if environment == "production":
        formatter = JSONFormatter()
        logger.setLevel(logging.INFO)
    else:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s | %(pathname)s | %(lineno)s ",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        logger.setLevel(logging.DEBUG)

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.propagate = False
    return logger


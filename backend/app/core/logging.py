import sys
import pytz
import json
import logging
import logstash
from typing import Any, Dict
from datetime import datetime

from app.core.config import env
from app.common.constants import Constants


class JSONFormatter(logging.Formatter):
    """Format log records as structured JSON for ELK."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.now(pytz.timezone(Constants.TIME_ZONE)).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "pathname": record.pathname,
            "lineno": record.lineno,
        }

        # Include any custom fields passed via 'extra'
        for key, value in record.__dict__.items():
            if key not in (
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                'thread', 'threadName', 'processName', 'process', 'message'
            ):
                log_obj[key] = value

        return json.dumps(log_obj)


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger instance."""

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger 

    environment = env.app_env
    enable_elk = getattr(env, "enable_elk_logging", False)

    # Console handler
    stream_handler = logging.StreamHandler(sys.stdout)
    if environment == "production":
        formatter = JSONFormatter()
        logger.setLevel(logging.INFO)
    else:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s | %(pathname)s | %(lineno)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        logger.setLevel(logging.DEBUG)

    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if enable_elk:
        try:
            logstash_handler = logstash.TCPLogstashHandler(
                host=env.logstash_host,
                port=int(env.logstash_port),
                version=1,
                message_type='fastapi_log',
                fqdn=False,
                tags=['fastapi', Constants.APP_NAME]
            )
            logger.addHandler(logstash_handler)
            logger.info("✅ Logstash handler connected")
        except Exception as e:
            logger.warning(f"⚠️ Failed to connect to Logstash: {e}")

    logger.propagate = False
    return logger


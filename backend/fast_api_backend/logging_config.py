# logging_config.py
import logging
import json
from logging.handlers import RotatingFileHandler

class RemoveExtraFieldsFilter(logging.Filter):
    def filter(self, record):
        # Define allowed log record attributes
        allowed_attrs = {
            "name", "msg", "args", "levelname", "levelno", "pathname",
            "filename", "module", "exc_info", "exc_text", "stack_info",
            "lineno", "funcName", "created", "msecs", "relativeCreated",
            "thread", "threadName", "processName", "process", "message",
            "asctime"
        }
        # Remove any attribute from the log record that isn't allowed
        for attr in list(vars(record)):
            if attr not in allowed_attrs:
                delattr(record, attr)
        return True

class CustomJSONFormatter(logging.Formatter):
    def format(self, record):
        record_message = super().format(record)
        return json.dumps({
            "time": record.asctime,
            "level": record.levelname,
            "logger_name": record.name,
            "message": record.getMessage(),
            "process_id": record.process,
            "thread_id": record.thread,
            "pathname": record.pathname,
            "line": record.lineno
        })

# Define the logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "remove_extra_fields": {
            "()": RemoveExtraFieldsFilter,
        }
    },
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "json": {
            "()": CustomJSONFormatter,
            "format": "%(asctime)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "filters": ["remove_extra_fields"],
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "json",
            "filename": "logs/app.log",
            "maxBytes": 1024 * 1024,  # 1 MB per file
            "backupCount": 3,
            "encoding": "utf8",
            "filters": ["remove_extra_fields"],
        }
    },
    "loggers": {
        "": {  # Root logger
            "handlers": ["console", "file"],
            "level": "INFO",
        },
        "uvicorn": {  # Uvicorn logger
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {  # Uvicorn error logger
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
            "name": "uvicorn_app_info",

        },
        "uvicorn.access": {  # Uvicorn access logger
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
            "name": "application_access",
        },
    }
}
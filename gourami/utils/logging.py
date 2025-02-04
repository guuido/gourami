import datetime
import json
import logging
import sys
from uvicorn.logging import DefaultFormatter
from logging.handlers import RotatingFileHandler
from pathlib import Path
from gourami.core.config import get_settings

class CustomFormatter(logging.Formatter):
    """
    Custom formatter that includes timestamp and log level.
    """
    def format(self, record):
        timestamp = datetime.utcnow().isoformat()
        log_data = {
            "timestamp": timestamp,
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)

def setup_logging():
    """
    Set up logging configuration.
    """
    settings = get_settings()  

    # Create logger
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)

    # Prevent duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    # Console handler with color formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(DefaultFormatter(
        fmt="%(levelprefix)s %(message)s",
        use_colors=True
    ))
    logger.addHandler(console_handler)

    # Skip file handlers if DISABLE_LOGGING is set to True
    if not settings.DISABLE_LOGGING:
        
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

        # File handlers for info and error logs
        info_handler = RotatingFileHandler(
            "logs/info.log",
            maxBytes=10485760,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(CustomFormatter())
        logger.addHandler(info_handler)

        error_handler = RotatingFileHandler(
            "logs/error.log",
            maxBytes=10485760,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(CustomFormatter())
        logger.addHandler(error_handler)
    else:
        logger.info("Logging is disabled. Log files won't be generated.")

    # Force lib logs to use application logger
    class StreamToLogger:
        def __init__(self, logger, level=logging.INFO):
            self.logger = logger
            self.level = level

        def write(self, message):
            if message.strip():  # Avoid logging empty messages
                self.logger.log(self.level, message.strip())

        def flush(self):
            pass

    sys.stdout = StreamToLogger(logger, logging.INFO)
    sys.stderr = StreamToLogger(logger, logging.ERROR)

    return logger


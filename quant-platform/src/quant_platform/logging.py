"""Logging framework for the quant-platform."""

import datetime
import logging
import pathlib
from logging.handlers import RotatingFileHandler
from typing import override

from quant_platform.config import RootConfig


class ISO8601Formatter(logging.Formatter):
    """Custom formatter to output ISO-8601 formatted timestamps."""

    @override
    def formatTime(
        self, record: logging.LogRecord, _datefmt: str | None = None
    ) -> str:
        """Format the time using ISO-8601 formatting."""
        dt = datetime.datetime.fromtimestamp(record.created, datetime.UTC)
        return dt.isoformat()


def create_logger(config: RootConfig) -> logging.Logger:
    """Create and configure the central logger.

    Args:
        config: The validated root configuration object.

    Returns:
        logging.Logger: The configured application logger.

    Raises:
        ValueError: If configuration validation or parameters are invalid.
        OSError: If log directory or log file creation fails.
    """
    if config is None:
        raise ValueError("Configuration object cannot be None.")

    if not hasattr(config, "logging") or config.logging is None:
        raise ValueError("Configuration is missing the logging section.")

    level_str = config.logging.level
    valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    if level_str not in valid_levels:
        msg = f"Invalid log level: {level_str}. Must be one of {valid_levels}"
        raise ValueError(msg)

    # Set up logger name using the application name
    logger_name = config.application.name
    logger = logging.getLogger(logger_name)

    # Set the level on the logger itself
    log_level = getattr(logging, level_str)
    logger.setLevel(log_level)

    # Prevent duplicate log entries and disable unnecessary propagation
    logger.propagate = False

    # Clear existing handlers to prevent duplicate handler issues
    # (e.g. during re-creation)
    for handler in list(logger.handlers):
        logger.removeHandler(handler)

    # Create the single formatter
    # Include: Timestamp, Level, Logger Name, Module, Function, Line Number, Message
    format_str = (
        "%(asctime)s - %(levelname)s - %(name)s - "
        "%(module)s - %(funcName)s - %(lineno)d - %(message)s"
    )
    formatter = ISO8601Formatter(format_str)

    # 1. Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. File Handler
    # Auto-create directory if required
    log_dir_str = config.logging.log_dir
    log_file_str = config.logging.log_file

    if not log_dir_str.strip():
        raise ValueError("Log directory path cannot be empty.")
    if not log_file_str.strip():
        raise ValueError("Log file name cannot be empty.")

    log_dir = pathlib.Path(log_dir_str)
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise OSError(f"Failed to create log directory '{log_dir_str}': {e}") from e

    log_file_path = log_dir / log_file_str
    if log_file_path.exists() and log_file_path.is_dir():
        raise ValueError(f"Log path '{log_file_path}' is a directory, not a file.")

    try:
        # Maximum size: 10 MB (10 * 1024 * 1024 bytes)
        # Keep 10 backups
        # UTF-8 encoding
        file_handler = RotatingFileHandler(
            filename=log_file_path,
            maxBytes=10 * 1024 * 1024,
            backupCount=10,
            encoding="utf-8",
        )
    except Exception as e:
        raise OSError(f"Failed to open log file '{log_file_path}': {e}") from e

    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

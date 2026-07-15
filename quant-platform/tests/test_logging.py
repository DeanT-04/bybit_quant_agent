"""Unit tests for the central logging framework."""

import logging
import pathlib
from typing import Any
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

import quant_platform.logging
from quant_platform.config import (
    ApplicationConfig,
    ExchangeConfig,
    LoggingConfig,
    MarketConfig,
    RootConfig,
    StorageConfig,
)
from quant_platform.logging import ISO8601Formatter, create_logger

EXPECTED_HANDLERS_COUNT = 2


@pytest.fixture
def base_config(tmp_path: pathlib.Path) -> RootConfig:
    """Fixture providing a base RootConfig with tmp_path for storage and logs."""
    return RootConfig(
        application=ApplicationConfig(
            name="TestApp",
            version="1.0.0",
            environment="test",
        ),
        exchange=ExchangeConfig(
            provider="bybit",
        ),
        market=MarketConfig(
            type="usdt_perpetual",
        ),
        storage=StorageConfig(
            data_directory=str(tmp_path / "data"),
        ),
        logging=LoggingConfig(
            level="DEBUG",
            log_dir=str(tmp_path / "logs"),
            log_file="app.log",
        ),
    )


def test_logger_creation_success(base_config: RootConfig) -> None:
    """Verify that a logger is successfully created with correct attributes."""
    logger = create_logger(base_config)
    assert isinstance(logger, logging.Logger)
    assert logger.name == "TestApp"
    assert logger.level == logging.DEBUG
    assert not logger.propagate


def test_console_and_file_handlers_exist(base_config: RootConfig) -> None:
    """Verify both console and file handlers are attached with the single formatter."""
    logger = create_logger(base_config)
    handlers = logger.handlers
    assert len(handlers) == EXPECTED_HANDLERS_COUNT

    # Check for console handler (StreamHandler)
    console_handlers = [
        h
        for h in handlers
        if isinstance(h, logging.StreamHandler)
        and not isinstance(h, logging.FileHandler)
    ]
    assert len(console_handlers) == 1
    assert console_handlers[0].level == logging.DEBUG

    # Check for file handler (RotatingFileHandler)
    file_handlers = [h for h in handlers if isinstance(h, logging.FileHandler)]
    assert len(file_handlers) == 1
    assert file_handlers[0].level == logging.DEBUG

    # Verify both handlers use the same formatter type and format
    assert console_handlers[0].formatter is not None
    assert file_handlers[0].formatter is not None
    assert isinstance(console_handlers[0].formatter, ISO8601Formatter)
    assert isinstance(file_handlers[0].formatter, ISO8601Formatter)


def test_correct_log_level(base_config: RootConfig) -> None:
    """Verify the logger adapts to different log levels from config."""
    # Test INFO level
    info_config = base_config.model_copy(
        update={
            "logging": LoggingConfig(
                level="INFO",
                log_dir=base_config.logging.log_dir,
                log_file=base_config.logging.log_file,
            )
        }
    )
    logger = create_logger(info_config)
    assert logger.level == logging.INFO
    for handler in logger.handlers:
        assert handler.level == logging.INFO


def test_invalid_log_level_rejected() -> None:
    """Verify invalid log levels are rejected during config validation or creation."""
    # 1. Pydantic validation rejection
    with pytest.raises(ValidationError):
        LoggingConfig(level="INVALID_LEVEL")  # type: ignore[arg-type]

    # 2. Rejection inside create_logger if validation is bypassed/mocked
    mock_config = MagicMock()
    mock_logging = MagicMock()
    mock_logging.level = "INVALID_LEVEL"
    mock_config.logging = mock_logging
    mock_config.application.name = "TestAppBypass"

    with pytest.raises(ValueError, match="Invalid log level"):
        create_logger(mock_config)


def test_automatic_log_directory_creation(
    tmp_path: pathlib.Path, base_config: RootConfig
) -> None:
    """Verify that the log directory is created automatically if it doesn't exist."""
    nested_log_dir = tmp_path / "new_logs" / "nested"
    assert not nested_log_dir.exists()

    config = base_config.model_copy(
        update={
            "logging": LoggingConfig(
                level="DEBUG",
                log_dir=str(nested_log_dir),
                log_file="app.log",
            )
        }
    )
    create_logger(config)
    assert nested_log_dir.exists()
    assert nested_log_dir.is_dir()


def test_log_file_creation_and_message_written(base_config: RootConfig) -> None:
    """Verify that the log file is created and messages are written."""
    logger = create_logger(base_config)
    test_message = "This is a diagnostic log entry."
    logger.info(test_message)

    # Force close file handlers to ensure writes are flushed
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            handler.close()

    log_file = pathlib.Path(base_config.logging.log_dir) / base_config.logging.log_file
    assert log_file.exists()

    log_content = log_file.read_text(encoding="utf-8")
    assert test_message in log_content
    assert "INFO" in log_content
    assert "TestApp" in log_content
    # ISO-8601 UTC timestamp check (ends with Z or offset representation or contains T)
    assert "T" in log_content


def test_duplicate_handler_prevention(base_config: RootConfig) -> None:
    """Verify that multiple calls to create_logger do not accumulate handlers."""
    logger1 = create_logger(base_config)
    assert len(logger1.handlers) == EXPECTED_HANDLERS_COUNT

    logger2 = create_logger(base_config)
    assert len(logger2.handlers) == EXPECTED_HANDLERS_COUNT
    assert logger1 is logger2


def test_create_logger_failures(
    base_config: RootConfig, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test various failure conditions during logger creation."""
    # 1. Configuration object is None
    with pytest.raises(ValueError, match=r"Configuration object cannot be None\."):
        create_logger(None)  # type: ignore[arg-type]

    # 2. Configuration is missing the logging section
    mock_config_no_logging = MagicMock()
    mock_config_no_logging.logging = None
    mock_config_no_logging.application.name = "TestAppNoLogging"
    with pytest.raises(
        ValueError, match=r"Configuration is missing the logging section\."
    ):
        create_logger(mock_config_no_logging)

    # 3. Log path exists but is a directory
    log_dir_path = pathlib.Path(base_config.logging.log_dir)
    log_dir_path.mkdir(parents=True, exist_ok=True)
    invalid_file_path = log_dir_path / "app.log"
    invalid_file_path.mkdir(exist_ok=True)  # Make it a directory!

    with pytest.raises(ValueError, match="is a directory, not a file"):
        create_logger(base_config)

    # Cleanup the directory so we don't affect other tests
    invalid_file_path.rmdir()

    # 4. Failures during log directory creation (e.g., OSError)
    def mock_mkdir(*_args: Any, **_kwargs: Any) -> None:
        raise OSError("Permission denied")

    # Use monkeypatch to patch pathlib.Path.mkdir
    monkeypatch.setattr(pathlib.Path, "mkdir", mock_mkdir)

    with pytest.raises(OSError, match="Failed to create log directory"):
        create_logger(base_config)

    monkeypatch.undo()

    # 5. Failures during RotatingFileHandler initialization
    def mock_rotating_file_handler_init(*_args: Any, **_kwargs: Any) -> None:
        raise PermissionError("Write access denied")

    monkeypatch.setattr(
        quant_platform.logging,
        "RotatingFileHandler",
        mock_rotating_file_handler_init,
    )
    with pytest.raises(OSError, match="Failed to open log file"):
        create_logger(base_config)


def test_validation_empty_whitespace_logging_paths() -> None:
    """Test validation fails when log directory or file is empty or just whitespace."""
    with pytest.raises(ValidationError) as excinfo:
        LoggingConfig(level="INFO", log_dir="", log_file="app.log")
    assert "Log directory path cannot be empty" in str(excinfo.value)

    with pytest.raises(ValidationError) as excinfo:
        LoggingConfig(level="INFO", log_dir="   ", log_file="app.log")
    assert "Log directory path cannot be empty" in str(excinfo.value)

    with pytest.raises(ValidationError) as excinfo:
        LoggingConfig(level="INFO", log_dir="logs", log_file="")
    assert "Log file name cannot be empty" in str(excinfo.value)

    with pytest.raises(ValidationError) as excinfo:
        LoggingConfig(level="INFO", log_dir="logs", log_file="  ")
    assert "Log file name cannot be empty" in str(excinfo.value)


def test_create_logger_with_empty_paths_validation_bypass() -> None:
    """Verify create_logger rejects empty logging paths if validation is bypassed."""
    mock_config = MagicMock()
    mock_logging = MagicMock()
    mock_logging.level = "INFO"
    mock_logging.log_dir = ""
    mock_logging.log_file = "app.log"
    mock_config.logging = mock_logging
    mock_config.application.name = "TestAppEmptyPaths"

    with pytest.raises(ValueError, match=r"Log directory path cannot be empty\."):
        create_logger(mock_config)

    mock_logging.log_dir = "logs"
    mock_logging.log_file = ""
    with pytest.raises(ValueError, match=r"Log file name cannot be empty\."):
        create_logger(mock_config)

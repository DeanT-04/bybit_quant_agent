import pathlib

import pytest
from pydantic import ValidationError

from quant_platform.config import (
    ApplicationConfig,
    ExchangeConfig,
    LoggingConfig,
    MarketConfig,
    StorageConfig,
    load_config,
)


def create_temp_files(
    tmp_path: pathlib.Path, yaml_content: str, env_content: str
) -> tuple[pathlib.Path, pathlib.Path]:
    """Helper to create temporary config.yaml and .env files."""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    env_file = tmp_path / ".env"
    env_file.write_text(env_content, encoding="utf-8")

    return yaml_file, env_file


def test_load_config_success(tmp_path: pathlib.Path) -> None:
    """Test successful configuration loading and env overrides."""
    data_dir = tmp_path / "data_dir"
    yaml_content = f"""
application:
  name: "Quant Platform"
  version: "0.1.0"
  environment: "development"
exchange:
  provider: "bybit"
market:
  type: "usdt_perpetual"
storage:
  data_directory: "{str(data_dir).replace('\\', '/')}"
logging:
  level: "INFO"
"""
    env_content = """
BYBIT_API_KEY=test_key
BYBIT_API_SECRET=test_secret
ENVIRONMENT=production
LOG_LEVEL=DEBUG
"""
    yaml_file, env_file = create_temp_files(tmp_path, yaml_content, env_content)

    config = load_config(config_path=str(yaml_file), env_path=str(env_file))

    # Verify overrides and values
    assert config.application.name == "Quant Platform"
    assert config.application.version == "0.1.0"
    assert config.application.environment == "production"  # Overridden by env
    assert config.exchange.provider == "bybit"
    assert config.exchange.api_key == "test_key"  # Overridden by env
    assert config.exchange.api_secret == "test_secret"  # Overridden by env
    assert config.market.type == "usdt_perpetual"
    assert config.logging.level == "DEBUG"  # Overridden by env
    assert config.storage.data_directory == str(data_dir).replace('\\', '/')
    assert data_dir.exists()
    assert data_dir.is_dir()


def test_load_config_optional_credentials_omitted(tmp_path: pathlib.Path) -> None:
    """Test that app loads successfully when both credentials are empty."""
    data_dir = tmp_path / "data_dir"
    yaml_content = f"""
application:
  name: "Quant Platform"
  version: "0.1.0"
  environment: "development"
exchange:
  provider: "bybit"
market:
  type: "usdt_perpetual"
storage:
  data_directory: "{str(data_dir).replace('\\', '/')}"
logging:
  level: "INFO"
"""
    env_content = """
BYBIT_API_KEY=
BYBIT_API_SECRET=
"""
    yaml_file, env_file = create_temp_files(tmp_path, yaml_content, env_content)

    config = load_config(config_path=str(yaml_file), env_path=str(env_file))
    assert config.exchange.api_key is None
    assert config.exchange.api_secret is None


def test_load_config_missing_env_file() -> None:
    """Test that loading fails with FileNotFoundError if .env file is missing."""
    msg = r"Environment file 'non_existent_env' is missing\."
    with pytest.raises(FileNotFoundError, match=msg):
        load_config(env_path="non_existent_env")


def test_load_config_missing_yaml_file(tmp_path: pathlib.Path) -> None:
    """Test that loading fails with FileNotFoundError if config.yaml is missing."""
    env_file = tmp_path / ".env"
    env_file.write_text("", encoding="utf-8")

    msg = r"Configuration file 'non_existent_yaml' is missing\."
    with pytest.raises(FileNotFoundError, match=msg):
        load_config(config_path="non_existent_yaml", env_path=str(env_file))


def test_load_config_malformed_yaml(tmp_path: pathlib.Path) -> None:
    """Test that malformed YAML content raises a ValueError."""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text("invalid_yaml: { [ }", encoding="utf-8")

    env_file = tmp_path / ".env"
    env_file.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid YAML content"):
        load_config(config_path=str(yaml_file), env_path=str(env_file))


def test_load_config_empty_yaml(tmp_path: pathlib.Path) -> None:
    """Test that an empty YAML content raises a ValueError."""
    yaml_file, env_file = create_temp_files(tmp_path, "", "")

    with pytest.raises(ValueError, match="empty or invalid"):
        load_config(config_path=str(yaml_file), env_path=str(env_file))


def test_validation_empty_application_name() -> None:
    """Test Pydantic validation rule: application name cannot be empty."""
    with pytest.raises(ValidationError) as excinfo:
        ApplicationConfig(name="", version="0.1.0", environment="development")
    assert "String should have at least 1 character" in str(excinfo.value)

    with pytest.raises(ValidationError) as excinfo:
        ApplicationConfig(name="   ", version="0.1.0", environment="development")
    assert "Application name cannot be empty or only whitespace" in str(excinfo.value)


def test_validation_invalid_exchange_provider() -> None:
    """Test Pydantic validation rule: exchange provider must be 'bybit'."""
    with pytest.raises(ValidationError) as excinfo:
        ExchangeConfig(provider="coinbase")  # type: ignore[arg-type]
    assert "Input should be 'bybit'" in str(excinfo.value)


def test_validation_invalid_market_type() -> None:
    """Test Pydantic validation rule: market type must be 'usdt_perpetual'."""
    with pytest.raises(ValidationError) as excinfo:
        MarketConfig(type="spot")  # type: ignore[arg-type]
    assert "Input should be 'usdt_perpetual'" in str(excinfo.value)


def test_validation_invalid_logging_level() -> None:
    """Test Pydantic validation rule: logging level validation."""
    with pytest.raises(ValidationError) as excinfo:
        LoggingConfig(level="TRACE")  # type: ignore[arg-type]
    assert "Input should be 'DEBUG', 'INFO'" in str(excinfo.value)


def test_validation_storage_directory_is_file(tmp_path: pathlib.Path) -> None:
    """Test that validation fails when storage directory is a file."""
    temp_file = tmp_path / "data_file"
    temp_file.write_text("dummy", encoding="utf-8")

    with pytest.raises(ValidationError) as excinfo:
        StorageConfig(data_directory=str(temp_file))
    assert "exists but is not a directory" in str(excinfo.value)


def test_validation_storage_directory_empty() -> None:
    """Test that validation fails when storage directory path is empty."""
    with pytest.raises(ValidationError) as excinfo:
        StorageConfig(data_directory="")
    assert "String should have at least 1 character" in str(excinfo.value)


def test_validation_storage_directory_whitespace() -> None:
    """Test that validation fails when storage directory path is only whitespace."""
    with pytest.raises(ValidationError) as excinfo:
        StorageConfig(data_directory="   ")
    assert "Storage directory path cannot be empty" in str(excinfo.value)


def test_validation_storage_directory_creation_failure() -> None:
    """Test that validation fails with ValueError when directory cannot be created."""
    invalid_path = r"C:\invalid_dir_*\?"
    with pytest.raises(ValidationError) as excinfo:
        StorageConfig(data_directory=invalid_path)
    assert "Failed to create storage directory" in str(excinfo.value)


def test_exchange_credentials_partial_missing() -> None:
    """Test that validation fails when only one of API key or secret is provided."""
    with pytest.raises(ValidationError) as excinfo:
        ExchangeConfig(provider="bybit", api_key="only_key")
    assert "Both api_key and api_secret must be provided together" in str(excinfo.value)

    with pytest.raises(ValidationError) as excinfo:
        ExchangeConfig(provider="bybit", api_secret="only_secret")
    assert "Both api_key and api_secret must be provided together" in str(excinfo.value)


def test_load_config_validation_wrapping(tmp_path: pathlib.Path) -> None:
    """Test Pydantic validation errors wrapper inside load_config."""
    yaml_content = """
application:
  name: "Quant Platform"
  version: "0.1.0"
  environment: "development"
exchange:
  provider: "invalid_exchange"
market:
  type: "usdt_perpetual"
storage:
  data_directory: "data/"
logging:
  level: "INFO"
"""
    yaml_file, env_file = create_temp_files(tmp_path, yaml_content, "")

    with pytest.raises(ValueError, match="Configuration validation failed"):
        load_config(config_path=str(yaml_file), env_path=str(env_file))


def test_load_config_failed_to_read_file(tmp_path: pathlib.Path) -> None:
    """Test loading directory as config_path raises ValueError (failed to read)."""
    env_file = tmp_path / ".env"
    env_file.write_text("", encoding="utf-8")

    # Pass the temp directory itself as the config path
    with pytest.raises(ValueError, match="Failed to read configuration file"):
        load_config(config_path=str(tmp_path), env_path=str(env_file))


def test_load_config_missing_sections_in_yaml(tmp_path: pathlib.Path) -> None:
    """Test missing YAML sections raise validation errors even with env overrides."""
    yaml_content = """
market:
  type: "usdt_perpetual"
storage:
  data_directory: "data/"
"""
    env_content = """
ENVIRONMENT=production
LOG_LEVEL=DEBUG
BYBIT_API_KEY=test_key
BYBIT_API_SECRET=test_secret
"""
    yaml_file, env_file = create_temp_files(tmp_path, yaml_content, env_content)

    with pytest.raises(ValueError, match="Configuration validation failed"):
        load_config(config_path=str(yaml_file), env_path=str(env_file))


def test_load_config_logging_env_overrides(tmp_path: pathlib.Path) -> None:
    """Test that logging path configuration can be overridden by env variables."""
    data_dir = tmp_path / "data_dir"
    yaml_content = f"""
application:
  name: "Quant Platform"
  version: "0.1.0"
  environment: "development"
exchange:
  provider: "bybit"
market:
  type: "usdt_perpetual"
storage:
  data_directory: "{str(data_dir).replace('\\', '/')}"
logging:
  level: "INFO"
"""
    env_content = """
LOG_DIR=custom_logs_dir
LOG_FILE=custom_app.log
"""
    yaml_file, env_file = create_temp_files(tmp_path, yaml_content, env_content)

    config = load_config(config_path=str(yaml_file), env_path=str(env_file))
    assert config.logging.log_dir == "custom_logs_dir"
    assert config.logging.log_file == "custom_app.log"

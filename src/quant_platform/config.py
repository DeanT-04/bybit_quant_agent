"""Configuration management system for the quant-platform."""

import os
import pathlib
from typing import Any, Literal

import yaml
from dotenv import load_dotenv
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)


class ApplicationConfig(BaseModel):
    """Configuration options for the application metadata."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(..., min_length=1)
    version: str = Field(..., min_length=1)
    environment: str = Field(..., min_length=1)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Verify the application name is not empty or just whitespace."""
        if not v.strip():
            raise ValueError("Application name cannot be empty or only whitespace.")
        return v


class ExchangeConfig(BaseModel):
    """Configuration options for the exchange connection."""

    model_config = ConfigDict(frozen=True)

    provider: Literal["bybit"]
    api_key: str | None = None
    api_secret: str | None = None

    @model_validator(mode="after")
    def validate_credentials(self) -> "ExchangeConfig":
        """Ensure both API key and secret are provided together, or both are omitted."""
        if (self.api_key is None) != (self.api_secret is None):
            err_msg = (
                "Both api_key and api_secret must be provided together, "
                "or both must be omitted."
            )
            raise ValueError(err_msg)
        return self


class MarketConfig(BaseModel):
    """Configuration options for the target market."""

    model_config = ConfigDict(frozen=True)

    type: Literal["usdt_perpetual"]


class StorageConfig(BaseModel):
    """Configuration options for directory storage paths."""

    model_config = ConfigDict(frozen=True)

    data_directory: str = Field(..., min_length=1)

    @field_validator("data_directory")
    @classmethod
    def validate_and_create_dir(cls, v: str) -> str:
        """Verify the path is not a file and automatically create it if missing."""
        if not v.strip():
            raise ValueError("Storage directory path cannot be empty.")
        path = pathlib.Path(v)
        if path.exists() and not path.is_dir():
            raise ValueError(f"Storage path '{v}' exists but is not a directory.")
        try:
            path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ValueError(f"Failed to create storage directory '{v}': {e}") from e
        return v


class LoggingConfig(BaseModel):
    """Configuration options for logging output."""

    model_config = ConfigDict(frozen=True)

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    log_dir: str = Field(default="logs")
    log_file: str = Field(default="application.log")

    @field_validator("log_dir")
    @classmethod
    def validate_log_dir(cls, v: str) -> str:
        """Verify the log directory path is not empty or just whitespace."""
        if not v.strip():
            raise ValueError("Log directory path cannot be empty or only whitespace.")
        return v

    @field_validator("log_file")
    @classmethod
    def validate_log_file(cls, v: str) -> str:
        """Verify the log file name is not empty or just whitespace."""
        if not v.strip():
            raise ValueError("Log file name cannot be empty or only whitespace.")
        return v


class RootConfig(BaseModel):
    """The root configuration object containing all sub-configurations."""

    model_config = ConfigDict(frozen=True)

    application: ApplicationConfig
    exchange: ExchangeConfig
    market: MarketConfig
    storage: StorageConfig
    logging: LoggingConfig


def _apply_env_overrides(config_dict: dict[str, Any]) -> None:
    """Helper to read OS environment variables and apply configuration overrides."""
    env_environment = os.getenv("ENVIRONMENT")
    if env_environment is not None:
        config_dict.setdefault("application", {})["environment"] = env_environment

    env_log_level = os.getenv("LOG_LEVEL")
    if env_log_level is not None:
        config_dict.setdefault("logging", {})["level"] = env_log_level

    env_log_dir = os.getenv("LOG_DIR")
    if env_log_dir is not None:
        config_dict.setdefault("logging", {})["log_dir"] = env_log_dir

    env_log_file = os.getenv("LOG_FILE")
    if env_log_file is not None:
        config_dict.setdefault("logging", {})["log_file"] = env_log_file

    env_api_key = os.getenv("BYBIT_API_KEY")
    env_api_secret = os.getenv("BYBIT_API_SECRET")

    # Handle empty strings from .env (e.g. BYBIT_API_KEY=) as None
    if env_api_key is not None:
        val = env_api_key if env_api_key.strip() != "" else None
        config_dict.setdefault("exchange", {})["api_key"] = val
    if env_api_secret is not None:
        val = env_api_secret if env_api_secret.strip() != "" else None
        config_dict.setdefault("exchange", {})["api_secret"] = val


def load_config(
    config_path: str | None = None,
    env_path: str | None = None,
) -> RootConfig:
    """Load, merge, and validate configuration from YAML and environment variables.

    Args:
        config_path: Path to the config.yaml file (defaults to config/config.yaml).
        env_path: Path to the .env file (defaults to .env).

    Returns:
        RootConfig: The immutable, validated configuration object.

    Raises:
        FileNotFoundError: If the config file or .env file is missing.
        ValueError: If loading, parsing, or validation fails.
    """
    # 1. Load and check environment file
    if env_path is None:
        env_path = ".env"

    env_file = pathlib.Path(env_path)
    if not env_file.exists():
        raise FileNotFoundError(f"Environment file '{env_path}' is missing.")

    # Load env variables with override=True to prioritize .env
    # over the local shell environment
    load_dotenv(dotenv_path=env_file, override=True)

    # 2. Check and load YAML config file
    if config_path is None:
        config_path = "config/config.yaml"

    yaml_file = pathlib.Path(config_path)
    if not yaml_file.exists():
        raise FileNotFoundError(f"Configuration file '{config_path}' is missing.")

    try:
        with yaml_file.open(encoding="utf-8") as f:
            config_dict = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML content in '{config_path}': {e}") from e
    except Exception as e:
        err_msg = f"Failed to read configuration file '{config_path}': {e}"
        raise ValueError(err_msg) from e

    if config_dict is None or not isinstance(config_dict, dict):
        raise ValueError(f"Configuration file '{config_path}' is empty or invalid.")

    # 3. Apply overrides from environment variables
    _apply_env_overrides(config_dict)

    # 4. Parse and validate config dictionary into RootConfig
    try:
        return RootConfig.model_validate(config_dict)
    except ValidationError as e:
        raise ValueError(f"Configuration validation failed: {e}") from e

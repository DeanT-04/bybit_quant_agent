"""Centralized application exception framework for the Quant Platform.

This package exposes the complete hierarchy of domain and infrastructure
exceptions. All exceptions inherit from QuantPlatformError.
"""

from quant_platform.exceptions.exceptions import (
    AuthenticationError,
    BacktestError,
    ConfigurationError,
    ConnectionError,  # noqa: A004
    ExchangeError,
    ExecutionError,
    InvalidResponseError,
    LoggingError,
    MarketDataError,
    QuantPlatformError,
    RateLimitError,
    ResearchError,
    RiskError,
    StorageError,
    TimeoutError,  # noqa: A004
    ValidationError,
)

__all__ = [
    "AuthenticationError",
    "BacktestError",
    "ConfigurationError",
    "ConnectionError",
    "ExchangeError",
    "ExecutionError",
    "InvalidResponseError",
    "LoggingError",
    "MarketDataError",
    "QuantPlatformError",
    "RateLimitError",
    "ResearchError",
    "RiskError",
    "StorageError",
    "TimeoutError",
    "ValidationError",
]

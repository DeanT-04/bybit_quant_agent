"""Centralized application exception definitions for the Quant Platform.

All exceptions in this module inherit from QuantPlatformError.
They support custom messages, exception chaining, and do not perform
any side effects (e.g. logging or I/O).
"""


class QuantPlatformError(Exception):
    """Base exception for the Quant Platform.

    All custom exceptions in the platform must inherit from this class.
    """

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or "An internal error occurred in the Quant Platform.")


class ConfigurationError(QuantPlatformError):
    """Exception raised when configuration is invalid or missing."""

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or "Configuration error occurred.")


class LoggingError(QuantPlatformError):
    """Exception raised when logging configuration or file setup fails."""

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or "Logging error occurred.")


class ValidationError(QuantPlatformError):
    """Exception raised when domain validation rules are violated."""

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or "Validation error occurred.")


class ExchangeError(QuantPlatformError):
    """Exception raised for general exchange communication or logic errors."""

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or "Exchange error occurred.")


class AuthenticationError(ExchangeError):
    """Exception raised when API authentication fails."""

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or "Authentication failed with the exchange.")


class ConnectionError(ExchangeError):  # noqa: A001
    """Exception raised when connection to the exchange fails."""

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or "Failed to connect to the exchange.")


class TimeoutError(ExchangeError):  # noqa: A001
    """Exception raised when an exchange operation times out."""

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or "Exchange operation timed out.")


class RateLimitError(ExchangeError):
    """Exception raised when exchange rate limits are exceeded."""

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or "Exchange rate limit exceeded.")


class InvalidResponseError(ExchangeError):
    """Exception raised when exchange returns a malformed or unexpected response."""

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or "Invalid response received from the exchange.")


class StorageError(QuantPlatformError):
    """Exception raised when storage read/write operations fail."""

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or "Storage error occurred.")


class MarketDataError(QuantPlatformError):
    """Exception raised when downloading or processing market data fails."""

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or "Market data error occurred.")


class ResearchError(QuantPlatformError):
    """Exception raised during research or strategy exploration."""

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or "Research error occurred.")


class BacktestError(QuantPlatformError):
    """Exception raised when backtest simulation encounters an error."""

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or "Backtest error occurred.")


class ExecutionError(QuantPlatformError):
    """Exception raised when live order routing or trade execution fails."""

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or "Execution error occurred.")


class RiskError(QuantPlatformError):
    """Exception raised when capital constraints or risk limit checks fail."""

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or "Risk threshold exceeded or risk check failed.")

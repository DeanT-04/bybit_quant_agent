"""Unit tests for the centralized exception framework.

Verifies imports, inheritance hierarchy, custom and default messages,
and exception chaining behavior.
"""

from quant_platform import exceptions
from quant_platform.exceptions import (
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

# List of all exceptions in the module
ALL_EXCEPTIONS = [
    QuantPlatformError,
    ConfigurationError,
    LoggingError,
    ValidationError,
    ExchangeError,
    AuthenticationError,
    ConnectionError,
    TimeoutError,
    RateLimitError,
    InvalidResponseError,
    StorageError,
    MarketDataError,
    ResearchError,
    BacktestError,
    ExecutionError,
    RiskError,
]

# Exceptions that inherit directly from ExchangeError
# (and transitively from QuantPlatformError)
EXCHANGE_SUBCLASSES = [
    AuthenticationError,
    ConnectionError,
    TimeoutError,
    RateLimitError,
    InvalidResponseError,
]


def test_imports() -> None:
    """Verify exceptions are exported and can be imported from the package."""
    for exc_class in ALL_EXCEPTIONS:
        assert hasattr(exceptions, exc_class.__name__)
        assert getattr(exceptions, exc_class.__name__) is exc_class


def test_inheritance() -> None:
    """Verify class hierarchy and inheritance chain of all custom exceptions."""
    # Every exception must inherit from QuantPlatformError
    for exc_class in ALL_EXCEPTIONS:
        assert issubclass(exc_class, QuantPlatformError)
        assert issubclass(exc_class, Exception)

    # Specific exchange exceptions must inherit from ExchangeError
    for exc_class in EXCHANGE_SUBCLASSES:
        assert issubclass(exc_class, ExchangeError)

    # ExchangeError itself is a base for them but not a subclass
    # of another specific error
    assert issubclass(ExchangeError, QuantPlatformError)


def test_default_messages() -> None:
    """Verify default messages when no custom message is supplied."""
    for exc_class in ALL_EXCEPTIONS:
        instance = exc_class()
        message = str(instance)
        assert len(message) > 0
        assert isinstance(message, str)


def test_custom_messages() -> None:
    """Verify that custom messages are preserved."""
    custom_msg = "A custom error message specifically for testing."
    for exc_class in ALL_EXCEPTIONS:
        instance = exc_class(custom_msg)
        assert str(instance) == custom_msg


def test_exception_chaining() -> None:
    """Verify that exception chaining (raise ... from ...) works correctly."""
    root_cause = ValueError("Original database connection failure")

    for exc_class in ALL_EXCEPTIONS:
        try:
            raise exc_class("Context wrapper message") from root_cause
        except exc_class as err:
            assert err.__cause__ is root_cause
            assert str(err) == "Context wrapper message"

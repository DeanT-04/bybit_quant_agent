"""Domain enums for the quant-platform."""

from enum import StrEnum


class Exchange(StrEnum):
    """Supported exchanges."""

    BYBIT = "BYBIT"


class MarketType(StrEnum):
    """Supported market types."""

    USDT_PERPETUAL = "USDT_PERPETUAL"


class Environment(StrEnum):
    """Application runtime environments."""

    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TEST = "test"


class LogLevel(StrEnum):
    """Logging severity levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class OrderSide(StrEnum):
    """Trading order sides."""

    BUY = "BUY"
    SELL = "SELL"


class PositionSide(StrEnum):
    """Trading position sides."""

    LONG = "LONG"
    SHORT = "SHORT"


class OrderType(StrEnum):
    """Trading order types."""

    MARKET = "MARKET"
    LIMIT = "LIMIT"


class TimeInForce(StrEnum):
    """Order time-in-force instructions."""

    GTC = "GTC"
    IOC = "IOC"
    FOK = "FOK"
    POST_ONLY = "POST_ONLY"


class PositionMode(StrEnum):
    """Position margin modes."""

    ONE_WAY = "ONE_WAY"
    HEDGE = "HEDGE"

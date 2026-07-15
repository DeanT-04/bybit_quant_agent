"""Domain constants for the quant-platform."""

from quant_platform.domain.enums import Exchange, MarketType

# Default values
DEFAULT_EXCHANGE: Exchange = Exchange.BYBIT
DEFAULT_MARKET: MarketType = MarketType.USDT_PERPETUAL

# Supported timeframes
SUPPORTED_TIMEFRAMES: frozenset[str] = frozenset(
    {
        "1m",
        "3m",
        "5m",
        "15m",
        "30m",
        "1h",
        "2h",
        "4h",
        "6h",
        "12h",
        "1d",
        "1w",
    }
)

# Symbol constraints
MIN_SYMBOL_LENGTH: int = 3
MAX_SYMBOL_LENGTH: int = 20

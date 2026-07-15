"""Unit tests for the domain model package."""

import pytest

from quant_platform.domain import (
    DEFAULT_EXCHANGE,
    DEFAULT_MARKET,
    MAX_SYMBOL_LENGTH,
    MIN_SYMBOL_LENGTH,
    SUPPORTED_TIMEFRAMES,
    Environment,
    Exchange,
    LogLevel,
    MarketType,
    OrderSide,
    OrderType,
    PositionMode,
    PositionSide,
    Symbol,
    Timeframe,
    TimeInForce,
)


def test_enums_values() -> None:
    """Verify enums are correctly defined and contain standard members."""
    # Exchange
    assert Exchange.BYBIT.value == "BYBIT"
    assert len(Exchange) == 1

    # MarketType
    assert MarketType.USDT_PERPETUAL.value == "USDT_PERPETUAL"
    assert len(MarketType) == 1

    # Environment
    assert Environment.DEVELOPMENT.value == "development"
    assert Environment.PRODUCTION.value == "production"
    assert Environment.TEST.value == "test"

    # LogLevel
    assert LogLevel.DEBUG.value == "DEBUG"
    assert LogLevel.INFO.value == "INFO"
    assert LogLevel.WARNING.value == "WARNING"
    assert LogLevel.ERROR.value == "ERROR"
    assert LogLevel.CRITICAL.value == "CRITICAL"

    # OrderSide
    assert OrderSide.BUY.value == "BUY"
    assert OrderSide.SELL.value == "SELL"

    # PositionSide
    assert PositionSide.LONG.value == "LONG"
    assert PositionSide.SHORT == "SHORT"

    # OrderType
    assert OrderType.MARKET.value == "MARKET"
    assert OrderType.LIMIT.value == "LIMIT"

    # TimeInForce
    assert TimeInForce.GTC.value == "GTC"
    assert TimeInForce.IOC.value == "IOC"
    assert TimeInForce.FOK.value == "FOK"
    assert TimeInForce.POST_ONLY.value == "POST_ONLY"

    # PositionMode
    assert PositionMode.ONE_WAY.value == "ONE_WAY"
    assert PositionMode.HEDGE.value == "HEDGE"


def test_constants() -> None:
    """Verify that domain constants are correctly set."""
    assert DEFAULT_EXCHANGE == Exchange.BYBIT
    assert DEFAULT_MARKET == MarketType.USDT_PERPETUAL
    assert MIN_SYMBOL_LENGTH == 3  # noqa: PLR2004
    assert MAX_SYMBOL_LENGTH == 20  # noqa: PLR2004
    assert "1m" in SUPPORTED_TIMEFRAMES
    assert "1w" in SUPPORTED_TIMEFRAMES


def test_symbol_validation_success() -> None:
    """Verify valid symbols pass checks and act like strings."""
    sym1 = Symbol("BTCUSDT")
    assert sym1 == "BTCUSDT"
    assert isinstance(sym1, str)
    assert repr(sym1) == "Symbol('BTCUSDT')"

    sym2 = Symbol("1000PEPEUSDT")
    assert sym2 == "1000PEPEUSDT"


def test_symbol_validation_failures() -> None:
    """Verify that invalid symbols are correctly rejected."""
    # 1. Non-string type
    with pytest.raises(TypeError, match=r"Symbol must be a string\."):
        Symbol(123)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match=r"Symbol must be a string\."):
        Symbol(None)  # type: ignore[arg-type]

    # 2. Empty string
    with pytest.raises(ValueError, match=r"Symbol cannot be empty\."):
        Symbol("")

    # 3. Contains whitespace
    with pytest.raises(ValueError, match=r"Symbol cannot contain whitespace\."):
        Symbol("BTC USDT")
    with pytest.raises(ValueError, match=r"Symbol cannot contain whitespace\."):
        Symbol(" BTC")
    with pytest.raises(ValueError, match=r"Symbol cannot contain whitespace\."):
        Symbol("BTC\n")

    # 4. Length out of bounds (min limit)
    with pytest.raises(ValueError, match="Symbol length must be at least"):
        Symbol("BT")

    # 5. Length out of bounds (max limit)
    too_long_symbol = "A" * (MAX_SYMBOL_LENGTH + 1)
    with pytest.raises(ValueError, match="Symbol length must be at most"):
        Symbol(too_long_symbol)

    # 6. Lowercase symbols
    with pytest.raises(
        ValueError, match=r"Symbol cannot contain lowercase characters\."
    ):
        Symbol("btcusdt")
    with pytest.raises(
        ValueError, match=r"Symbol cannot contain lowercase characters\."
    ):
        Symbol("BtcUsdt")

    # 7. Invalid characters
    with pytest.raises(ValueError, match="Symbol contains invalid characters"):
        Symbol("BTC-USDT")
    with pytest.raises(ValueError, match="Symbol contains invalid characters"):
        Symbol("BTC/USDT")
    with pytest.raises(ValueError, match="Symbol contains invalid characters"):
        Symbol("BTC.USDT")


def test_timeframe_validation_success() -> None:
    """Verify that every supported timeframe is accepted and behaves correctly."""
    for tf_str in SUPPORTED_TIMEFRAMES:
        tf = Timeframe(tf_str)
        assert tf == tf_str
        assert isinstance(tf, str)
        assert repr(tf) == f"Timeframe('{tf_str}')"


def test_timeframe_validation_failures() -> None:
    """Verify that invalid timeframes are rejected."""
    # 1. Non-string type
    with pytest.raises(TypeError, match=r"Timeframe must be a string\."):
        Timeframe(123)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match=r"Timeframe must be a string\."):
        Timeframe(None)  # type: ignore[arg-type]

    # 2. Invalid timeframe values
    with pytest.raises(ValueError, match="Invalid timeframe"):
        Timeframe("2m")
    with pytest.raises(ValueError, match="Invalid timeframe"):
        Timeframe("abc")
    with pytest.raises(ValueError, match="Invalid timeframe"):
        Timeframe("")

"""Domain timeframe model for the quant-platform."""

from typing import override

from quant_platform.domain.constants import SUPPORTED_TIMEFRAMES


class Timeframe(str):
    """An immutable domain type representing a validated timeframe."""

    def __new__(cls, value: str) -> "Timeframe":
        """Validate and create a new Timeframe instance.

        Args:
            value: The timeframe string representation.

        Returns:
            Timeframe: The validated, immutable timeframe object.

        Raises:
            TypeError: If the input is not a string.
            ValueError: If the input is not a supported timeframe.
        """
        if not isinstance(value, str):
            msg = "Timeframe must be a string."
            raise TypeError(msg)

        if value not in SUPPORTED_TIMEFRAMES:
            msg = (
                f"Invalid timeframe: '{value}'. "
                f"Must be one of {sorted(SUPPORTED_TIMEFRAMES)}"
            )
            raise ValueError(msg)

        return super().__new__(cls, value)

    @override
    def __repr__(self) -> str:
        """Return the string representation for debugging."""
        return f"Timeframe({super().__repr__()})"

"""Domain symbol model for the quant-platform."""

import re
from typing import override

from quant_platform.domain.constants import MAX_SYMBOL_LENGTH, MIN_SYMBOL_LENGTH


class Symbol(str):
    """An immutable domain type representing a validated trading symbol."""

    def __new__(cls, value: str) -> "Symbol":
        """Validate and create a new Symbol instance.

        Args:
            value: The symbol string representation.

        Returns:
            Symbol: The validated, immutable symbol object.

        Raises:
            TypeError: If the input is not a string.
            ValueError: If the input fails validation checks.
        """
        if not isinstance(value, str):
            msg = "Symbol must be a string."
            raise TypeError(msg)

        # Reject empty values
        if not value:
            msg = "Symbol cannot be empty."
            raise ValueError(msg)

        # Reject whitespace
        if any(c.isspace() for c in value):
            msg = "Symbol cannot contain whitespace."
            raise ValueError(msg)

        # Length validation
        if len(value) < MIN_SYMBOL_LENGTH:
            msg = f"Symbol length must be at least {MIN_SYMBOL_LENGTH} characters."
            raise ValueError(msg)
        if len(value) > MAX_SYMBOL_LENGTH:
            msg = f"Symbol length must be at most {MAX_SYMBOL_LENGTH} characters."
            raise ValueError(msg)

        # Reject lowercase symbols
        if any(c.islower() for c in value):
            msg = "Symbol cannot contain lowercase characters."
            raise ValueError(msg)

        # Validate invalid characters (Only uppercase alphanumeric allowed)
        if not re.match(r"^[A-Z0-9]+$", value):
            msg = (
                "Symbol contains invalid characters. "
                "Only uppercase alphanumeric are allowed."
            )
            raise ValueError(msg)

        return super().__new__(cls, value)

    @override
    def __repr__(self) -> str:
        """Return the string representation for debugging."""
        return f"Symbol({super().__repr__()})"

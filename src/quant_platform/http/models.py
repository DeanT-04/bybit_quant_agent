"""Data models for the HTTP transport layer.

Defines HttpConfig and HttpResponse models used by HttpClient.
"""

import json
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from quant_platform.exceptions import InvalidResponseError


class HttpConfig(BaseModel):
    """Configuration options for the HTTP client."""

    model_config = ConfigDict(frozen=True)

    timeout: float = Field(
        default=10.0,
        ge=0.0,
        description="Request timeout in seconds.",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        description="Maximum number of retries for transient errors.",
    )
    backoff_factor: float = Field(
        default=0.3,
        ge=0.0,
        description="Backoff factor for retry delays.",
    )
    pool_connections: int = Field(
        default=10,
        gt=0,
        description="Number of connection pools to cache.",
    )
    pool_maxsize: int = Field(
        default=10,
        gt=0,
        description="Maximum size of the connection pool.",
    )
    status_forcelist: list[int] = Field(
        default_factory=lambda: [500, 502, 503, 504],
        description="HTTP status codes to trigger retry on.",
    )


@dataclass(frozen=True)
class HttpResponse:
    """Typed response object returned by HttpClient."""

    status_code: int
    headers: dict[str, str]
    text: str

    def json(self) -> Any:
        """Parse response text as JSON.

        Raises:
            InvalidResponseError: If the response is not valid JSON.
        """
        try:
            return json.loads(self.text)
        except json.JSONDecodeError as e:
            raise InvalidResponseError(
                f"Failed to parse response body as JSON: {e}"
            ) from e

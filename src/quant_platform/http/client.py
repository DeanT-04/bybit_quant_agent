"""HTTP transport client implementation for the Quant Platform.

Implements HttpClient using requests.Session with connection pooling, retries,
and standard logging. Maps requests exceptions to project exceptions.
"""

import logging
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from quant_platform.exceptions import (
    ConnectionError as ProjectConnectionError,
)
from quant_platform.exceptions import (
    QuantPlatformError,
)
from quant_platform.exceptions import (
    TimeoutError as ProjectTimeoutError,
)
from quant_platform.http.models import HttpConfig, HttpResponse


class HttpClient:
    """A reusable, exchange-agnostic HTTP transport layer client."""

    def __init__(self, config: HttpConfig, logger: logging.Logger) -> None:
        """Initialize the HttpClient with injected configuration and logger.

        Args:
            config: Configuration settings for the HTTP transport.
            logger: Logger instance to write request and response information.
        """
        self._config = config
        self._logger = logger
        self._session = requests.Session()

        # Configure connection pooling and retries
        retry_strategy = Retry(
            total=self._config.max_retries,
            backoff_factor=self._config.backoff_factor,
            status_forcelist=self._config.status_forcelist,
            raise_on_status=False,  # We handle status checks/errors at domain level
        )
        adapter = HTTPAdapter(
            pool_connections=self._config.pool_connections,
            pool_maxsize=self._config.pool_maxsize,
            max_retries=retry_strategy,
        )
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

    def get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> HttpResponse:
        """Perform an HTTP GET request.

        Args:
            url: Target URL for the request.
            params: Dictionary of query parameters to send.
            headers: Dictionary of HTTP headers to send.

        Returns:
            HttpResponse containing status code, headers, and text body.

        Raises:
            TimeoutError: If the HTTP request times out.
            ConnectionError: If connection to the host fails.
            QuantPlatformError: For any other request errors.
        """
        return self._request("GET", url, params=params, headers=headers)

    def post(
        self,
        url: str,
        data: Any | None = None,
        json: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> HttpResponse:
        """Perform an HTTP POST request.

        Args:
            url: Target URL for the request.
            data: Data to send in the body of the request (form-encoded, etc.).
            json: JSON serializable object to send in the body of the request.
            headers: Dictionary of HTTP headers to send.

        Returns:
            HttpResponse containing status code, headers, and text body.

        Raises:
            TimeoutError: If the HTTP request times out.
            ConnectionError: If connection to the host fails.
            QuantPlatformError: For any other request errors.
        """
        return self._request("POST", url, data=data, json=json, headers=headers)

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self._logger.info("Closing HTTP transport client session.")
        self._session.close()

    def _request(  # noqa: PLR0913
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        data: Any | None = None,
        json: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> HttpResponse:
        """Execute HTTP request with session pooling, timeout and retry."""
        self._logger.debug("Executing HTTP %s request to %s", method, url)
        try:
            response = self._session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json,
                headers=headers,
                timeout=self._config.timeout,
            )
            # Log basic response metadata
            self._logger.debug(
                "Received HTTP %d response from %s",
                response.status_code,
                url,
            )
            # Convert requests headers CaseInsensitiveDict to standard dict
            res_headers = dict(response.headers)
            return HttpResponse(
                status_code=response.status_code,
                headers=res_headers,
                text=response.text,
            )
        except requests.exceptions.Timeout as e:
            msg = f"HTTP request to {url} timed out: {e}"
            self._logger.error(msg)
            raise ProjectTimeoutError(msg) from e
        except requests.exceptions.ConnectionError as e:
            msg = f"HTTP connection to {url} failed: {e}"
            self._logger.error(msg)
            raise ProjectConnectionError(msg) from e
        except requests.exceptions.RequestException as e:
            msg = f"HTTP request to {url} failed: {e}"
            self._logger.error(msg)
            raise QuantPlatformError(msg) from e

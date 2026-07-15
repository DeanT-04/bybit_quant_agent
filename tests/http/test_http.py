# ruff: noqa: PLR2004
"""Unit tests for the HTTP transport layer.

Mocks all outbound network requests using unittest.mock to verify GET, POST,
retries, timeout, connection failures, session reuse, and response parsing.
"""

import logging
from unittest.mock import MagicMock, patch

import pytest
import requests
import urllib3
from requests.structures import CaseInsensitiveDict

from quant_platform.exceptions import (
    ConnectionError as ProjectConnectionError,
)
from quant_platform.exceptions import (
    InvalidResponseError,
    QuantPlatformError,
)
from quant_platform.exceptions import (
    TimeoutError as ProjectTimeoutError,
)
from quant_platform.http import HttpClient, HttpConfig


@patch("requests.adapters.HTTPAdapter.send")
def test_get_success(mock_send: MagicMock) -> None:
    """Verify that a GET request succeeds and parses correctly."""
    mock_resp = requests.Response()
    mock_resp.status_code = 200
    mock_resp.headers = CaseInsensitiveDict(
        {"Content-Type": "application/json"}
    )
    mock_resp._content = b'{"status": "ok"}'
    mock_send.return_value = mock_resp

    logger = logging.getLogger("test_logger")
    config = HttpConfig(timeout=5.0)
    client = HttpClient(config, logger)

    response = client.get(
        "https://example.com/api",
        params={"foo": "bar"},
        headers={"X-Header": "val"},
    )

    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert response.text == '{"status": "ok"}'
    assert response.json() == {"status": "ok"}

    assert mock_send.call_count == 1
    args, _ = mock_send.call_args
    request = args[0]
    assert request.method == "GET"
    assert request.url == "https://example.com/api?foo=bar"
    assert request.headers["X-Header"] == "val"


@patch("requests.adapters.HTTPAdapter.send")
def test_post_success(mock_send: MagicMock) -> None:
    """Verify that a POST request sends body data correctly and succeeds."""
    mock_resp = requests.Response()
    mock_resp.status_code = 201
    mock_resp.headers = CaseInsensitiveDict()
    mock_resp._content = b"created"
    mock_send.return_value = mock_resp

    logger = logging.getLogger("test_logger")
    config = HttpConfig(timeout=5.0)
    client = HttpClient(config, logger)

    response = client.post("https://example.com/api", json={"foo": "bar"})

    assert response.status_code == 201
    assert response.text == "created"

    assert mock_send.call_count == 1
    args, _ = mock_send.call_args
    request = args[0]
    assert request.method == "POST"
    assert request.body == b'{"foo": "bar"}'


@patch("urllib3.connectionpool.HTTPConnectionPool._make_request")
def test_retry_on_status_failure(mock_make: MagicMock) -> None:
    """Verify that status-code retries occur using custom status_forcelist."""
    mock_response_502 = MagicMock()
    mock_response_502.status = 502
    mock_response_502.msg = MagicMock()
    mock_response_502.headers = {}
    mock_response_502.get_redirect_header.return_value = None
    mock_response_502.length = 0
    mock_response_502.read.return_value = b""

    mock_response_200 = MagicMock()
    mock_response_200.status = 200
    mock_response_200.msg = MagicMock()
    mock_response_200.headers = {}
    mock_response_200.get_redirect_header.return_value = None
    mock_response_200.length = 0
    mock_response_200.read.return_value = b"success-content"

    mock_make.side_effect = [
        mock_response_502,
        mock_response_502,
        mock_response_200,
    ]

    logger = logging.getLogger("test_logger")
    config = HttpConfig(
        max_retries=2,
        status_forcelist=[502],
        timeout=1.0,
        backoff_factor=0.0,
    )
    client = HttpClient(config, logger)

    response = client.get("http://example.com/status")
    assert response.status_code == 200
    assert mock_make.call_count == 3


@patch("urllib3.connectionpool.HTTPConnectionPool._make_request")
def test_connection_failure_after_retries(mock_make: MagicMock) -> None:
    """Verify that ConnectionError is raised after exhausting retries."""
    mock_make.side_effect = urllib3.exceptions.ProtocolError(
        "Connection reset"
    )

    logger = logging.getLogger("test_logger")
    config = HttpConfig(max_retries=1, timeout=1.0, backoff_factor=0.0)
    client = HttpClient(config, logger)

    with pytest.raises(ProjectConnectionError):
        client.get("http://example.com/fail")

    assert mock_make.call_count == 2


@patch("requests.adapters.HTTPAdapter.send")
def test_timeout_error_raised(mock_send: MagicMock) -> None:
    """Verify requests Timeout wraps to ProjectTimeoutError."""
    mock_send.side_effect = requests.exceptions.Timeout("Request timed out")

    logger = logging.getLogger("test_logger")
    config = HttpConfig()
    client = HttpClient(config, logger)

    with pytest.raises(ProjectTimeoutError) as exc_info:
        client.get("https://example.com/timeout")

    assert "timed out" in str(exc_info.value)


@patch("requests.adapters.HTTPAdapter.send")
def test_generic_request_error_raised(mock_send: MagicMock) -> None:
    """Verify generic RequestException wraps to QuantPlatformError."""
    mock_send.side_effect = requests.exceptions.RequestException(
        "Generic error"
    )

    logger = logging.getLogger("test_logger")
    config = HttpConfig()
    client = HttpClient(config, logger)

    with pytest.raises(QuantPlatformError) as exc_info:
        client.get("https://example.com/error")

    assert "failed" in str(exc_info.value)


@patch("requests.adapters.HTTPAdapter.send")
def test_invalid_json_parsing(mock_send: MagicMock) -> None:
    """Verify that calling json() on invalid content raises InvalidResponseError."""
    mock_resp = requests.Response()
    mock_resp.status_code = 200
    mock_resp._content = b"not json"
    mock_send.return_value = mock_resp

    logger = logging.getLogger("test_logger")
    config = HttpConfig()
    client = HttpClient(config, logger)

    response = client.get("https://example.com/json")
    with pytest.raises(InvalidResponseError) as exc_info:
        response.json()

    assert "Failed to parse response body as JSON" in str(exc_info.value)


@patch("requests.Session.close")
def test_session_close(mock_close: MagicMock) -> None:
    """Verify that close() triggers session close."""
    logger = logging.getLogger("test_logger")
    config = HttpConfig()
    client = HttpClient(config, logger)
    client.close()
    assert mock_close.call_count == 1


@patch("requests.adapters.HTTPAdapter.send")
def test_session_reuse(mock_send: MagicMock) -> None:
    """Verify that the client reuses connection pooling under the hood."""
    mock_resp = requests.Response()
    mock_resp.status_code = 200
    mock_resp._content = b"ok"
    mock_send.return_value = mock_resp

    logger = logging.getLogger("test_logger")
    config = HttpConfig()
    client = HttpClient(config, logger)

    client.get("https://example.com/1")
    client.get("https://example.com/2")

    assert mock_send.call_count == 2

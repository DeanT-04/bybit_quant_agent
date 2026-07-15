# EBS-007 — HTTP Transport Layer

## Purpose
Create a reusable, exchange-agnostic HTTP transport layer client supporting persistent sessions, connection pooling, retries, and clean mappings of library-specific exceptions to project-specific exceptions.

## Status
Completed.

## Details
- Implemented `HttpClient` in `src/quant_platform/http/client.py` using `requests.Session`.
- Configured connection pooling and automatic retry policies via urllib3 `Retry` mounted to the HTTP session adapters.
- Created `HttpConfig` (frozen Pydantic model) and `HttpResponse` (frozen dataclass supporting automatic JSON parsing) in `src/quant_platform/http/models.py`.
- Mapped all `requests.exceptions` to project-specific exceptions (`TimeoutError`, `ConnectionError`, `QuantPlatformError`).
- Injected `HttpConfig` and `logging.Logger` into `HttpClient` to keep the layer domain-blind and testable.
- Documented package details and future usage under `Architecture.md`.

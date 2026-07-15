# EBS-006 — Central Error & Exception Framework

## Purpose
Create a centralized application exception framework where every project-specific exception inherits from one common base class.

## Status
Completed.

## Details
- Established base `QuantPlatformError` class inheriting from Python's built-in `Exception`.
- Implemented core domain and infrastructure exceptions: `ConfigurationError`, `LoggingError`, `ValidationError`, `StorageError`, `MarketDataError`, `ResearchError`, `BacktestError`, `ExecutionError`, `RiskError`.
- Created exchange specific hierarchy: `ExchangeError` (base), and subclasses `AuthenticationError`, `ConnectionError`, `TimeoutError`, `RateLimitError`, `InvalidResponseError`.
- Integrated strict checks to ensure no side effects (no logging, no I/O) are triggered during exception initialization or instantiation.
- Updated `Architecture.md` to document the exceptions hierarchy and extension guidelines.

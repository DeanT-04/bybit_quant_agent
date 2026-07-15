# Quant Platform

## Project Overview
This repository contains the foundation for a professional-grade, long-term quantitative cryptocurrency trading platform. Designed for incremental, robust development, it is built with high reliability, strict type safety, and clean software architecture patterns.

## Goals
- **Professional-Grade Research**: Establish a robust environment for backtesting and analyzing trading strategies.
- **Automated Trading**: Execute trades with minimal latency, maximum reliability, and safety boundaries.
- **Exchange Integration**: Exclusively support the Bybit cryptocurrency exchange (no other exchange integrations will be added).
- **Production Quality**: Maintain absolute type safety, comprehensive test coverage, and strict code formatting from day one.

## Current Milestone
- **EBS-001 — Project Foundation**: Initialize the project structure, dependency configurations, and local environments without any trading logic, database integration, API communication, or custom strategies.

## Folder Structure
```
quant-platform/
├── config/              # Configuration files and templates
├── data/                # Data storage directory (ignored by git)
├── docs/                # Project documentation and specifications
├── logs/                # Application runtime logs (ignored by git)
├── scripts/             # Utility and automation scripts
├── src/                 # Application source code
│   └── quant_platform/  # Main application package
│       ├── __init__.py  # Package initializer
│       └── main.py      # Entry point
├── tests/               # Unit, integration, and regression tests
│   └── test_main.py     # Entry point smoke test
├── .env.example         # Example environment template
├── .gitignore           # Git ignore patterns
├── LICENSE              # License file (MIT)
├── pdm.lock             # PDM lockfile (ensures deterministic installs)
├── pyproject.toml       # Build system config, dependencies, and lint tool configs
└── README.md            # Project documentation (this file)
```

## Development Philosophy
- **Incremental Progress**: Build only what is requested in the current milestone. Do not anticipate or design for hypothetical future features.
- **No Placeholder Code**: Avoid placeholder logic, blank classes, empty functions, or `TODO` comment tags.
- **Strict Quality Controls**: Every commit must pass all quality tools (Ruff, MyPy strict mode, Pytest) with zero warnings or errors.
- **No Over-Engineering**: Keep implementations simple, focused, and directly aligned with the acceptance criteria.

## Why PDM?
This project uses **PDM (Python Dependency Manager)** as its package manager. Unlike Rust-based managers (such as `uv` or `pixi`), PDM is written in Python and runs fully inside standard `python.exe`. This guarantees that it bypasses the legacy Winsock Layered Service Provider (LSP) injection crashes (such as those triggered by Astrill VPN's `ASProxy.dll` on Windows), ensuring a stable development experience without requiring dangerous system-level workarounds.

## How to Run
Ensure you have Python 3.13 and PDM installed. To install PDM:
```bash
pip install --user pdm
```

1. Navigate to the project directory:
   ```bash
   cd quant-platform
   ```
2. Synchronize dependencies and virtual environment:
   ```bash
   pdm install
   ```
3. Run the application:
   ```bash
   pdm run start
   ```
   *Expected output: `Platform Started Successfully`*

## How to Run Tests and Quality Checks
To run all tests and execute static analysis:

- **Run Pytest**:
  ```bash
  pdm run test
  ```
- **Run Ruff (Linter)**:
  ```bash
  pdm run lint
  ```
- **Run MyPy (Strict Type Check)**:
  ```bash
  pdm run typecheck
  ```

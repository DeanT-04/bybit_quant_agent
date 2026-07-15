# Quant Platform Architecture Documentation

## Repository Philosophy
The Quant Platform is designed as a professional-grade, long-term quantitative cryptocurrency trading system. It prioritizes:
- **Absolute Type Safety**: Enforced strict-mode static type checks.
- **Incremental Stability**: Each milestone delivers a clean, operational build with 100% test coverage.
- **Clean Separation of Concerns**: Clean boundaries between business domain definitions and infrastructure/API implementations.

---

## Architecture Principles
1. **Unidirectional Dependencies**: Packages must import only from packages above themselves in the import chain.
2. **Business Capabilities Over Layers**: Directories correspond to high-level system functions (e.g. `backtesting`, `risk`, `execution`) rather than technical abstractions (`models`, `views`, `controllers`).
3. **Purity of Domain Model**: The `domain/` package represents pure business logic and must remain free from all network, storage, database, configuration, and logging dependencies.
4. **No Shared/Common Packages**: Generic "utils" or "common" directories are strictly prohibited to avoid coupling.

---

## Folder Structure
```text
bybit_quant_agent/ (Repository Root)
├── config/              # YAML config files and templates
├── data/                # Data storage (market, backtests, paper, live)
├── docs/                # Architecture, API, and Engineering milestone docs
├── logs/                # Application runtime logs
├── scripts/             # Automation and convenience scripts
├── tests/               # Test suites mirroring the src/ structure
└── src/
    └── quant_platform/  # Python package root
        ├── __init__.py
        ├── main.py      # Entry point and Composition Root
        └── [packages]   # 17 standard business modules
```

---

## Package Responsibilities
Each package under `src/quant_platform/` has a single, strictly defined scope of responsibility:

| Package | Responsibility |
|---|---|
| `config` | Configuration loading, schema definitions, validation. |
| `logging` | Centralized Stream and Rotating File logging. |
| `domain` | Business types, enums, constants, validation (pure domain). |
| `exchange` | REST and WebSocket communication with Bybit, authentication. |
| `storage` | Persistent storage integration, Parquet format, repository layers. |
| `market_data` | Historical market data downloaders, local caching, validation. |
| `indicators` | Technical indicator formulas and calculations (pure). |
| `features` | Feature engineering transformations and processing pipelines. |
| `research` | Strategy research notebook resources, experimentation metrics. |
| `optimization` | Parameter search, walk-forward analysis, hyperparameter tuning. |
| `backtesting` | Event-driven or vector-based historical simulation engine. |
| `paper_trading` | Real-time mock execution and portfolio simulation. |
| `execution` | Live order routing, position tracking, exchange synchronizers. |
| `portfolio` | Risk-parity, capital allocation, rebalancing calculators. |
| `risk` | Capital constraints, drawdown tracking, automated kill switches. |
| `monitoring` | Application health checks, system metrics, push alerts. |
| `ai` | Strategy review and assistance modules. |

---

## Dependency Graph & Import Rules
Import hierarchy goes sequentially downward. Packages may only import from packages positioned **above** them in the flow:

```mermaid
graph TD
    config --> logging
    logging --> domain
    domain --> exchange
    exchange --> storage
    storage --> market_data
    market_data --> indicators
    indicators --> features
    features --> research
    research --> optimization
    optimization --> backtesting
    backtesting --> paper_trading
    paper_trading --> execution
    execution --> portfolio
    portfolio --> risk
    risk --> monitoring
    monitoring --> ai
```

### Import Constraints
1. **Never Import Below**: A package must never import from any package lower than itself in the chain (e.g. `domain` cannot import from `exchange`).
2. **Never Import Sideways**: Sideways imports are disabled unless explicitly documented and verified in architectural reviews.
3. **No Circular Imports**: Dependencies must be strictly acyclic.
4. **Wildcard Imports**: Wildcard (`from x import *`) imports are prohibited.

---

## Naming Conventions
- **Packages/Modules**: Lowercase snake_case (e.g., `market_data`).
- **Classes/Type Parameters**: PascalCase (e.g., `Symbol`).
- **Functions/Methods/Variables**: Lowercase snake_case (e.g., `load_config`).
- **Constants**: Uppercase snake_case (e.g., `MAX_SYMBOL_LENGTH`).
- **Test files**: Prefixed with `test_` (e.g., `test_logging.py`).

---

## Future Extensions & Extension Rules
When implementing future milestones:
1. **Build inside the structure**: Place all new capabilities within the corresponding 17 pre-defined packages.
2. **No new top-level packages**: The layout of `src/quant_platform/` established here is static and final.
3. **Initialize correctly**: Ensure every sub-package folder contains `__init__.py` (both in `src/` and `tests/`).
4. **Maintain Test Mirroring**: Place all tests inside their mirrored packages (e.g. `tests/execution/test_orders.py` mirrors `src/quant_platform/execution/orders.py`).

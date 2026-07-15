# EBS-004 — Domain Model

## Purpose
Define the foundational, immutable domain types representing common business languages and constraints across the platform.

## Status
Completed.

## Details
- Created core domain enums (e.g. `Exchange`, `MarketType`, `OrderSide`, `PositionMode`).
- Implemented immutable `Symbol` and `Timeframe` validation types.
- Defined PEP 695 type aliases (e.g. `Price`, `Quantity`).
- Added strict length and character validation to ensure domain-level data purity.

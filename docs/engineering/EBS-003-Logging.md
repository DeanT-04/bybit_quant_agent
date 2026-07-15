# EBS-003 — Central Logging Framework

## Purpose
Implement the central, structured logging framework utilizing Python Standard Library logging.

## Status
Completed.

## Details
- Implemented `create_logger` central factory.
- Added StreamHandler (console) and RotatingFileHandler (UTF-8, 10MB limit, 10 backup counts).
- Implemented custom `ISO8601Formatter` ensuring uniform ISO-8601 formatting across console and file output.
- Prevented handler duplicates and unnecessary propagation.
- Integrated into `main.py` composition root.

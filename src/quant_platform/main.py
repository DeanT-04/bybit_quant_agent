"""Main entry point for the quant_platform application."""

from quant_platform.config import load_config
from quant_platform.logging import create_logger


def main() -> None:
    """Run the platform startup routine."""
    # Composition Root: load config first to validate environment
    config = load_config()
    logger = create_logger(config)
    logger.info("Application started successfully.")


if __name__ == "__main__":
    main()


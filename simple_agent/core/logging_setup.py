"""
Logging configuration for the application.
"""

import logging
import sys
from pathlib import Path


def setup_logging(
    log_file: str, log_level: str = "INFO", console_enabled: bool = False
) -> None:
    """
    Configure logging for the application.

    Args:
        log_file: Path to log file (relative to project root)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console_enabled: Whether to also log to console (only for CLI mode)
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # File handler (always enabled)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(getattr(logging, log_level.upper()))

    # Detailed format with line numbers
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler (only for CLI mode, not REPL)
    if console_enabled:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.WARNING)  # Less verbose for console
        console_formatter = logging.Formatter("[%(levelname)s] %(message)s")
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    logger.info(f"Logging initialized: {log_file} (level={log_level})")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)

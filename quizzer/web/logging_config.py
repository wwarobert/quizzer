"""
Logging configuration for web server.

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(file_level=logging.DEBUG, console_level=logging.DEBUG):
    """
    Configure logging with file and console handlers.

    Args:
        file_level: Log level for file handler (default: DEBUG - logs everything)
        console_level: Log level for console handler (default: DEBUG - logs everything)

    Returns:
        logger: Configured logger instance
    """
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Create logger
    logger = logging.getLogger("quizzer")
    logger.setLevel(logging.DEBUG)  # Set to lowest level, handlers will filter

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # File handler with rotation (max 10MB, keep 5 backup files)
    log_file = logs_dir / "web_quiz.log"
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"  # 10MB
    )
    file_handler.setLevel(file_level)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

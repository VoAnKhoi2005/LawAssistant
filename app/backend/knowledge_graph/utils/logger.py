"""
Logging utilities
"""

import logging
import os
from typing import Tuple, Optional


def setup_logger(
    name: str = "law_assistant",
    level: int = logging.INFO,
    log_to_file: bool = False,
    file_path: Optional[str] = None
) -> Tuple[logging.Logger, logging.StreamHandler, Optional[logging.FileHandler]]:
    """
    Set up logger with console and optional file output
    
    Args:
        name: Logger name
        level: Logging level (logging.INFO, logging.DEBUG, etc.)
        log_to_file: Whether to log to file
        file_path: Path to log file (auto-generated if None)
        
    Returns:
        Tuple of (logger, console_handler, file_handler)
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    # Prevent duplicate handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(console_handler)

    # File handler (optional)
    file_handler = None
    if log_to_file:
        if not file_path:
            file_path = os.path.join(os.getcwd(), "logs", f"{name}.log")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        file_handler = logging.FileHandler(file_path, encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        )
        logger.addHandler(file_handler)

        logger.info(f"Logging to file: {file_path}")

    return logger, console_handler, file_handler


def get_logger(name: str = "law_assistant") -> logging.Logger:
    """
    Get existing logger or create new one with default settings
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        setup_logger(name)
    return logger

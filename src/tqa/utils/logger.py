# src/tqa/utils/logger.py
import logging
import sys
from pathlib import Path
from datetime import datetime
from config.settings import BASE_DIR

# Define log directory relative to the project root
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

def setup_logger(name: str = "TQA", log_level: int = logging.INFO, console=None):
    """Configures a unified logger for console and file output."""
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # If handlers already exist, update the RichHandler console if provided
    if logger.handlers:
        from rich.logging import RichHandler
        updated = False
        for handler in logger.handlers:
            if isinstance(handler, RichHandler) and console is not None:
                handler.console = console
                updated = True
        if updated:
            return logger

    # Formatting
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(module)s:%(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 1. Console Handler (Using RichHandler for better progress bar integration)
    from rich.logging import RichHandler
    console_handler = RichHandler(console=console, rich_tracebacks=True)
    # RichHandler uses its own formatter, but we can set one if we want
    logger.addHandler(console_handler)

    # 2. File Handler (Save to logs/ folder)
    log_filename = f"pipeline_{datetime.now().strftime('%Y-%m-%d')}.log"
    file_handler = logging.FileHandler(LOG_DIR / log_filename)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Create the logger instance to be used throughout the app
logger = setup_logger()

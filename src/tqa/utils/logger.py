# src/tqa/utils/logger.py
import logging
import sys
from pathlib import Path
from datetime import datetime
from config.settings import BASE_DIR

# Define log directory relative to the project root
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

def setup_logger(name: str = "TQA", log_level: int = logging.INFO):
    """Configures a unified logger for console and file output."""
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Prevent duplicate handlers if setup is called multiple times
    if logger.handlers:
        return logger

    # Formatting
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(module)s:%(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 1. Console Handler (Stream to stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. File Handler (Save to logs/ folder)
    log_filename = f"pipeline_{datetime.now().strftime('%Y-%m-%d')}.log"
    file_handler = logging.FileHandler(LOG_DIR / log_filename)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Create the logger instance to be used throughout the app
logger = setup_logger()
# logger.py
import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

def setup_logger(name):
    """Sets up a daily rotating logger that saves to logs/{name}.log and merged.log"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False  # Prevent double logging if root logger also logs

    # File handler for this logger
    log_path = os.path.join(log_dir, f"{name}.log")
    file_handler = TimedRotatingFileHandler(
        log_path, when="midnight", interval=1, backupCount=7, encoding="utf-8"
    )
    file_handler.suffix = "%Y-%m-%d"
    file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

    # Merged file handler
    merged_path = os.path.join(log_dir, "merged.log")
    merged_handler = TimedRotatingFileHandler(
        merged_path, when="midnight", interval=1, backupCount=7, encoding="utf-8"
    )
    merged_handler.suffix = "%Y-%m-%d"
    merged_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.addHandler(merged_handler)

    return logger
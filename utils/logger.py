# logger.py
import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

def setup_logger(name):
    """Sets up a daily rotating logger that saves to logs/YYYY-MM-DD.log"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    # Name log file depending on name
    log_path = os.path.join(log_dir, f"{name}.log")

    # File handler (rotates daily, keeps 7 days)
    handler = TimedRotatingFileHandler(
        log_path, when="midnight", interval=1, backupCount=7, encoding="utf-8"
    )
    handler.suffix="%Y-%m-%d"

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    handler.setFormatter(formatter)

    # Logger
    logger = logging.getLogger(name)
    logger.addHandler(console_handler)
    logger.addHandler(handler)
    logger.propagate = False
    logger.setLevel(logging.INFO)

    return logger
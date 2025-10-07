# logger.py
import logging
import os
from logging.handlers import TimedRotatingFileHandler

def setup_logger(name):
    """Sets up a daily rotating logger that saves to logs/YYYY-MM-DD.log"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    if name == "coup":
        log_path = os.path.join(log_dir, "coup.log")
    else:
        log_path = os.path.join(log_dir, "bot.log")

    handler = TimedRotatingFileHandler(
        log_path, when="midnight", interval=1, backupCount=7, encoding="utf-8"
    )
    handler.suffix="%Y-%m-%d"

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(messages)s"
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    return logger
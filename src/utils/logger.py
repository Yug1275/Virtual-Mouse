# src/utils/logger.py
# PURPOSE: Centralized logging configuration for the entire project.
#          Replaces scattered print() statements with proper log levels.

import logging
import os

def setup_logger(name="VirtualMouse", log_to_file=True):
    """
    Creates and configures a logger instance.

    Args:
        name        : identifier for this logger (shows in log output)
        log_to_file : if True, also writes logs to logs/app.log

    Returns:
        A configured logging.Logger object.
    """

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # capture everything; handlers filter display

    # Avoid adding duplicate handlers if setup_logger() is called more than once.
    if logger.handlers:
        return logger

    # --- FORMAT ---
    # Example output: 2026-06-18 14:32:10 | INFO | Camera opened successfully
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # --- CONSOLE HANDLER ---
    # Shows INFO and above in the terminal (DEBUG is too noisy for normal use).
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # --- FILE HANDLER ---
    # Writes EVERYTHING (including DEBUG) to a log file for later review.
    if log_to_file:
        log_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
        os.makedirs(log_dir, exist_ok=True)  # create logs/ folder if missing

        log_file_path = os.path.join(log_dir, 'app.log')
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
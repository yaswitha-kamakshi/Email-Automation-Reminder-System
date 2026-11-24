"""Logging: one console+file app log, plus separate sent/failed logs."""
import logging
from .config import LOGS_DIR


def _file_logger(name: str, filename: str, fmt: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:  # avoid duplicate handlers if called twice
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(LOGS_DIR / filename, encoding="utf-8")
        handler.setFormatter(logging.Formatter(fmt))
        logger.addHandler(handler)
        logger.propagate = False
    return logger


def setup_logging():
    """Return (app_logger, sent_logger, failed_logger)."""
    LOGS_DIR.mkdir(exist_ok=True)
    fmt = "%(asctime)s | %(levelname)s | %(message)s"

    app = logging.getLogger("email_automation")
    if not app.handlers:
        app.setLevel(logging.INFO)
        file_h = logging.FileHandler(LOGS_DIR / "app.log", encoding="utf-8")
        file_h.setFormatter(logging.Formatter(fmt))
        console_h = logging.StreamHandler()
        console_h.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s", "%H:%M:%S"))
        app.addHandler(file_h)
        app.addHandler(console_h)
        app.propagate = False

    sent = _file_logger("email_sent", "sent_emails.log", fmt)
    failed = _file_logger("email_failed", "failed_emails.log", fmt)
    return app, sent, failed

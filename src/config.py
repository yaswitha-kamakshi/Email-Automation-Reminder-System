"""Central configuration: folder paths and SMTP settings (read from environment)."""
import os
from pathlib import Path

try:  # python-dotenv is optional; .env is loaded if the package is installed
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUTS_DIR = BASE_DIR / "outputs"
LOGS_DIR = BASE_DIR / "logs"

CONTACTS_CSV = DATA_DIR / "contacts.csv"
REMINDERS_CSV = DATA_DIR / "reminders.csv"
LEDGER_CSV = OUTPUTS_DIR / "sent_ledger.csv"  # remembers real sends so reruns don't duplicate


def get_smtp_settings() -> dict:
    """Read SMTP credentials from environment variables (never hard-code them)."""
    return {
        "host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
        "port": int(os.getenv("SMTP_PORT", "465")),
        "user": os.getenv("SMTP_USER", ""),
        "password": os.getenv("SMTP_PASS", ""),
        "sender_name": os.getenv("SENDER_NAME", "Email Automation Demo"),
        "sender_email": os.getenv("SENDER_EMAIL", os.getenv("SMTP_USER", "")),
    }

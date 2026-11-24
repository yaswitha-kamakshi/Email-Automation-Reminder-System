"""Read contacts and reminders from CSV files and validate them."""
import re
import logging
import pandas as pd

log = logging.getLogger("email_automation")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
CONTACT_COLUMNS = {"contact_id", "name", "email", "company", "subscribed"}
REMINDER_COLUMNS = {"reminder_id", "contact_id", "title", "send_at", "repeat", "template", "details"}
VALID_REPEATS = {"none", "daily", "weekly"}


def is_valid_email(address: str) -> bool:
    return bool(EMAIL_RE.match(address or ""))


def _read_csv(path, required: set) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str).fillna("")
    df.columns = [c.strip() for c in df.columns]
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{path.name} is missing columns: {sorted(missing)}")
    return df.apply(lambda col: col.str.strip())


def load_contacts(path) -> dict:
    """Return {contact_id: contact_dict}."""
    df = _read_csv(path, CONTACT_COLUMNS)
    contacts = {row["contact_id"]: row for row in df.to_dict("records")}
    log.info("Loaded %d contacts from %s", len(contacts), path.name)
    return contacts


def load_reminders(path) -> list:
    """Return a list of reminder dicts with send_at converted to datetime."""
    df = _read_csv(path, REMINDER_COLUMNS)
    reminders = []
    for row in df.to_dict("records"):
        try:
            row["send_at"] = pd.to_datetime(row["send_at"]).to_pydatetime()
        except Exception:
            log.warning("Skipping reminder %s: bad send_at '%s'", row["reminder_id"], row["send_at"])
            continue
        row["repeat"] = (row["repeat"] or "none").lower()
        if row["repeat"] not in VALID_REPEATS:
            log.warning("Reminder %s: unknown repeat '%s', using 'none'", row["reminder_id"], row["repeat"])
            row["repeat"] = "none"
        reminders.append(row)
    log.info("Loaded %d reminders from %s", len(reminders), path.name)
    return reminders

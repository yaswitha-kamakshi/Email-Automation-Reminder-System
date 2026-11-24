"""Decide which reminders are due right now (one-off, daily or weekly)."""
from datetime import datetime, timedelta

STEP = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


def latest_occurrence(reminder: dict, now: datetime):
    """Most recent fire time <= now, or None if the reminder hasn't started yet."""
    start = reminder["send_at"]
    if start > now:
        return None
    step = STEP.get(reminder["repeat"])
    if step is None:  # one-off
        return start
    n = int((now - start) / step)
    return start + n * step


def find_due(reminders: list, now: datetime, done_keys: set) -> list:
    """Return [(reminder, occurrence, key)] not yet processed.
    key = reminder_id@occurrence - the idempotency key that prevents duplicate sends."""
    due = []
    for r in reminders:
        occ = latest_occurrence(r, now)
        if occ is None:
            continue
        key = f'{r["reminder_id"]}@{occ.isoformat()}'
        if key not in done_keys:
            due.append((r, occ, key))
    return sorted(due, key=lambda item: item[1])

"""Create dummy contacts + reminders (times are relative to NOW so the demo always works)."""
import csv
from datetime import datetime, timedelta
from .config import DATA_DIR

CONTACTS = [
    ("C001", "Aarav Sharma", "aarav.demo@example.com", "Demo Academy", "yes"),
    ("C002", "Priya Nair", "priya.demo@example.com", "Demo Academy", "yes"),
    ("C003", "Rohan Verma", "rohan.demo@example.com", "Acme Sales", "yes"),
    ("C004", "Sneha Reddy", "sneha.demo@example.com", "Acme HR", "yes"),
    ("C005", "Kiran Patel", "kiran.demo@example.com", "Acme Ops", "no"),      # unsubscribed -> skipped
    ("C006", "Meera Iyer", "meera.invalid-email", "Acme Ops", "yes"),         # bad email -> failed
    ("C007", "Vikram Rao", "vikram.demo@example.com", "Acme Finance", "yes"),
]


def main():
    DATA_DIR.mkdir(exist_ok=True)
    now = datetime.now().replace(microsecond=0)
    fmt = "%Y-%m-%d %H:%M:%S"
    reminders = [
        ("R001", "C001", "Python Class", now - timedelta(hours=2), "none", "class_reminder.txt", "Session starts at 7 PM - Zoom link in portal"),
        ("R002", "C002", "Python Class", now - timedelta(hours=2), "none", "class_reminder.txt", "Session starts at 7 PM - Zoom link in portal"),
        ("R003", "C003", "Invoice INV-1042", now - timedelta(days=1), "none", "payment_reminder.txt", "Amount due: Rs. 12,500 by 30 Nov"),
        ("R004", "C004", "Weekly Team Sync", now - timedelta(days=10), "weekly", "meeting_reminder.txt", "Monday 10 AM, Conference Room B"),
        ("R005", "C005", "Webinar: Intro to Automation", now - timedelta(hours=1), "none", "webinar_reminder.txt", "Starts at 6 PM IST"),
        ("R006", "C006", "Task Deadline", now - timedelta(minutes=30), "none", "class_reminder.txt", "Submit report by EOD"),
        ("R007", "C007", "Payment Follow-up", now - timedelta(minutes=5), "none", "no_such_template.txt", "Template missing on purpose"),
        ("R008", "C001", "Daily Standup", now - timedelta(days=3), "daily", "meeting_reminder.txt", "Every day 9:30 AM, Google Meet"),
        ("R009", "C003", "Webinar: Intro to Automation", now + timedelta(seconds=10), "none", "webinar_reminder.txt", "Starts at 6 PM IST"),
        ("R010", "C007", "Invoice INV-1050", now + timedelta(seconds=20), "none", "payment_reminder.txt", "Amount due: Rs. 4,200 by 5 Dec"),
    ]
    with open(DATA_DIR / "contacts.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["contact_id", "name", "email", "company", "subscribed"])
        w.writerows(CONTACTS)
    with open(DATA_DIR / "reminders.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["reminder_id", "contact_id", "title", "send_at", "repeat", "template", "details"])
        for r in reminders:
            w.writerow([r[0], r[1], r[2], r[3].strftime(fmt), *r[4:]])
    print(f"Created {len(CONTACTS)} contacts and {len(reminders)} reminders in {DATA_DIR}")


if __name__ == "__main__":
    main()

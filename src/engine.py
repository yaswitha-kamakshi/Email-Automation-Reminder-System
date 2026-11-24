"""Core processing: for each due reminder -> validate -> personalise -> send -> record result."""
import time
from datetime import datetime
from .data_loader import is_valid_email
from .template_engine import load_template, render
from .scheduler import find_due


def _result(r, contact, subject, status, error=""):
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "reminder_id": r["reminder_id"],
        "contact_name": (contact or {}).get("name", ""),
        "email": (contact or {}).get("email", ""),
        "subject": subject,
        "status": status,
        "error": error,
    }


def process_reminder(r, occ, contact, sender, loggers, pause=0.0):
    app, sent_log, failed_log = loggers
    subject = ""
    try:
        if contact is None:
            raise ValueError(f'Unknown contact_id "{r["contact_id"]}"')
        if contact["subscribed"].lower() not in ("yes", "true", "1"):
            app.info("SKIPPED %s (unsubscribed)", contact["email"])
            return _result(r, contact, "", "skipped", "Contact unsubscribed")
        if not is_valid_email(contact["email"]):
            raise ValueError(f'Invalid email address "{contact["email"]}"')

        subject_tpl, body_tpl = load_template(r["template"])
        context = {
            "name": contact["name"], "email": contact["email"], "company": contact["company"],
            "title": r["title"], "details": r["details"],
            "send_at": occ.strftime("%d %b %Y, %I:%M %p"),
            "sender_name": sender.s["sender_name"],
        }
        subject, body = render(subject_tpl, body_tpl, context)
        status, error = sender.send(contact["name"], contact["email"], subject, body)
        if pause and not sender.dry_run:
            time.sleep(pause)  # simple rate limit
    except Exception as e:  # any problem -> record as failed, keep processing others
        status, error = "failed", f"{type(e).__name__}: {e}"

    to = (contact or {}).get("email", "?")
    if status == "failed":
        app.error("FAILED  %s -> %s | %s", r["reminder_id"], to, error)
        failed_log.error("%s | %s | %s | %s", r["reminder_id"], to, subject, error)
    else:
        label = "DRY-RUN" if status == "dry_run" else "SENT   "
        app.info("%s %s -> %s | %s", label, r["reminder_id"], to, subject)
        sent_log.info("%s | %s | %s | %s", status, r["reminder_id"], to, subject)
    return _result(r, contact, subject, status, error)


def run_cycle(now, contacts, reminders, sender, done_keys, loggers, pause=0.0):
    """Process everything due at `now`. Returns list of result rows."""
    results = []
    for r, occ, key in find_due(reminders, now, done_keys):
        res = process_reminder(r, occ, contacts.get(r["contact_id"]), sender, loggers, pause)
        res["_key"] = key
        results.append(res)
        done_keys.add(key)
    return results

"""Send email through SMTP (or simulate it in dry-run mode)."""
import logging
import smtplib
import time
from email.message import EmailMessage

log = logging.getLogger("email_automation")


class EmailSender:
    def __init__(self, settings: dict, dry_run: bool = True, retries: int = 2):
        self.s = settings
        self.dry_run = dry_run
        self.retries = retries

    def check_credentials(self):
        if self.dry_run:
            return
        if not (self.s["user"] and self.s["password"]):
            raise RuntimeError("SMTP_USER / SMTP_PASS are not set. Copy .env.example to .env and fill it in.")

    def build_message(self, to_name, to_email, subject, body) -> EmailMessage:
        msg = EmailMessage()
        msg["From"] = f'{self.s["sender_name"]} <{self.s["sender_email"] or "demo@example.com"}>'
        msg["To"] = f"{to_name} <{to_email}>"
        msg["Subject"] = subject
        msg.set_content(body)
        return msg

    def send(self, to_name, to_email, subject, body):
        """Return (status, error). status is 'sent', 'dry_run' or 'failed'."""
        msg = self.build_message(to_name, to_email, subject, body)
        if self.dry_run:
            return "dry_run", ""

        last_error = ""
        for attempt in range(1, self.retries + 2):
            try:
                if self.s["port"] == 465:
                    server = smtplib.SMTP_SSL(self.s["host"], self.s["port"], timeout=20)
                else:  # 587 -> STARTTLS
                    server = smtplib.SMTP(self.s["host"], self.s["port"], timeout=20)
                    server.starttls()
                with server:
                    server.login(self.s["user"], self.s["password"])
                    server.send_message(msg)
                return "sent", ""
            except smtplib.SMTPAuthenticationError as e:
                return "failed", f"Authentication failed (check App Password): {e}"  # retrying won't help
            except Exception as e:  # network errors, refused recipients, etc.
                last_error = f"{type(e).__name__}: {e}"
                log.warning("Attempt %d failed for %s: %s", attempt, to_email, last_error)
                time.sleep(2)
        return "failed", last_error

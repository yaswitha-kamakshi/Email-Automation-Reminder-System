# Interview Preparation

### 1. Explain your project. ⭐
**Answer:** "I built an Email Automation & Reminder System in Python. It reads contacts and reminders from CSV files using pandas, fills email templates with each person's details, decides which reminders are due (one-time, daily or weekly), sends them through SMTP, and records every outcome in logs and a CSV report. It has a dry-run mode so I could test safely without sending real emails, it skips unsubscribed or invalid contacts, and it prevents duplicate sends. Credentials come from environment variables, so nothing sensitive is on GitHub."

### 2. What problem does it solve?
Manual, repetitive reminders (class, payment, meeting, webinar) are slow and error-prone. Automation makes them consistent, timely and auditable.

### 3. Why dry-run mode?
Emailing real people during development is risky. Dry-run runs the entire pipeline (validation, templating, scheduling) but skips only the final SMTP call. It is the default, and `--live` requires explicit confirmation.

### 4. How does personalisation work?
Templates use `$name`, `$title` etc. For each reminder I build a context dictionary from the contact and reminder rows and call `string.Template.substitute`. A missing placeholder raises `KeyError`, which is caught and logged as a failure rather than sending a broken email.

### 5. How does scheduling work, and how do you avoid duplicates?
For each reminder I compute its latest occurrence ≤ now (start time for one-offs; start + n×interval for daily/weekly). Each occurrence has an idempotency key, `reminder_id@timestamp`. Processed keys are stored in memory (and in a ledger file in live mode), so a rerun never resends.

### 6. What is SMTP and how did you use it?
Simple Mail Transfer Protocol is how mail is submitted to a server. I used `smtplib` with SSL (port 465) or STARTTLS (587), authenticated with a Gmail App Password, and built messages with `email.message.EmailMessage`.

### 7. How did you handle errors?
Per-reminder try/except so one bad row never stops the batch. Handled: invalid email, unknown contact, missing template/placeholder, SMTP auth failure (no retry), and network errors (2 retries). Failures go to `failed_emails.log` and the report.

### 8. How did you keep secrets safe?
Environment variables via `.env` (git-ignored), a committed `.env.example`, App Password instead of the real password, and I checked `git status` before pushing.

### 9. How would you scale or improve it?
Move CSV → database (SQLite/Postgres), use APScheduler with RRULE for complex recurrence, add FastAPI + dashboard, a queue/worker with retries, HTML templates (Jinja2), timezone-per-contact sending, open/click tracking, SPF/DKIM via a provider like SendGrid, Docker deployment.

### 10. How would you explain it to a non-technical person?
"It's like a smart assistant that automatically sends reminder emails at the right time, personalised for each person, and keeps a diary of what it sent, so nobody has to remember to do it manually."

---
**HR-friendly summary:** Self-initiated project showing problem-solving, attention to security and reliability, and the discipline of documenting and shipping work on GitHub.
**Technical summary:** Modular Python CLI: pandas ingestion → `string.Template` rendering → rule-based scheduler with idempotency keys → `smtplib` sender with retries and dry-run → structured logging and CSV reporting, with unit tests.

## Honest tips
Be ready to say what you'd do differently (database, proper timezone handling, a retry queue). Naive local datetimes are a known simplification here. Know every line of the code; run it live in the interview if asked.

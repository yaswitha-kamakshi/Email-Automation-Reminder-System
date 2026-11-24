# Virtual Simulation & How to Run

## Safe simulation approach
| Need | How |
|---|---|
| Dummy contacts | `python main.py --generate-sample-data` creates 7 contacts at `@example.com` (a reserved domain that can never receive mail), including one **invalid email** and one **unsubscribed** contact |
| Sample reminders | Same command creates 10 reminders: past, future (+10s, +20s), daily, weekly, one with a **missing template** |
| Templates | Edit `templates/*.txt` (first line `Subject:`, then `---`, then body) |
| Dry-run | Default behaviour. Builds the full email but sends nothing |
| Logs / reports | Auto-created in `logs/` and `outputs/` |

**In a real company** the CSVs would be a CRM/HR database, the loop would run as a service (cron, Windows Task Scheduler, Docker, cloud function), and sending would go through SendGrid/SES with domain authentication (SPF/DKIM). The logic is the same.

## Commands
```bash
python main.py --generate-sample-data   # create dummy data (times are relative to "now")
python main.py                          # DRY-RUN: process everything due now
python main.py --watch --duration 40    # DRY-RUN scheduler loop, checks every 5s for 40s
python main.py --live                   # REAL sending (needs .env, asks for YES)
python -m unittest discover -s tests    # run tests
```
Re-run `--generate-sample-data` before each demo so the "+10s/+20s" reminders are fresh.

## Expected dry-run output
```
INFO    | Starting in DRY-RUN mode
INFO    | Loaded 7 contacts from contacts.csv
INFO    | Loaded 10 reminders from reminders.csv
INFO    | DRY-RUN R001 -> aarav.demo@example.com | Reminder: Python Class
INFO    | SKIPPED kiran.demo@example.com (unsubscribed)
ERROR   | FAILED  R006 -> meera.invalid-email | ValueError: Invalid email address "meera.invalid-email"
ERROR   | FAILED  R007 -> vikram.demo@example.com | FileNotFoundError: Template not found: no_such_template.txt
INFO    | DRY-RUN R009 -> rohan.demo@example.com | Starting soon: Webinar...   (appears ~10s later in --watch)
==== SUMMARY (DRY-RUN): Total 10 | dry_run 7 | failed 2 | skipped 1 ====
```

## Running in live mode (optional, only to yourself)
1. Create a Gmail App Password; copy `.env.example` → `.env`; fill it in.
2. Edit `data/contacts.csv` so a few contacts use **your own** addresses.
3. `python main.py --live` → type `YES`. Successful sends go to `outputs/sent_ledger.csv` so a rerun never duplicates them.
Generated files: `logs/app.log`, `logs/sent_emails.log`, `logs/failed_emails.log`, `outputs/report_<timestamp>.csv` (columns: timestamp, reminder_id, contact_name, email, subject, status, error).

## Screenshots to capture
Save into `images/` with these names:
1. `project_structure.png`: folder tree in VS Code
2. `contacts_csv.png`: contacts file
3. `email_template.png`: a template file
4. `dry_run_output.png`: terminal after `python main.py`
5. `watch_mode.png`: reminders firing in `--watch`
6. `logs.png`: `sent_emails.log` + `failed_emails.log`
7. `report_csv.png`: report opened in Excel/VS Code
8. `github_repo.png`: your repo page

## Upload to GitHub ✅ / never upload ❌
✅ code, dummy CSVs, templates, sample logs/reports from **dry runs**, screenshots, `.env.example`
❌ `.env`, passwords, App Passwords, real people's emails/phone numbers, live-mode logs/reports containing real addresses, `sent_ledger.csv` from real sends, screenshots showing your inbox or credentials (blur them)

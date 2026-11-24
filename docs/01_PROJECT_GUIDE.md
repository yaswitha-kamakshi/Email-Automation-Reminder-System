# 1. Project Guide: Explanation, Tech Stack, Architecture, Phases, Install

## 1.1 What is an Email Automation & Reminder System?
**Simple:** A program that sends the right email to the right person at the right time, automatically, and keeps a record of what was sent.
Like setting alarms, except the alarm writes and sends an email for you.

**Technical:** A pipeline that ingests structured data (contacts, reminders), merges it with templates, evaluates schedule rules (one-off / recurrence) against the current time, delivers messages through SMTP (or an email API), and persists status (sent / failed / skipped) in logs and reports. Good systems are idempotent (never double-send), observable (logs and metrics) and safe (unsubscribe, rate limits, secret handling).

## 1.2 Problem it solves
Repetitive manual communication causes missed deadlines, inconsistent wording, no-shows, late payments and no audit trail.

## 1.3 Who uses it and how
| Team | Use cases |
|---|---|
| Companies / Ops | Meeting alerts, task notifications, SLA nudges |
| Trainers / Educators | Class reminders, assignment deadlines, webinar links |
| HR | Interview schedules, onboarding steps, policy acknowledgements |
| Sales | Follow-up sequences, demo reminders |
| Finance | Invoice and payment-due reminders |

Real companies usually run this through tools (Mailchimp, HubSpot, SendGrid, Outlook rules) or in-house services built on a database + job scheduler + email API. This project mirrors the same building blocks at student scale.

## 1.4 How Python automates it
CSV/DB reading (pandas) → string templating → `datetime` rule evaluation → `smtplib` sending → `logging` + CSV reports. A loop (or cron / Task Scheduler / APScheduler) runs it continuously.

## 1.5 Workflow
```
contact list → message template → scheduled reminder → email sending → status tracking → report generation
```

## 2. Tech stack options
| | Option A: Easy | Option B: Intermediate ⭐ (implemented) | Option C: Advanced |
|---|---|---|---|
| Tools | Python, csv, smtplib, `time.sleep` | Python, pandas, smtplib + email.message, datetime scheduler (or `schedule`), logging, argparse, dotenv | FastAPI, SQLAlchemy + SQLite/Postgres, APScheduler, Jinja2, aiosmtplib/SendGrid, Next.js or Streamlit dashboard, Docker |
| Difficulty | ⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| Output | Prints + one email | Dry-run, logs, CSV report, recurring reminders | REST API, DB history, web dashboard, open/click tracking |
| Time | 1 day | 4-6 days | 3-4 weeks |

**Best for students: Option B.** It is fully runnable offline, shows professional habits (modularity, logging, safety, testing), and the architecture upgrades naturally to Option C. The provided project PDF describes Option C. See "Upgrade path" at the bottom.

## 3. Architecture
```
 INPUT                         PROCESSING                                  OUTPUT
┌──────────────┐        ┌──────────────────────────────────────────┐   ┌─────────────────────┐
│contacts.csv  │──┐     │ data_loader  → validate rows             │   │ logs/app.log        │
│reminders.csv │──┼────▶│ scheduler    → which reminders are due?  │──▶│ logs/sent_emails    │
│templates/*.txt──┘     │ template_engine → personalise subject/body│   │ logs/failed_emails  │
│.env (SMTP)   │        │ mailer       → SMTP send / dry-run        │   │ outputs/report_*.csv│
└──────────────┘        │ engine       → orchestrates + tracks      │   │ console summary     │
                        └──────────────────────────────────────────┘   └─────────────────────┘
```
**Data flow:** `main.py` loads CSVs → every tick, `scheduler.find_due()` compares `send_at` with `now` and skips keys already processed → `engine` validates the contact, renders the template, calls `mailer.send()` → each result is logged and collected → `reporter` writes the CSV and summary.

## 4. Implementation plan (10 phases)
| # | Phase | What / why | Expected output | Beginner mistakes |
|---|---|---|---|---|
| 1 | Setup | Install Python, VS Code, Git; create venv. Isolates dependencies. | `python --version` works | Forgetting to activate venv |
| 2 | Folder creation | Create the structure so code, data and outputs stay separate. | Folders + `.gitignore` | Putting everything in one file |
| 3 | Contact CSV | Dummy contacts (incl. invalid + unsubscribed). Test edge cases safely. | `data/contacts.csv` | Using real people's emails |
| 4 | Templates | `$name`-style placeholders. Separate content from code. | `templates/*.txt` | Typos in placeholder names |
| 5 | SMTP config | Credentials in `.env`. Keeps secrets out of Git. | `.env` (local only) | Hard-coding passwords; using normal Gmail password instead of App Password |
| 6 | Personalisation | `string.Template.substitute` per contact. | Customised subject/body | Missing variable → KeyError (we catch it and log) |
| 7 | Scheduling | Compare `send_at` vs now; support daily/weekly. | Due reminders list | Mixing timezones; re-sending every loop |
| 8 | Sending | `smtplib` + retries + dry-run. | Sent/dry-run status | Testing live first; no timeout |
| 9 | Logging & report | `logging` + pandas CSV. Auditability. | `logs/`, `outputs/report_*.csv` | Printing instead of logging |
| 10 | GitHub upload | Commit, push, README, screenshots. Proof of work. | Public repo | Committing `.env` |

## 5. Folder structure explained
- `data/`: input CSVs. `templates/`: email text with placeholders. `src/`: modules (one job each). `outputs/`: reports. `logs/`: run history. `images/`: screenshots for README. `docs/`: guides. `tests/`: unit tests. `main.py`: CLI entry. `requirements.txt`: dependencies. `.gitignore`: files Git must ignore. `.env.example`: safe config template.

## 6. Installation
1. Install Python 3.9+ from python.org (Windows: tick **Add Python to PATH**). Check: `python --version` (Windows) / `python3 --version` (Mac).
2. Create and activate a virtual environment:
   - Windows: `python -m venv venv` then `venv\Scripts\activate`
   - Mac/Linux: `python3 -m venv venv` then `source venv/bin/activate`
3. `pip install -r requirements.txt` (pandas, python-dotenv)
4. Optional: `pip install schedule` if you want to try the `schedule` library as an alternative to the built-in loop in `src/scheduler.py`.

## Upgrade path to Option C (from the project PDF)
Replace CSV with SQLite tables (contacts, templates, campaigns, reminders, messages), swap `scheduler.find_due` for APScheduler + RRULE (`python-dateutil`), wrap with FastAPI endpoints, render HTML with Jinja2 + Markdown, and add a Next.js/Streamlit dashboard. Our module split (`data_loader`, `scheduler`, `mailer`, `engine`) maps one-to-one to the PDF's `models/scheduler/mailer/renderer`.

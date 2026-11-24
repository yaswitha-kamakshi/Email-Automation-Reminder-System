# GitHub Upload & Proof-Building Plan

## Repository details
- **Name:** `Email-Automation-Reminder-System`
- **Description:** Python automation system that schedules, personalises and sends reminder emails via SMTP with dry-run mode, logging and CSV reporting.
- **Topics:** `python` `automation` `email-automation` `smtp` `pandas` `scheduler` `reminder-system` `csv` `logging` `portfolio-project`

## Steps
1. github.com → **New repository** → name above → Public → **don't** add README (you already have one) → Create.
2. In your project folder:
```bash
git init
git add .
git status            # CHECK: .env must NOT appear in the list
git commit -m "feat: initial project structure and sample data"
git branch -M main
git remote add origin https://github.com/<your-username>/Email-Automation-Reminder-System.git
git push -u origin main
```
3. Later updates: `git add . && git commit -m "message" && git push`.
4. Add screenshots into `images/`, commit, push. They show in the README automatically.

### Security rules
- Never commit passwords. Use `.env` locally and `.env.example` in the repo.
- `.gitignore` already excludes `.env`, `venv/`, `__pycache__/`.
- If you ever commit a secret by mistake: **revoke the App Password immediately**. Deleting the file in a later commit does not remove it from history.

## Day-wise proof plan
| Day | Work | Commit message(s) | Screenshots |
|---|---|---|---|
| 1 | Setup, venv, folders, `.gitignore`, `requirements.txt`, `.env.example` | `chore: project scaffold and gitignore` | `project_structure.png` |
| 2 | Contact/reminder CSVs, 4 templates, `generate_sample_data.py` | `feat: add sample data and email templates` | `contacts_csv.png`, `email_template.png` |
| 3 | `data_loader.py`, `template_engine.py`, personalisation, `mailer.py` with dry-run | `feat: CSV loading, template personalisation, dry-run mailer` | `dry_run_output.png` |
| 4 | `scheduler.py` (one-off/daily/weekly), `engine.py`, `--watch` mode | `feat: reminder scheduling and watch loop` | `watch_mode.png` |
| 5 | Logging, `reporter.py`, error handling, tests | `feat: logging, CSV report, unit tests` | `logs.png`, `report_csv.png` |
| 6 | README, docs, final cleanup, push; pin repo on your profile | `docs: add README, guides and screenshots` | `github_repo.png` |

Tip: commit once per day (not one giant upload). The commit graph is part of your proof of work.

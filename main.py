"""Email Automation & Reminder System - entry point.

Examples:
  python main.py --generate-sample-data      # create dummy CSVs
  python main.py                             # DRY-RUN (safe, default): process everything due now
  python main.py --watch --duration 40       # DRY-RUN scheduler loop for 40 seconds
  python main.py --live                      # REAL emails (needs .env with SMTP credentials)
"""
import argparse
import csv
import sys
import time
from datetime import datetime

from src import config
from src.logger_setup import setup_logging
from src.data_loader import load_contacts, load_reminders
from src.mailer import EmailSender
from src.engine import run_cycle
from src.reporter import write_report, print_summary


def load_ledger() -> set:
    if config.LEDGER_CSV.exists():
        with open(config.LEDGER_CSV, newline="", encoding="utf-8") as f:
            return {row[0] for row in csv.reader(f) if row}
    return set()


def append_ledger(keys):
    config.OUTPUTS_DIR.mkdir(exist_ok=True)
    with open(config.LEDGER_CSV, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows([[k] for k in keys])


def parse_args():
    p = argparse.ArgumentParser(description="Email Automation & Reminder System")
    p.add_argument("--live", action="store_true", help="Send REAL emails (default is dry-run)")
    p.add_argument("--dry-run", action="store_true", help="Simulate only (this is already the default)")
    p.add_argument("--watch", action="store_true", help="Keep running and check for due reminders repeatedly")
    p.add_argument("--interval", type=int, default=5, help="Seconds between checks in --watch mode")
    p.add_argument("--duration", type=int, default=0, help="Stop --watch after N seconds (0 = run until Ctrl+C)")
    p.add_argument("--generate-sample-data", action="store_true", help="Create dummy contacts/reminders and exit")
    return p.parse_args()


def main():
    args = parse_args()
    if args.live and args.dry_run:
        sys.exit("Choose either --live or --dry-run, not both.")

    if args.generate_sample_data:
        from src.generate_sample_data import main as gen
        gen()
        return

    dry_run = not args.live
    mode = "DRY-RUN" if dry_run else "LIVE"
    app, sent_log, failed_log = setup_logging()
    loggers = (app, sent_log, failed_log)
    app.info("Starting in %s mode", mode)

    try:
        contacts = load_contacts(config.CONTACTS_CSV)
        reminders = load_reminders(config.REMINDERS_CSV)
    except FileNotFoundError as e:
        sys.exit(f"{e}\nTip: run  python main.py --generate-sample-data  first.")

    sender = EmailSender(config.get_smtp_settings(), dry_run=dry_run)
    try:
        sender.check_credentials()
    except RuntimeError as e:
        sys.exit(str(e))

    if not dry_run:
        if input("LIVE mode will send real emails. Type YES to continue: ").strip() != "YES":
            sys.exit("Cancelled.")
        done = load_ledger()
    else:
        done = set()
    already_done = set(done)

    all_results = []
    start = time.time()
    try:
        while True:
            cycle = run_cycle(datetime.now(), contacts, reminders, sender, done, loggers,
                              pause=0 if dry_run else 1.0)
            all_results.extend(cycle)
            if not args.watch:
                break
            if args.duration and time.time() - start >= args.duration:
                break
            time.sleep(args.interval)
    except KeyboardInterrupt:
        app.info("Stopped by user (Ctrl+C)")

    if not dry_run:  # remember successful real sends so a rerun never duplicates them
        append_ledger([r["_key"] for r in all_results if r["status"] == "sent" and r["_key"] not in already_done])

    for r in all_results:
        r.pop("_key", None)
    path, df = write_report(all_results)
    print_summary(df, path, mode)


if __name__ == "__main__":
    main()

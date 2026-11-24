"""Streamlit dashboard for the Email Automation & Reminder System.

Run with:  streamlit run dashboard.py
Shows run reports, status charts, failed emails, contacts, reminders and logs.
The sidebar button runs a safe DRY-RUN (never sends real email).
"""
from datetime import datetime

import pandas as pd
import streamlit as st

from src import config
from src.data_loader import load_contacts, load_reminders
from src.engine import run_cycle
from src.logger_setup import setup_logging
from src.mailer import EmailSender
from src.reporter import write_report

st.set_page_config(page_title="Email Automation Dashboard", page_icon="📧", layout="wide")
st.title("📧 Email Automation & Reminder Dashboard")
st.caption("Monitor reminder runs, failures and logs. Dry-run only: no real emails are sent from here.")


def list_reports():
    return sorted(config.OUTPUTS_DIR.glob("report_*.csv"), reverse=True)


def run_dry_run():
    """Run one dry-run cycle and save a new report."""
    loggers = setup_logging()
    contacts = load_contacts(config.CONTACTS_CSV)
    reminders = load_reminders(config.REMINDERS_CSV)
    sender = EmailSender(config.get_smtp_settings(), dry_run=True)
    results = run_cycle(datetime.now(), contacts, reminders, sender, set(), loggers)
    for r in results:
        r.pop("_key", None)
    path, _ = write_report(results)
    return path


# ---------------- Sidebar ----------------
st.sidebar.header("Controls")
if st.sidebar.button("▶ Run dry-run now", use_container_width=True):
    try:
        new_path = run_dry_run()
        st.sidebar.success(f"Created {new_path.name}")
        st.rerun()
    except FileNotFoundError:
        st.sidebar.error("CSV files missing. Run: python main.py --generate-sample-data")

reports = list_reports()
if st.sidebar.button("🔄 Refresh", use_container_width=True):
    st.rerun()

tab_reports, tab_contacts, tab_reminders, tab_logs = st.tabs(["📊 Reports", "👥 Contacts", "⏰ Reminders", "📜 Logs"])

# ---------------- Reports tab ----------------
with tab_reports:
    if not reports:
        st.info("No reports yet. Click **Run dry-run now** in the sidebar.")
    else:
        choice = st.selectbox("Select report", [p.name for p in reports])
        df = pd.read_csv(config.OUTPUTS_DIR / choice).fillna("")

        total = len(df)
        counts = df["status"].value_counts() if total else pd.Series(dtype=int)
        ok = int(counts.get("sent", 0) + counts.get("dry_run", 0))
        failed = int(counts.get("failed", 0))
        skipped = int(counts.get("skipped", 0))

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total", total)
        c2.metric("Sent / simulated", ok)
        c3.metric("Failed", failed)
        c4.metric("Skipped", skipped)
        c5.metric("Success rate", f"{(ok / total * 100):.0f}%" if total else "0%")

        left, right = st.columns([1, 2])
        with left:
            st.subheader("Status breakdown")
            if total:
                st.bar_chart(counts)
        with right:
            st.subheader("Filter results")
            statuses = st.multiselect("Status", sorted(df["status"].unique()), default=sorted(df["status"].unique()))
            search = st.text_input("Search email / name / subject")
            view = df[df["status"].isin(statuses)]
            if search:
                mask = view.apply(lambda row: search.lower() in " ".join(map(str, row.values)).lower(), axis=1)
                view = view[mask]
            st.dataframe(view, use_container_width=True, hide_index=True)
            st.download_button("⬇ Download this report (CSV)", df.to_csv(index=False), file_name=choice, mime="text/csv")

        st.subheader("❌ Failed emails and reasons")
        failed_df = df[df["status"] == "failed"][["reminder_id", "contact_name", "email", "error"]]
        if failed_df.empty:
            st.success("No failures in this report.")
        else:
            st.dataframe(failed_df, use_container_width=True, hide_index=True)

# ---------------- Contacts tab ----------------
with tab_contacts:
    if config.CONTACTS_CSV.exists():
        st.dataframe(pd.read_csv(config.CONTACTS_CSV), use_container_width=True, hide_index=True)
    else:
        st.info("contacts.csv not found. Run: python main.py --generate-sample-data")

# ---------------- Reminders tab ----------------
with tab_reminders:
    if config.REMINDERS_CSV.exists():
        rem = pd.read_csv(config.REMINDERS_CSV)
        rem["send_at"] = pd.to_datetime(rem["send_at"], errors="coerce")
        now = datetime.now()
        rem["state"] = rem["send_at"].apply(lambda t: "upcoming" if pd.notna(t) and t > now else "due / past")
        st.dataframe(rem.sort_values("send_at"), use_container_width=True, hide_index=True)
    else:
        st.info("reminders.csv not found. Run: python main.py --generate-sample-data")

# ---------------- Logs tab ----------------
with tab_logs:
    log_name = st.radio("Log file", ["app.log", "sent_emails.log", "failed_emails.log"], horizontal=True)
    log_path = config.LOGS_DIR / log_name
    if log_path.exists():
        lines = log_path.read_text(encoding="utf-8").splitlines()[-100:]
        st.code("\n".join(lines) or "(empty)", language="text")
    else:
        st.info("No log yet. Run the system once.")
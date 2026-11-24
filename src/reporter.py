"""Create the CSV report and print a summary."""
from datetime import datetime
import pandas as pd
from .config import OUTPUTS_DIR

COLUMNS = ["timestamp", "reminder_id", "contact_name", "email", "subject", "status", "error"]


def write_report(results: list):
    OUTPUTS_DIR.mkdir(exist_ok=True)
    df = pd.DataFrame(results, columns=COLUMNS) if results else pd.DataFrame(columns=COLUMNS)
    path = OUTPUTS_DIR / f"report_{datetime.now():%Y%m%d_%H%M%S}.csv"
    df.to_csv(path, index=False)
    return path, df


def print_summary(df: pd.DataFrame, path, mode: str):
    counts = df["status"].value_counts().to_dict() if len(df) else {}
    print("\n" + "=" * 52)
    print(f" SUMMARY ({mode})")
    print("=" * 52)
    print(f" Total processed : {len(df)}")
    for status in ("sent", "dry_run", "failed", "skipped"):
        print(f" {status:<15} : {counts.get(status, 0)}")
    print(f" Report saved to : {path}")
    print("=" * 52)

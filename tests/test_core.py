import sys, unittest
from datetime import datetime, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_loader import is_valid_email
from src.template_engine import render
from src.scheduler import latest_occurrence, find_due


class CoreTests(unittest.TestCase):
    def test_email_validation(self):
        self.assertTrue(is_valid_email("a@b.com"))
        self.assertFalse(is_valid_email("not-an-email"))

    def test_render_fills_placeholders(self):
        s, b = render("Hi $name", "Bye $name", {"name": "Asha"})
        self.assertEqual((s, b), ("Hi Asha", "Bye Asha"))

    def test_render_missing_variable_raises(self):
        with self.assertRaises(KeyError):
            render("Hi $name", "x", {})

    def test_future_reminder_not_due(self):
        now = datetime(2026, 1, 1, 12)
        r = {"reminder_id": "R", "send_at": now + timedelta(hours=1), "repeat": "none"}
        self.assertIsNone(latest_occurrence(r, now))

    def test_daily_repeat_picks_latest(self):
        now = datetime(2026, 1, 10, 12)
        r = {"reminder_id": "R", "send_at": datetime(2026, 1, 7, 9), "repeat": "daily"}
        self.assertEqual(latest_occurrence(r, now), datetime(2026, 1, 10, 9))

    def test_done_keys_prevent_duplicates(self):
        now = datetime(2026, 1, 1, 12)
        r = {"reminder_id": "R", "send_at": now - timedelta(hours=1), "repeat": "none"}
        due = find_due([r], now, set())
        self.assertEqual(len(due), 1)
        self.assertEqual(find_due([r], now, {due[0][2]}), [])


if __name__ == "__main__":
    unittest.main()

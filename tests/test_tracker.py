"""Tests for learning tracker module."""

import json
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from ai_daily.tracker import LearningTracker, LearningEntry


class TestLearningTracker(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.tracker = LearningTracker(data_dir=Path(self.tmpdir))

    def test_log_today_creates_entry(self):
        entry = self.tracker.log_today(
            articles=["Test Article"], notes="Learned about AI", minutes=10
        )
        self.assertEqual(entry.date, date.today().isoformat())
        self.assertEqual(entry.articles_read, ["Test Article"])
        self.assertEqual(entry.minutes_spent, 10)

    def test_log_today_accumulates(self):
        self.tracker.log_today(articles=["Article 1"], minutes=5)
        entry = self.tracker.log_today(articles=["Article 2"], minutes=10)
        self.assertEqual(len(entry.articles_read), 2)
        self.assertEqual(entry.minutes_spent, 15)

    def test_persistence(self):
        self.tracker.log_today(articles=["Test"], minutes=5)
        # Create new tracker instance pointing to same dir
        tracker2 = LearningTracker(data_dir=Path(self.tmpdir))
        entry = tracker2.get_entry(date.today())
        self.assertIsNotNone(entry)
        self.assertEqual(entry.articles_read, ["Test"])

    def test_streak_no_entries(self):
        self.assertEqual(self.tracker.calculate_streak(), 0)

    def test_streak_today_only(self):
        self.tracker.log_today(minutes=5)
        self.assertEqual(self.tracker.calculate_streak(), 1)

    def test_streak_consecutive_days(self):
        today = date.today()
        for i in range(5):
            d = today - timedelta(days=i)
            self.tracker.entries[d.isoformat()] = LearningEntry(
                date=d.isoformat(), articles_read=[], minutes_spent=5
            )
        self.tracker._save()
        self.assertEqual(self.tracker.calculate_streak(), 5)

    def test_streak_broken(self):
        today = date.today()
        # Log today and yesterday, skip day before
        self.tracker.entries[today.isoformat()] = LearningEntry(
            date=today.isoformat(), articles_read=[], minutes_spent=5
        )
        self.tracker.entries[(today - timedelta(days=1)).isoformat()] = LearningEntry(
            date=(today - timedelta(days=1)).isoformat(),
            articles_read=[],
            minutes_spent=5,
        )
        # Skip day -2, add day -3
        self.tracker.entries[(today - timedelta(days=3)).isoformat()] = LearningEntry(
            date=(today - timedelta(days=3)).isoformat(),
            articles_read=[],
            minutes_spent=5,
        )
        self.assertEqual(self.tracker.calculate_streak(), 2)

    def test_longest_streak(self):
        today = date.today()
        # Old 5-day streak
        for i in range(20, 15, -1):
            d = today - timedelta(days=i)
            self.tracker.entries[d.isoformat()] = LearningEntry(
                date=d.isoformat(), articles_read=[], minutes_spent=5
            )
        # Current 2-day streak
        for i in range(2):
            d = today - timedelta(days=i)
            self.tracker.entries[d.isoformat()] = LearningEntry(
                date=d.isoformat(), articles_read=[], minutes_spent=5
            )
        self.tracker._save()
        self.assertEqual(self.tracker.longest_streak(), 5)

    def test_stats(self):
        self.tracker.log_today(articles=["A1", "A2"], minutes=15)
        stats = self.tracker.stats()
        self.assertEqual(stats.total_days, 1)
        self.assertEqual(stats.total_articles, 2)
        self.assertEqual(stats.total_minutes, 15)

    def test_recent_entries(self):
        today = date.today()
        for i in range(3):
            d = today - timedelta(days=i)
            self.tracker.entries[d.isoformat()] = LearningEntry(
                date=d.isoformat(), articles_read=[f"art-{i}"], minutes_spent=5
            )
        self.tracker._save()
        recent = self.tracker.recent_entries(7)
        self.assertEqual(len(recent), 3)


if __name__ == "__main__":
    unittest.main()

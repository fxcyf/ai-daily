"""Tests for obsidian module."""

import tempfile
import unittest
from datetime import date
from pathlib import Path

from ai_daily.obsidian import write_daily_note


class TestWriteDailyNote(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def test_creates_file(self):
        target = date(2026, 4, 3)
        path = write_daily_note(self.tmpdir, "# Hello", target_date=target)

        self.assertTrue(path.exists())
        self.assertEqual(path.name, "2026-04-03.md")
        self.assertEqual(path.parent.name, "AI-Daily")

    def test_file_content_has_frontmatter(self):
        target = date(2026, 4, 3)
        path = write_daily_note(self.tmpdir, "# Content", target_date=target)
        content = path.read_text(encoding="utf-8")

        self.assertIn("date: 2026-04-03", content)
        self.assertIn("tags: [ai-daily]", content)
        self.assertIn("# Content", content)

    def test_creates_ai_daily_subdir(self):
        write_daily_note(self.tmpdir, "test", target_date=date(2026, 1, 1))
        self.assertTrue((Path(self.tmpdir) / "AI-Daily").is_dir())

    def test_overwrites_existing(self):
        target = date(2026, 4, 3)
        write_daily_note(self.tmpdir, "first", target_date=target)
        path = write_daily_note(self.tmpdir, "second", target_date=target)
        content = path.read_text(encoding="utf-8")
        self.assertIn("second", content)
        self.assertNotIn("first", content)

    def test_defaults_to_today(self):
        path = write_daily_note(self.tmpdir, "test")
        self.assertEqual(path.name, f"{date.today().isoformat()}.md")


if __name__ == "__main__":
    unittest.main()

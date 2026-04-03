"""Learning streak tracker — records daily learning and maintains streaks."""

import json
import os
from dataclasses import dataclass, asdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional


def _default_data_dir() -> Path:
    """Default data directory: ~/.ai-daily/"""
    return Path.home() / ".ai-daily"


@dataclass
class LearningEntry:
    """A single learning log entry."""

    date: str  # YYYY-MM-DD
    articles_read: list[str]  # list of article titles/URLs
    notes: str = ""
    minutes_spent: int = 0


@dataclass
class TrackerStats:
    """Summary statistics."""

    current_streak: int
    longest_streak: int
    total_days: int
    total_minutes: int
    total_articles: int


class LearningTracker:
    """Persistent learning tracker with streak counting."""

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or _default_data_dir()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.data_dir / "learning_log.json"
        self.entries: dict[str, LearningEntry] = {}
        self._load()

    def _load(self):
        """Load existing log from disk."""
        if self.log_file.exists():
            try:
                data = json.loads(self.log_file.read_text(encoding="utf-8"))
                for date_str, entry_data in data.items():
                    self.entries[date_str] = LearningEntry(**entry_data)
            except (json.JSONDecodeError, TypeError, KeyError):
                self.entries = {}

    def _save(self):
        """Persist log to disk."""
        data = {k: asdict(v) for k, v in self.entries.items()}
        self.log_file.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def log_today(
        self,
        articles: Optional[list[str]] = None,
        notes: str = "",
        minutes: int = 0,
    ) -> LearningEntry:
        """Log or update today's learning."""
        today = date.today().isoformat()

        if today in self.entries:
            entry = self.entries[today]
            if articles:
                entry.articles_read.extend(articles)
            if notes:
                entry.notes += ("\n" + notes) if entry.notes else notes
            entry.minutes_spent += minutes
        else:
            entry = LearningEntry(
                date=today,
                articles_read=articles or [],
                notes=notes,
                minutes_spent=minutes,
            )
            self.entries[today] = entry

        self._save()
        return entry

    def get_entry(self, target_date: date) -> Optional[LearningEntry]:
        """Get entry for a specific date."""
        return self.entries.get(target_date.isoformat())

    def calculate_streak(self) -> int:
        """Calculate current consecutive learning days (including today)."""
        if not self.entries:
            return 0

        today = date.today()
        streak = 0
        check_date = today

        while check_date.isoformat() in self.entries:
            streak += 1
            check_date -= timedelta(days=1)

        # If today not logged yet, check if yesterday was
        if streak == 0:
            check_date = today - timedelta(days=1)
            while check_date.isoformat() in self.entries:
                streak += 1
                check_date -= timedelta(days=1)

        return streak

    def longest_streak(self) -> int:
        """Calculate the longest streak ever."""
        if not self.entries:
            return 0

        dates = sorted(date.fromisoformat(d) for d in self.entries.keys())
        max_streak = 1
        current = 1

        for i in range(1, len(dates)):
            if (dates[i] - dates[i - 1]).days == 1:
                current += 1
                max_streak = max(max_streak, current)
            else:
                current = 1

        return max_streak

    def stats(self) -> TrackerStats:
        """Get overall learning statistics."""
        total_minutes = sum(e.minutes_spent for e in self.entries.values())
        total_articles = sum(len(e.articles_read) for e in self.entries.values())

        return TrackerStats(
            current_streak=self.calculate_streak(),
            longest_streak=self.longest_streak(),
            total_days=len(self.entries),
            total_minutes=total_minutes,
            total_articles=total_articles,
        )

    def recent_entries(self, days: int = 7) -> list[LearningEntry]:
        """Get entries from the last N days."""
        today = date.today()
        result = []
        for i in range(days):
            d = today - timedelta(days=i)
            entry = self.entries.get(d.isoformat())
            if entry:
                result.append(entry)
        return result

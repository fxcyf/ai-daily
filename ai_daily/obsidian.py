"""Obsidian vault integration — write daily digests as Markdown files."""

import subprocess
from datetime import date
from pathlib import Path
from typing import Optional


def write_daily_note(
    vault_path: str,
    content: str,
    target_date: Optional[date] = None,
) -> Path:
    """Write a daily digest note into the Obsidian vault.

    Args:
        vault_path: Path to the Obsidian vault root directory.
        content: Markdown content for the daily note.
        target_date: Date for the note (defaults to today).

    Returns:
        Path to the written file.
    """
    target_date = target_date or date.today()
    daily_dir = Path(vault_path) / "AI-Daily"
    daily_dir.mkdir(parents=True, exist_ok=True)

    date_str = target_date.isoformat()
    frontmatter = (
        f"---\n"
        f"date: {date_str}\n"
        f"tags: [ai-daily]\n"
        f"---\n\n"
    )

    file_path = daily_dir / f"{date_str}.md"
    file_path.write_text(frontmatter + content, encoding="utf-8")

    # Auto git commit+push if vault is a git repo
    _git_sync(daily_dir, file_path, date_str)

    return file_path


def _git_sync(directory: Path, file_path: Path, date_str: str) -> None:
    """If the vault is a git repo, commit and push the new file."""
    git_dir = directory
    while git_dir != git_dir.parent:
        if (git_dir / ".git").exists():
            break
        git_dir = git_dir.parent
    else:
        return  # Not a git repo

    try:
        subprocess.run(
            ["git", "add", str(file_path)],
            cwd=git_dir, capture_output=True, timeout=10,
        )
        subprocess.run(
            ["git", "commit", "-m", f"ai-daily: {date_str}"],
            cwd=git_dir, capture_output=True, timeout=10,
        )
        subprocess.run(
            ["git", "push"],
            cwd=git_dir, capture_output=True, timeout=30,
        )
    except (subprocess.TimeoutExpired, OSError):
        pass  # Best effort — don't fail if git operations fail

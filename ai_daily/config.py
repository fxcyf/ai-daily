"""Configuration management for ai-daily."""

import json
import os
from pathlib import Path
from typing import Optional


def _default_config_dir() -> Path:
    return Path.home() / ".ai-daily"


def load_config(config_dir: Optional[Path] = None) -> dict:
    """Load config from ~/.ai-daily/config.json, with env var overrides."""
    config_dir = config_dir or _default_config_dir()
    config_file = config_dir / "config.json"

    config = {}
    if config_file.exists():
        try:
            config = json.loads(config_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    # Env vars override file config
    if api_key := os.environ.get("ANTHROPIC_API_KEY"):
        config["anthropic_api_key"] = api_key
    if vault := os.environ.get("AI_DAILY_OBSIDIAN_VAULT"):
        config["obsidian_vault"] = vault

    return config


def save_config(config: dict, config_dir: Optional[Path] = None) -> None:
    """Save config to ~/.ai-daily/config.json."""
    config_dir = config_dir or _default_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "config.json"
    config_file.write_text(
        json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8"
    )

"""Tests for config module."""

import json
import os
import tempfile
import unittest
from pathlib import Path

from ai_daily.config import load_config, save_config


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.config_dir = Path(self.tmpdir)

    def test_load_empty(self):
        config = load_config(self.config_dir)
        self.assertEqual(config, {})

    def test_save_and_load(self):
        save_config({"anthropic_api_key": "sk-test", "obsidian_vault": "/tmp/vault"}, self.config_dir)
        config = load_config(self.config_dir)
        self.assertEqual(config["anthropic_api_key"], "sk-test")
        self.assertEqual(config["obsidian_vault"], "/tmp/vault")

    def test_env_var_override(self):
        save_config({"anthropic_api_key": "sk-file"}, self.config_dir)
        os.environ["ANTHROPIC_API_KEY"] = "sk-env"
        try:
            config = load_config(self.config_dir)
            self.assertEqual(config["anthropic_api_key"], "sk-env")
        finally:
            del os.environ["ANTHROPIC_API_KEY"]

    def test_load_corrupted_file(self):
        config_file = self.config_dir / "config.json"
        config_file.write_text("not json", encoding="utf-8")
        config = load_config(self.config_dir)
        self.assertEqual(config, {})


if __name__ == "__main__":
    unittest.main()

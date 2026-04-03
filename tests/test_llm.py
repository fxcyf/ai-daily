"""Tests for llm module."""

import unittest
from unittest.mock import patch, MagicMock

from ai_daily.feeds import Article
from ai_daily.llm import generate_digest


class TestGenerateDigest(unittest.TestCase):
    def test_empty_articles(self):
        result = generate_digest([], "sk-test")
        self.assertIn("暂无", result)

    @patch("ai_daily.llm.anthropic.Anthropic")
    def test_generates_digest(self, mock_cls):
        mock_client = MagicMock()
        mock_cls.return_value = mock_client

        text_block = MagicMock()
        text_block.type = "text"
        text_block.text = "# AI 日报\n\n今天的要点..."

        mock_response = MagicMock()
        mock_response.content = [text_block]
        mock_client.messages.create.return_value = mock_response

        articles = [
            Article(
                title="Test Article",
                url="https://example.com",
                source="Test",
                category="news",
                summary="Some summary",
            )
        ]

        result = generate_digest(articles, "sk-test")
        self.assertEqual(result, "# AI 日报\n\n今天的要点...")
        mock_client.messages.create.assert_called_once()

        call_kwargs = mock_client.messages.create.call_args[1]
        self.assertEqual(call_kwargs["model"], "claude-haiku-4-5")
        self.assertIn("Test Article", call_kwargs["messages"][0]["content"])

    @patch("ai_daily.llm.anthropic.Anthropic")
    def test_handles_no_text_block(self, mock_cls):
        mock_client = MagicMock()
        mock_cls.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = []
        mock_client.messages.create.return_value = mock_response

        articles = [
            Article(title="X", url="https://x.com", source="X", category="news")
        ]
        result = generate_digest(articles, "sk-test")
        self.assertIn("失败", result)


if __name__ == "__main__":
    unittest.main()

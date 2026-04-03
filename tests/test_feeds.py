"""Tests for feeds module."""

import unittest
from ai_daily.feeds import Article, score_relevance, _strip_html, _parse_date


class TestStripHtml(unittest.TestCase):
    def test_removes_tags(self):
        self.assertEqual(_strip_html("<p>Hello <b>world</b></p>"), "Hello world")

    def test_empty(self):
        self.assertEqual(_strip_html(""), "")

    def test_no_tags(self):
        self.assertEqual(_strip_html("plain text"), "plain text")


class TestParseDate(unittest.TestCase):
    def test_rfc822(self):
        d = _parse_date("Mon, 01 Jan 2024 12:00:00 +0000")
        self.assertIsNotNone(d)
        self.assertEqual(d.year, 2024)

    def test_iso(self):
        d = _parse_date("2024-06-15T08:30:00Z")
        self.assertIsNotNone(d)
        self.assertEqual(d.month, 6)

    def test_invalid(self):
        self.assertIsNone(_parse_date("not a date"))

    def test_empty(self):
        self.assertIsNone(_parse_date(""))


class TestScoreRelevance(unittest.TestCase):
    def test_high_score_for_ai_article(self):
        article = Article(
            title="New LLM Agent Framework for Autonomous AI",
            url="https://example.com",
            source="test",
            category="research",
            summary="A new multi-agent system using large language models and RAG.",
        )
        score = score_relevance(article)
        self.assertGreater(score, 5.0)

    def test_low_score_for_unrelated(self):
        article = Article(
            title="Best Recipes for Summer BBQ",
            url="https://example.com",
            source="test",
            category="news",
            summary="Top 10 grilling tips for your next cookout.",
        )
        score = score_relevance(article)
        self.assertEqual(score, 0.0)

    def test_medium_score(self):
        article = Article(
            title="Python 3.13 Released",
            url="https://example.com",
            source="test",
            category="news",
            summary="New release includes performance improvements for machine learning workloads.",
        )
        score = score_relevance(article)
        self.assertGreater(score, 0.0)


class TestArticle(unittest.TestCase):
    def test_reading_time(self):
        a = Article(
            title="test",
            url="https://example.com",
            source="test",
            category="test",
            summary=" ".join(["word"] * 400),
        )
        self.assertEqual(a.reading_time_min, 2)

    def test_reading_time_minimum(self):
        a = Article(
            title="test", url="https://example.com", source="test", category="test"
        )
        self.assertEqual(a.reading_time_min, 1)


if __name__ == "__main__":
    unittest.main()

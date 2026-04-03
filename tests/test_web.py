"""Tests for web interface."""

import unittest
from datetime import datetime, timezone

from ai_daily.feeds import Article
from ai_daily.web import _render_digest, _render_log, _render_stats, _page


class TestWebRendering(unittest.TestCase):
    def test_page_wrapper(self):
        html = _page("<p>test</p>", active="digest")
        self.assertIn("<p>test</p>", html)
        self.assertIn('class="active"', html)
        self.assertIn("viewport", html)

    def test_render_digest_empty(self):
        html = _render_digest([])
        self.assertIn("ai-daily", html)
        self.assertIn("请稍候刷新", html)

    def test_render_digest_with_articles(self):
        articles = [
            Article(
                title="Test LLM Article",
                url="https://example.com/1",
                source="TestSource",
                category="research",
                published=datetime(2024, 6, 1, tzinfo=timezone.utc),
                summary="A summary about agents.",
                relevance_score=5.0,
            )
        ]
        html = _render_digest(articles)
        self.assertIn("Test LLM Article", html)
        self.assertIn("research", html)
        self.assertIn("example.com", html)

    def test_render_log_form(self):
        html = _render_log()
        self.assertIn("<form", html)
        self.assertIn('name="title"', html)
        self.assertIn('name="notes"', html)
        self.assertIn('name="minutes"', html)

    def test_render_log_success(self):
        html = _render_log(success=True)
        self.assertIn("打卡成功", html)

    def test_render_stats(self):
        html = _render_stats()
        self.assertIn("当前连续", html)
        self.assertIn("最长连续", html)
        self.assertIn("累计文章", html)

    def test_xss_prevention(self):
        articles = [
            Article(
                title='<script>alert("xss")</script>',
                url="https://example.com",
                source="test",
                category="news",
                summary='<img onerror="alert(1)">',
                relevance_score=1.0,
            )
        ]
        rendered = _render_digest(articles)
        # Script tags must be escaped, not rendered as raw HTML
        self.assertNotIn("<script>", rendered)
        self.assertNotIn('<img onerror', rendered)
        # Escaped versions should be present
        self.assertIn("&lt;script&gt;", rendered)


if __name__ == "__main__":
    unittest.main()

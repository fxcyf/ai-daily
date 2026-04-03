"""RSS feed aggregation and AI-related filtering."""

import xml.etree.ElementTree as ET
import urllib.request
import urllib.error
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from email.utils import parsedate_to_datetime


# 默认RSS源配置
DEFAULT_FEEDS = [
    {
        "name": "Hacker News (Best)",
        "url": "https://hnrss.org/best?q=AI+OR+LLM+OR+GPT+OR+agent+OR+machine+learning+OR+Claude+OR+OpenAI+OR+Anthropic",
        "category": "community",
    },
    {
        "name": "ArXiv CS.AI",
        "url": "https://rss.arxiv.org/rss/cs.AI",
        "category": "research",
    },
    {
        "name": "ArXiv CS.CL (NLP)",
        "url": "https://rss.arxiv.org/rss/cs.CL",
        "category": "research",
    },
    {
        "name": "The Batch (Andrew Ng)",
        "url": "https://www.deeplearning.ai/the-batch/feed/",
        "category": "newsletter",
    },
    {
        "name": "MIT Tech Review - AI",
        "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed",
        "category": "news",
    },
    {
        "name": "OpenAI Blog",
        "url": "https://openai.com/blog/rss.xml",
        "category": "industry",
    },
    {
        "name": "Anthropic Research",
        "url": "https://www.anthropic.com/research/rss.xml",
        "category": "industry",
    },
    {
        "name": "Hugging Face Blog",
        "url": "https://huggingface.co/blog/feed.xml",
        "category": "tools",
    },
]

# AI 相关关键词（用于二次过滤）
AI_KEYWORDS = re.compile(
    r"\b("
    r"ai|artificial.intelligence|machine.learning|deep.learning|neural.net"
    r"|llm|large.language.model|gpt|claude|gemini|llama|mistral"
    r"|transformer|attention.mechanism|fine.tun|rlhf|rag"
    r"|agent|agentic|autonomous|multi.agent|tool.use"
    r"|diffusion|generative|gan|vae|stable.diffusion|midjourney|dall-e"
    r"|embedding|vector.database|prompt.engineer"
    r"|openai|anthropic|google.deepmind|meta.ai|hugging.face"
    r"|mlops|model.serving|inference|quantiz|distill"
    r"|computer.vision|nlp|natural.language|speech.recognition"
    r"|reinforcement.learning|reward.model"
    r"|mcp|model.context.protocol"
    r")\b",
    re.IGNORECASE,
)


@dataclass
class Article:
    """A single news article/paper."""

    title: str
    url: str
    source: str
    category: str
    published: Optional[datetime] = None
    summary: str = ""
    tags: list[str] = field(default_factory=list)
    relevance_score: float = 0.0

    @property
    def reading_time_min(self) -> int:
        """Estimated reading time in minutes."""
        word_count = len(self.summary.split()) if self.summary else 50
        return max(1, round(word_count / 200))


def _parse_date(date_str: str) -> Optional[datetime]:
    """Parse various date formats from RSS feeds."""
    if not date_str:
        return None
    try:
        return parsedate_to_datetime(date_str)
    except (ValueError, TypeError):
        pass
    # Try ISO format
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def _strip_html(text: str) -> str:
    """Remove HTML tags from text."""
    return re.sub(r"<[^>]+>", "", text).strip()


def fetch_feed(feed_config: dict, timeout: int = 15) -> list[Article]:
    """Fetch and parse a single RSS feed."""
    articles = []
    url = feed_config["url"]
    source = feed_config["name"]
    category = feed_config["category"]

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ai-daily/0.1"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
    except (urllib.error.URLError, OSError, TimeoutError):
        return articles

    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return articles

    # Handle both RSS 2.0 and Atom feeds
    ns = {"atom": "http://www.w3.org/2005/Atom"}

    # RSS 2.0
    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        desc = _strip_html(item.findtext("description") or "")
        pub_date = _parse_date(item.findtext("pubDate") or "")
        if title and link:
            articles.append(
                Article(
                    title=title,
                    url=link,
                    source=source,
                    category=category,
                    published=pub_date,
                    summary=desc[:500],
                )
            )

    # Atom
    for entry in root.findall(".//atom:entry", ns):
        title = (entry.findtext("atom:title", namespaces=ns) or "").strip()
        link_el = entry.find("atom:link", ns)
        link = link_el.get("href", "") if link_el is not None else ""
        summary_el = entry.findtext("atom:summary", namespaces=ns) or entry.findtext(
            "atom:content", namespaces=ns
        )
        desc = _strip_html(summary_el or "")
        pub_date = _parse_date(
            entry.findtext("atom:updated", namespaces=ns)
            or entry.findtext("atom:published", namespaces=ns)
            or ""
        )
        if title and link:
            articles.append(
                Article(
                    title=title,
                    url=link,
                    source=source,
                    category=category,
                    published=pub_date,
                    summary=desc[:500],
                )
            )

    return articles


def score_relevance(article: Article) -> float:
    """Score how relevant an article is to AI/ML/Agent topics."""
    text = f"{article.title} {article.summary}".lower()
    matches = AI_KEYWORDS.findall(text)
    # Unique keyword matches
    unique = set(m.lower() for m in matches)
    # Title matches are worth more
    title_matches = AI_KEYWORDS.findall(article.title.lower())
    title_unique = set(m.lower() for m in title_matches)

    score = len(unique) * 1.0 + len(title_unique) * 2.0

    # Boost for hot topics
    hot_topics = {"agent", "agentic", "llm", "rag", "mcp", "tool.use"}
    if hot_topics & unique:
        score *= 1.5

    return round(score, 1)


def fetch_all(
    feeds: Optional[list[dict]] = None,
    min_score: float = 1.0,
    max_articles: int = 20,
) -> list[Article]:
    """Fetch all feeds, filter, score, and return top articles."""
    if feeds is None:
        feeds = DEFAULT_FEEDS

    all_articles = []
    for feed_config in feeds:
        all_articles.extend(fetch_feed(feed_config))

    # Score and filter
    for article in all_articles:
        article.relevance_score = score_relevance(article)

    filtered = [a for a in all_articles if a.relevance_score >= min_score]

    # Deduplicate by URL
    seen_urls = set()
    unique = []
    for a in filtered:
        if a.url not in seen_urls:
            seen_urls.add(a.url)
            unique.append(a)

    # Sort by relevance, then recency
    unique.sort(key=lambda a: (a.relevance_score, a.published or datetime.min.replace(tzinfo=timezone.utc)), reverse=True)

    return unique[:max_articles]

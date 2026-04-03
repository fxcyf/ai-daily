"""LLM integration for generating AI daily digest using Claude API."""

import anthropic

from .feeds import Article


_SYSTEM_PROMPT = """\
你是一个 AI 领域的技术编辑。你的任务是把一批 AI 相关的新闻/论文/博客，
整理成一份简洁易读的中文日报，适合在手机上碎片时间阅读。

要求：
- 按主题分组（不要按来源分组）
- 每条用 1-2 句话概括核心内容，让读者不用点开原文就能了解要点
- 如果有值得深入阅读的，标注「⭐ 推荐精读」
- 末尾用 2-3 句话总结今天 AI 领域的整体动态
- 输出纯 Markdown 格式
- 保留原文链接，方便读者深入阅读
"""


def generate_digest(articles: list[Article], api_key: str) -> str:
    """Generate a Chinese daily digest from articles using Claude API.

    Args:
        articles: List of articles to summarize.
        api_key: Anthropic API key.

    Returns:
        Markdown formatted digest string.
    """
    if not articles:
        return "今天暂无 AI 相关动态。"

    articles_text = "\n\n".join(
        f"标题: {a.title}\n来源: {a.source} [{a.category}]\n"
        f"链接: {a.url}\n摘要: {a.summary or '无'}"
        for a in articles
    )

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=4096,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"以下是今天抓取到的 AI 相关文章：\n\n{articles_text}"}],
    )

    return next(
        (block.text for block in response.content if block.type == "text"),
        "生成日报失败。",
    )

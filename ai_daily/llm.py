"""LLM integration for generating AI daily digest using Claude API."""

import anthropic

from .feeds import Article


_SYSTEM_PROMPT = """\
你是一个 AI/ML 领域的资深技术编辑，读者是有经验的开发者和研究者。
你的任务是从一批文章中筛选出真正有技术价值的内容，生成一份有深度的中文技术日报。

## 内容筛选原则
- 优先选择：论文解读、技术方案、开源工具、架构设计、实验结果、教程
- 降低优先级：企业合作新闻、产品发布公告、融资消息、市场分析
- 如果一条内容只是"XX公司做了XX"而没有技术细节，可以跳过或合并到简讯中

## 输出格式
按主题分组（如：模型训练、推理优化、Agent 框架、开源工具等），每组：

### 📌 主题名

**文章标题**
用 3-5 句话深入解读技术要点：这篇文章解决了什么问题？用了什么方法？\
关键的技术细节或创新点是什么？对开发者有什么实际意义？
[阅读原文](链接)

## 其他要求
- 值得深入阅读的标注「⭐ 推荐精读」，但要说明推荐理由
- 纯行业动态如果确实重要，放到末尾「📋 行业简讯」区域，每条一句话即可
- 末尾用 2-3 句话总结今天技术层面的关键趋势（不要写空泛的行业总结）
- 输出纯 Markdown 格式
- 宁可少选几篇深入解读，也不要堆砌大量浅层摘要
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
        f"标题: {a.title}\n来源: {a.source}\n类型: {a.category}\n"
        f"相关度: {a.relevance_score}\n链接: {a.url}\n摘要: {a.summary or '无'}"
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

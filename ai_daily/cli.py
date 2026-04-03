"""CLI entry point for ai-daily."""

import argparse
import sys
import textwrap
from datetime import date, datetime, timezone

from .feeds import fetch_all, DEFAULT_FEEDS, Article
from .tracker import LearningTracker
from .config import load_config, save_config


# ── ANSI colors ──────────────────────────────────────────────────────
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
RESET = "\033[0m"

CATEGORY_COLORS = {
    "community": YELLOW,
    "research": CYAN,
    "newsletter": MAGENTA,
    "news": BLUE,
    "industry": GREEN,
    "tools": RED,
}


def _print_header():
    print(f"""
{BOLD}{CYAN}╔══════════════════════════════════════════╗
║        ai-daily · 每日AI动态追踪         ║
╚══════════════════════════════════════════╝{RESET}
""")


def _print_article(idx: int, article: Article):
    color = CATEGORY_COLORS.get(article.category, "")
    score_bar = "●" * min(int(article.relevance_score), 10)
    pub = ""
    if article.published:
        pub = article.published.strftime("%m-%d %H:%M")

    print(f"  {BOLD}{idx:>2}. {article.title}{RESET}")
    print(
        f"      {color}[{article.category}]{RESET}  "
        f"{DIM}{article.source}  {pub}  "
        f"~{article.reading_time_min}min  "
        f"相关度 {score_bar}{RESET}"
    )
    if article.summary:
        short = textwrap.shorten(article.summary, width=120, placeholder="...")
        print(f"      {DIM}{short}{RESET}")
    print(f"      {DIM}{article.url}{RESET}")
    print()


def cmd_digest(args):
    """Show today's AI digest."""
    _print_header()
    tracker = LearningTracker()
    stats = tracker.stats()

    # Streak display
    streak = stats.current_streak
    if streak > 0:
        flame = "🔥" * min(streak, 5)
        print(f"  {flame} 连续学习 {BOLD}{streak}{RESET} 天 | "
              f"累计 {stats.total_days} 天 | "
              f"已读 {stats.total_articles} 篇 | "
              f"投入 {stats.total_minutes} 分钟")
    else:
        print(f"  {YELLOW}今天还没有打卡哦！读完一篇文章后用 ai-daily log 记录{RESET}")
    print()

    print(f"  {BOLD}正在抓取最新AI动态...{RESET}\n")
    articles = fetch_all(max_articles=args.count)

    if not articles:
        print(f"  {YELLOW}暂未获取到文章，请检查网络连接{RESET}")
        return

    print(f"  {GREEN}找到 {len(articles)} 篇相关文章：{RESET}\n")
    for i, article in enumerate(articles, 1):
        _print_article(i, article)

    print(f"  {DIM}提示: 读完后用 ai-daily log -t \"文章标题\" -n \"学到了什么\" -m 分钟数 打卡{RESET}\n")


def cmd_log(args):
    """Log a learning entry."""
    tracker = LearningTracker()

    articles = []
    if args.title:
        articles = [args.title]

    entry = tracker.log_today(
        articles=articles,
        notes=args.notes or "",
        minutes=args.minutes,
    )

    stats = tracker.stats()
    streak = stats.current_streak

    print(f"\n  {GREEN}✓ 打卡成功！{RESET}\n")
    print(f"  日期: {entry.date}")
    print(f"  今日已读: {len(entry.articles_read)} 篇")
    print(f"  今日时间: {entry.minutes_spent} 分钟")
    if entry.notes:
        print(f"  笔记: {entry.notes}")
    print()

    flame = "🔥" * min(streak, 5) if streak > 0 else ""
    print(f"  {flame} 连续学习 {BOLD}{streak}{RESET} 天")
    if stats.longest_streak > streak:
        print(f"  最长记录: {stats.longest_streak} 天 — 继续加油！")
    elif streak >= 7:
        print(f"  {GREEN}太棒了！已经坚持一周以上！{RESET}")
    print()


def cmd_stats(args):
    """Show learning statistics."""
    tracker = LearningTracker()
    stats = tracker.stats()

    _print_header()
    print(f"  {BOLD}学习统计{RESET}\n")
    print(f"  🔥 当前连续: {BOLD}{stats.current_streak}{RESET} 天")
    print(f"  🏆 最长连续: {BOLD}{stats.longest_streak}{RESET} 天")
    print(f"  📅 累计天数: {stats.total_days} 天")
    print(f"  📖 累计文章: {stats.total_articles} 篇")
    print(f"  ⏱  累计时间: {stats.total_minutes} 分钟")
    print()

    # Recent 7 days
    recent = tracker.recent_entries(7)
    if recent:
        print(f"  {BOLD}最近 7 天:{RESET}\n")
        for entry in recent:
            check = f"{GREEN}✓{RESET}"
            articles_str = f"{len(entry.articles_read)} 篇" if entry.articles_read else "0 篇"
            print(
                f"    {check} {entry.date}  "
                f"{articles_str}  {entry.minutes_spent}min"
            )
            if entry.notes:
                short = textwrap.shorten(entry.notes, width=60, placeholder="...")
                print(f"      {DIM}{short}{RESET}")
        print()

    # Show empty days in last 7
    today = date.today()
    logged_dates = {e.date for e in recent}
    from datetime import timedelta
    for i in range(7):
        d = (today - timedelta(days=i)).isoformat()
        if d not in logged_dates:
            print(f"    {DIM}○ {d}  —{RESET}")


def cmd_sources(args):
    """List configured RSS sources."""
    _print_header()
    print(f"  {BOLD}RSS 订阅源:{RESET}\n")
    for feed in DEFAULT_FEEDS:
        color = CATEGORY_COLORS.get(feed["category"], "")
        print(f"    {color}[{feed['category']:>10}]{RESET}  {feed['name']}")
        print(f"                  {DIM}{feed['url']}{RESET}")
    print(f"\n  {DIM}共 {len(DEFAULT_FEEDS)} 个源，可在 feeds.py 中自定义{RESET}\n")


def cmd_generate(args):
    """Generate AI daily digest → Obsidian vault."""
    config = load_config()

    api_key = config.get("anthropic_api_key")
    vault_path = config.get("obsidian_vault")

    if not api_key:
        print(f"  {RED}错误: 未配置 API Key{RESET}")
        print(f"  运行: ai-daily config --api-key YOUR_KEY")
        print(f"  或设置环境变量: export ANTHROPIC_API_KEY=YOUR_KEY")
        return
    if not vault_path:
        print(f"  {RED}错误: 未配置 Obsidian vault 路径{RESET}")
        print(f"  运行: ai-daily config --vault /path/to/your/vault")
        return

    print(f"  {BOLD}正在抓取最新AI动态...{RESET}")
    articles = fetch_all(max_articles=args.count)

    if not articles:
        print(f"  {YELLOW}暂未获取到文章，请检查网络连接{RESET}")
        return

    print(f"  {GREEN}抓取到 {len(articles)} 篇文章，正在生成日报...{RESET}")

    from .llm import generate_digest
    digest = generate_digest(articles, api_key)

    from .obsidian import write_daily_note
    file_path = write_daily_note(vault_path, digest)

    print(f"\n  {GREEN}✓ 日报已生成！{RESET}")
    print(f"  文件: {file_path}")
    print(f"  打开 Obsidian 即可阅读\n")


def cmd_config(args):
    """Configure ai-daily settings."""
    config = load_config()
    changed = False

    if args.api_key:
        config["anthropic_api_key"] = args.api_key
        changed = True
        print(f"  {GREEN}✓ API Key 已保存{RESET}")

    if args.vault:
        from pathlib import Path
        vault = Path(args.vault).expanduser().resolve()
        if not vault.is_dir():
            print(f"  {RED}错误: 目录不存在: {vault}{RESET}")
            return
        config["obsidian_vault"] = str(vault)
        changed = True
        print(f"  {GREEN}✓ Obsidian vault 路径已保存: {vault}{RESET}")

    if changed:
        save_config(config)
    else:
        # Show current config
        print(f"\n  {BOLD}当前配置{RESET} (~/.ai-daily/config.json)\n")
        api_key = config.get("anthropic_api_key", "")
        if api_key:
            masked = api_key[:7] + "..." + api_key[-4:]
            print(f"  API Key:       {masked}")
        else:
            print(f"  API Key:       {DIM}未配置{RESET}")
        vault = config.get("obsidian_vault", "")
        print(f"  Obsidian vault: {vault or f'{DIM}未配置{RESET}'}")
        print()


def cmd_serve(args):
    """Start the web server for mobile access."""
    from .web import run_server
    run_server(host=args.host, port=args.port)


def main():
    parser = argparse.ArgumentParser(
        prog="ai-daily",
        description="每日AI动态追踪 + 微学习打卡工具",
    )
    subparsers = parser.add_subparsers(dest="command")

    # digest
    p_digest = subparsers.add_parser("digest", help="查看今日AI动态摘要")
    p_digest.add_argument("-c", "--count", type=int, default=15, help="显示文章数量")
    p_digest.set_defaults(func=cmd_digest)

    # log
    p_log = subparsers.add_parser("log", help="记录今天的学习")
    p_log.add_argument("-t", "--title", help="阅读的文章标题")
    p_log.add_argument("-n", "--notes", help="学习笔记")
    p_log.add_argument("-m", "--minutes", type=int, default=5, help="花费分钟数 (默认5)")
    p_log.set_defaults(func=cmd_log)

    # stats
    p_stats = subparsers.add_parser("stats", help="查看学习统计")
    p_stats.set_defaults(func=cmd_stats)

    # sources
    p_sources = subparsers.add_parser("sources", help="查看RSS订阅源")
    p_sources.set_defaults(func=cmd_sources)

    # generate
    p_gen = subparsers.add_parser("generate", help="生成AI日报 → Obsidian")
    p_gen.add_argument("-c", "--count", type=int, default=15, help="文章数量 (默认15)")
    p_gen.set_defaults(func=cmd_generate)

    # config
    p_cfg = subparsers.add_parser("config", help="配置 API Key 和 Obsidian 路径")
    p_cfg.add_argument("--api-key", help="Anthropic API Key")
    p_cfg.add_argument("--vault", help="Obsidian vault 路径")
    p_cfg.set_defaults(func=cmd_config)

    # serve
    p_serve = subparsers.add_parser("serve", help="启动 Web 界面（手机访问）")
    p_serve.add_argument("-p", "--port", type=int, default=8080, help="端口号 (默认8080)")
    p_serve.add_argument("--host", default="0.0.0.0", help="监听地址 (默认0.0.0.0)")
    p_serve.set_defaults(func=cmd_serve)

    args = parser.parse_args()
    if not args.command:
        # Default to digest
        args.count = 15
        cmd_digest(args)
    else:
        args.func(args)


if __name__ == "__main__":
    main()

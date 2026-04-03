"""CLI entry point for ai-daily."""

import argparse

from .feeds import fetch_all, DEFAULT_FEEDS
from .config import load_config, save_config


# ── ANSI colors ──────────────────────────────────────────────────────
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
RESET = "\033[0m"

CATEGORY_COLORS = {
    "community": YELLOW,
    "research": CYAN,
    "newsletter": "\033[35m",
    "news": "\033[34m",
    "industry": GREEN,
    "tools": RED,
}


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


def cmd_sources(args):
    """List configured RSS sources."""
    print(f"\n  {BOLD}RSS 订阅源:{RESET}\n")
    for feed in DEFAULT_FEEDS:
        color = CATEGORY_COLORS.get(feed["category"], "")
        print(f"    {color}[{feed['category']:>10}]{RESET}  {feed['name']}")
        print(f"                  {DIM}{feed['url']}{RESET}")
    print(f"\n  {DIM}共 {len(DEFAULT_FEEDS)} 个源，可在 feeds.py 中自定义{RESET}\n")


def main():
    parser = argparse.ArgumentParser(
        prog="ai-daily",
        description="每日AI日报生成 + Obsidian 联动",
    )
    subparsers = parser.add_subparsers(dest="command")

    # generate (default)
    p_gen = subparsers.add_parser("generate", help="生成AI日报 → Obsidian")
    p_gen.add_argument("-c", "--count", type=int, default=15, help="文章数量 (默认15)")
    p_gen.set_defaults(func=cmd_generate)

    # config
    p_cfg = subparsers.add_parser("config", help="配置 API Key 和 Obsidian 路径")
    p_cfg.add_argument("--api-key", help="Anthropic API Key")
    p_cfg.add_argument("--vault", help="Obsidian vault 路径")
    p_cfg.set_defaults(func=cmd_config)

    # sources
    p_sources = subparsers.add_parser("sources", help="查看RSS订阅源")
    p_sources.set_defaults(func=cmd_sources)

    args = parser.parse_args()
    if not args.command:
        # Default to generate
        args.count = 15
        cmd_generate(args)
    else:
        args.func(args)


if __name__ == "__main__":
    main()

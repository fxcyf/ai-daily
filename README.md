# ai-daily — 每日AI动态追踪 + 微学习打卡

一个零依赖的 Python CLI 工具，帮你每天花几分钟跟踪 AI/ML/Agent 领域最新动态，并养成持续学习的习惯。

## 功能

- **RSS 聚合** — 从 8 个高质量源（HN、ArXiv、MIT Tech Review、OpenAI、Anthropic 等）抓取最新内容
- **智能过滤** — 基于关键词匹配和相关度评分，只展示 AI 相关内容
- **学习打卡** — 记录每天读了什么、学了什么、花了多少时间
- **连续追踪** — 维护学习连续天数，激励你坚持每日学习
- **零外部依赖** — 仅使用 Python 标准库

## 安装

```bash
# 方式1: 直接运行
python -m ai_daily

# 方式2: 安装为命令行工具
pip install -e .
ai-daily
```

## 使用

### 查看今日AI动态

```bash
ai-daily digest          # 查看今日精选（默认15篇）
ai-daily digest -c 5     # 只看5篇
ai-daily                 # 等同于 ai-daily digest
```

### 学习打卡

```bash
ai-daily log -t "文章标题" -n "学到了什么" -m 10
# -t: 文章标题
# -n: 学习笔记
# -m: 花费分钟数（默认5分钟）
```

### 查看统计

```bash
ai-daily stats           # 连续天数、累计数据、最近7天
```

### 查看RSS源

```bash
ai-daily sources         # 列出所有订阅源
```

## 每日使用建议

1. 早上或午休时运行 `ai-daily digest`，浏览标题（2分钟）
2. 挑 1-2 篇感兴趣的点开看看（5-10分钟）
3. 看完后 `ai-daily log -t "xxx" -n "学到了xxx" -m 10` 打卡
4. 周末 `ai-daily stats` 回顾本周学习

### 配合 cron 定时提醒

```bash
# 每天早上 9 点提醒
crontab -e
0 9 * * * cd /path/to/random && python -m ai_daily digest > /tmp/ai-daily.txt && osascript -e 'display notification "今日AI动态已更新！" with title "ai-daily"'
```

## 数据存储

学习记录保存在 `~/.ai-daily/learning_log.json`，纯 JSON 格式，方便备份和迁移。

## 自定义RSS源

编辑 `ai_daily/feeds.py` 中的 `DEFAULT_FEEDS` 列表，添加你感兴趣的 RSS 源。

## 技术要求

- Python >= 3.10
- 无需安装任何第三方包

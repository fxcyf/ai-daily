# ai-daily — AI 日报生成 + Obsidian 联动

自动抓取 AI 领域最新动态，用 Claude 生成中文日报，写入 Obsidian 笔记库。设好 cron 后每天打开 Obsidian 就能看。

## 安装

```bash
pip install -e .
```

## 配置

```bash
# 设置 Anthropic API Key
ai-daily config --api-key sk-ant-xxx

# 设置 Obsidian vault 路径
ai-daily config --vault ~/Documents/MyVault

# 查看当前配置
ai-daily config
```

也可以用环境变量：`ANTHROPIC_API_KEY`、`AI_DAILY_OBSIDIAN_VAULT`

## 使用

```bash
ai-daily generate          # 抓取文章 → AI 生成中文日报 → 写入 Obsidian
ai-daily generate -c 20    # 基于 20 篇文章生成
ai-daily sources           # 查看 RSS 订阅源
```

日报保存到 `{vault}/AI-Daily/YYYY-MM-DD.md`。

### 配合 cron 每天自动运行

```bash
0 8 * * * cd /path/to/ai-daily && ai-daily generate
```

## 数据存储

- **AI 日报** → `{Obsidian vault}/AI-Daily/YYYY-MM-DD.md`
- **配置** → `~/.ai-daily/config.json`

## 自定义 RSS 源

编辑 `ai_daily/feeds.py` 中的 `DEFAULT_FEEDS` 列表。

## 技术要求

- Python >= 3.10
- `anthropic` SDK（`pip install -e .` 自动安装）

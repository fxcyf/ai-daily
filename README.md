# ai-daily — 每日AI动态追踪 + 智能日报 + Obsidian 联动

一个 Python CLI 工具，帮你每天花几分钟跟踪 AI/ML/Agent 领域最新动态，用 AI 生成中文日报，自动写入 Obsidian 笔记库。

## 功能

- **RSS 聚合** — 从 8 个高质量源（HN、ArXiv、MIT Tech Review、OpenAI、Anthropic 等）抓取最新内容
- **智能过滤** — 基于关键词匹配和相关度评分，只展示 AI 相关内容
- **AI 日报生成** — 调用 Claude API 将文章整理成中文日报，按主题分组、提炼要点，手机上直接看
- **Obsidian 联动** — 日报自动写入 Obsidian vault，支持 git 自动同步
- **学习打卡** — 记录每天读了什么、学了什么、花了多少时间
- **连续追踪** — 维护学习连续天数，激励你坚持每日学习

## 安装

```bash
pip install -e .
```

## 初始配置

```bash
# 设置 Anthropic API Key（用于 AI 日报生成）
ai-daily config --api-key sk-ant-xxx

# 设置 Obsidian vault 路径
ai-daily config --vault ~/Documents/MyVault

# 查看当前配置
ai-daily config
```

也可以通过环境变量配置：
```bash
export ANTHROPIC_API_KEY=sk-ant-xxx
export AI_DAILY_OBSIDIAN_VAULT=~/Documents/MyVault
```

## 使用

### 生成 AI 日报（核心功能）

```bash
ai-daily generate          # 抓取文章 → AI 生成中文日报 → 写入 Obsidian
ai-daily generate -c 20    # 基于 20 篇文章生成
```

日报会自动保存到 `{vault}/AI-Daily/2026-04-03.md`，打开 Obsidian 即可阅读。

配合 cron 每天自动运行：
```bash
# 每天早上 8 点自动生成日报
0 8 * * * cd /path/to/ai-daily && ai-daily generate
```

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

### 手机访问（Web 界面）

```bash
ai-daily serve           # 启动 Web 服务器，默认 8080 端口
ai-daily serve -p 3000   # 自定义端口
```

手机和电脑连同一个 WiFi，打开终端提示的地址即可访问。支持：
- 浏览今日 AI 动态
- 一键打卡（表单提交）
- 查看学习统计和最近 14 天记录
- 暗色主题，针对移动端优化

也可以添加到手机主屏幕作为 Web App 使用（iOS Safari 菜单 → 添加到主屏幕）。

## 每日使用建议

**最简流程：** 设好 cron 后什么都不用做，每天打开 Obsidian 看日报就行。

想深入学习时：
1. 看日报，挑感兴趣的文章点链接深入阅读
2. 直接在 Obsidian 的日报文件里记笔记
3. `ai-daily log -t "xxx" -n "学到了xxx" -m 10` 打卡（可选）
4. 周末 `ai-daily stats` 回顾

## 数据存储

- **AI 日报** → `{Obsidian vault}/AI-Daily/YYYY-MM-DD.md`
- **学习记录** → `~/.ai-daily/learning_log.json`
- **配置** → `~/.ai-daily/config.json`

## 自定义RSS源

编辑 `ai_daily/feeds.py` 中的 `DEFAULT_FEEDS` 列表，添加你感兴趣的 RSS 源。

## 技术要求

- Python >= 3.10
- `anthropic` SDK（AI 日报生成需要，`pip install -e .` 会自动安装）

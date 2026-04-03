# 测试指南

## 运行测试

```bash
python -m pytest tests/ -v
```

## 测试覆盖

### feeds 模块 (test_feeds.py)

| 测试 | 描述 |
|------|------|
| TestStripHtml | HTML标签清除：空字符串、纯文本、含标签 |
| TestParseDate | 日期解析：RFC822、ISO格式、无效输入、空字符串 |
| TestScoreRelevance | 相关度评分：高相关AI文章、无关文章、中等相关 |
| TestArticle | 文章模型：阅读时间计算、最小值保证 |

### tracker 模块 (test_tracker.py)

| 测试 | 描述 |
|------|------|
| test_log_today_creates_entry | 打卡创建新记录 |
| test_log_today_accumulates | 同一天多次打卡累加 |
| test_persistence | 数据持久化到磁盘 |
| test_streak_no_entries | 无记录时连续天数为0 |
| test_streak_today_only | 仅今天打卡连续1天 |
| test_streak_consecutive_days | 连续多天正确计算 |
| test_streak_broken | 中断后只计最近连续 |
| test_longest_streak | 历史最长连续记录 |
| test_stats | 统计数据汇总 |
| test_recent_entries | 最近N天记录查询 |

### web 模块 (test_web.py)

| 测试 | 描述 |
|------|------|
| test_page_wrapper | HTML 页面包装：viewport、active nav |
| test_render_digest_empty | 无文章时的空状态页面 |
| test_render_digest_with_articles | 有文章时正确渲染标题/来源/分类 |
| test_render_log_form | 打卡表单包含所有字段 |
| test_render_log_success | 打卡成功后显示提示 |
| test_render_stats | 统计页面包含所有指标 |
| test_xss_prevention | XSS 防护：script/onerror 被转义 |

### config 模块 (test_config.py)

| 测试 | 描述 |
|------|------|
| test_load_empty | 空目录加载返回空 dict |
| test_save_and_load | 保存后加载正确恢复 |
| test_env_var_override | 环境变量覆盖文件配置 |
| test_load_corrupted_file | 损坏的 JSON 文件不报错 |

### llm 模块 (test_llm.py)

| 测试 | 描述 |
|------|------|
| test_empty_articles | 空文章列表返回默认提示 |
| test_generates_digest | Mock API 调用正确生成日报 |
| test_handles_no_text_block | API 返回空内容时的降级处理 |

### obsidian 模块 (test_obsidian.py)

| 测试 | 描述 |
|------|------|
| test_creates_file | 在指定日期创建 .md 文件 |
| test_file_content_has_frontmatter | 文件包含 YAML frontmatter |
| test_creates_ai_daily_subdir | 自动创建 AI-Daily 子目录 |
| test_overwrites_existing | 同一天重新生成会覆盖 |
| test_defaults_to_today | 不指定日期默认使用今天 |

## 添加新测试

新增功能时，在对应的 `tests/test_*.py` 中添加测试用例，确保：
1. 测试覆盖正常路径和边界情况
2. tracker 测试使用临时目录，不污染真实数据
3. feeds 测试不依赖网络（使用构造的 Article 对象）
4. llm 测试 Mock Anthropic API，不发真实请求

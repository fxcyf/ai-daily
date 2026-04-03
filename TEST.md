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
2. feeds 测试不依赖网络（使用构造的 Article 对象）
3. llm 测试 Mock Anthropic API，不发真实请求

# 经验教训

## 2026-04-03 — ai-daily 项目初始化

- **做了什么**: 从零构建了 ai-daily CLI 工具（RSS聚合 + 学习打卡）
- **技术决策**: 零外部依赖，仅用标准库 `xml.etree`、`urllib`、`json`
  - 好处：无需 `pip install` 任何依赖即可运行
  - 代价：RSS 解析不如 `feedparser` 健壮，但对主流格式足够
- **注意**: ArXiv RSS 返回的是 RDF/Atom 混合格式，需要同时处理 RSS 2.0 和 Atom
- **Commit**: (见 git log)

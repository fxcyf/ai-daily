# 经验教训

## 2026-04-03 — 简化为 AI 日报 + Obsidian 管线

- **做了什么**: 砍掉 web 界面、学习打卡、连续天数等功能，只保留核心管线：RSS → Claude 摘要 → Obsidian
- **教训**: 不要为了做工具而做工具。用户只需要碎片时间学东西，最简方案是每天自动生成日报写入 Obsidian
- **Commit**: (见 git log)

## 2026-04-03 — ai-daily 项目初始化

- **做了什么**: 从零构建了 ai-daily CLI 工具（RSS聚合 + 学习打卡）
- **技术决策**: ArXiv RSS 返回的是 RDF/Atom 混合格式，需要同时处理 RSS 2.0 和 Atom
- **Commit**: (见 git log)

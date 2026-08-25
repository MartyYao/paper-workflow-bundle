# Method source map

本技能不是把外部仓库原样复制，而是将其结构适配到中文公司金融和 CSSCI 实证论文。

| 来源 | 吸收内容 | 不直接照搬的部分 |
|---|---|---|
| [K-Dense Scientific Agent Skills](https://github.com/K-Dense-AI/scientific-agent-skills) | evidence boundary、rival explanations、discriminating predictions、operationalization、确定性结构校验 | 不自动评分、排序或替用户接受/淘汰假设；按中国经管数据和制度改写 |
| [Orchestra AI Research SKILLs](https://github.com/Orchestra-Research/AI-Research-SKILLs) | 将 ideation 与总流程分离；problem-first/solution-first；多框架构思 | 不把通用科学头脑风暴当作文献空白证据 |
| [academic-research-skills](https://github.com/Imbad0202/academic-research-skills) | 阶段、成果物、检查点、用户确认和 provenance/integrity gate | 不复制其通用深度研究代理编排；沿用本地 Obsidian 项目结构 |
| [paper-search-mcp](https://github.com/openags/paper-search-mcp) | 多来源搜索、去重、DOI、全文和来源能力透明 | 不替代 CNKI、NCPSSD、Zotero，也不负责判断创新价值 |
| 旧版 `chinese-corporate-finance-topic-design` | 三通道检索、CSMAR 可得性、直接 X→Y、主 Y 不用交互项、单向故事 | 将其从“给出选题建议”提升为证据台账和决策门 |
| 当前 `paper-workflow` | Obsidian 入口、阶段 0 输出、Edmans 护栏、CSSCI 边界、淘汰记录 | 由本技能承接所有非调度性的选题协议 |

## 架构边界

`paper-workflow` 是中枢：读取仪表盘、加载 `research-topic`、传递项目上下文、检查成果物、等待用户确认并推进阶段。

`research-topic` 是专业技能：检索、筛选、编码、空白论证、贡献价值、可行性、竞争性解释和 GO/HOLD/KILL 档案都在这里完成。

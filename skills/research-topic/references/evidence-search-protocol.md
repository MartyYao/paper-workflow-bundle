# Evidence-bounded literature search protocol

## 目标

把“空白判断”变成可复核的检索记录，而不是一次性搜索结果或模型记忆。检索结果只能支持“在既定边界内未定位到”，不能支持“没有任何研究”。

## 1. 建立检索边界

在开始搜索前写入 `选题检索边界.md`：

| 字段 | 要求 |
|---|---|
| 研究问题版本 | 当前待检验的一句话问题，注明版本号 |
| 检索日期 | YYYY-MM-DD；新近领域设置截止日期 |
| 中文来源 | CNKI RSS、CNKI 主动检索、NCPSSD、Zotero 本地库等 |
| 英文来源 | OpenAlex、Crossref、Semantic Scholar、SSRN、Zotero 等 |
| 检索层级 | 精确主题、邻近机制、方法/政策三层 |
| 时间范围 | 近五年核心文献 + 经典理论/方法文献 |
| 期刊边界 | CSSCI、中文核心、英文领域期刊及必要的工作论文 |
| 排除标准 | 非学术来源、重复记录、与研究问题无关、无法核验的引用 |
| 已知限制 | 登录墙、全文不可得、关键词歧义、数据库覆盖不足 |

## 2. 查询矩阵

至少为每个概念准备中文和英文同义词，并组合以下四类词：

1. 处理变量或制度：政策名称、制度同义词、机构名称、英文缩写；
2. 结果变量：经济概念、数据库常用指标、理论术语；
3. 机制：行为渠道、资源渠道、治理渠道、金融渠道；
4. 研究对象和方法：企业、上市公司、地方政府、DID、panel、IV 等。

每层至少形成多组组合，而不是只搜一句自然语言问题。对中文政策变量尤其要加入历史名称、机构升格/改名和地方异名。

## 3. 来源路由

### 中文

- `chinese-literature`：优先使用 CNKI RSS 监控、CNKI 主动检索和 NCPSSD 开放检索；
- RSS 只适合获取期刊最新论文，不能替代主题检索；
- CNKI 浏览器或网页结果需要记录是否经过 CSSCI/核心期刊过滤；
- Zotero 用于本地去重、精读和全文回溯，不把“已在 Zotero”当作完整领域覆盖。

### 英文

- OpenAlex/Crossref：发现、DOI 和元数据核验；
- Semantic Scholar：补充引用网络和相近论文；
- SSRN/工作论文：用于识别尚未正式发表的竞争性研究，并标记出版状态；
- `paper-search-mcp`：可作为多来源发现、去重和全文获取层，使用时记录实际调用的平台和失败原因。

从多来源平台获得的题目、作者和年份必须回到 DOI、期刊官网、出版社或 Zotero 全文核验。不得把搜索摘要当作论文结论。

## 4. 筛选和编码

对题目和摘要先筛选，进入全文后再确认。每篇纳入文献至少编码：

```text
作者/年份/期刊/DOI
研究问题
处理变量 X
结果变量 Y
机制 M
制度环境和样本
识别策略
主要结论
与候选题目的关系
证据角色：支持 / 挑战 / 限定 / 背景
```

排除文献必须记录理由。相同论文的预印本、期刊版和重复 DOI 合并为一条，但保留出版状态。

## 5. 最低覆盖检查

探索初筛检查：

- 至少建立 4 个研究分支，每个分支至少 3 篇独立学术文献；
- 每个分支尽量至少有 1 篇中文和 1 篇英文，且分支层面至少有 1 篇挑战、限制或不同结论的研究；
- 同一 X×Y 尚未形成前，不强行要求精确文献；精确文献为 0 时记录 `UNKNOWN` 或 `NOT-LOCATED-WITHIN-BOUNDARY`，不作“没人研究”的判断。

优先路径进入决策门前，检查：

- 中文近五年核心/CSSCI 文献已查；
- 英文对应主题及相邻机制文献已查；
- 经典理论和方法文献已查；
- 优先分支已扩展到 5—8 篇独立学术文献，且包含精确、邻近、近期和挑战/限定性研究；
- 同一 X×Y、同一政策×Y 和同一机制×Y 的竞争论文已查；
- 至少一批反对、限制或得到不同结论的文献已查；
- 关键词、数据库、日期和筛选过程已写入台账；
- 代表性来源可以追溯到原文、DOI 或稳定数据库记录。

如果某一通道不可用，候选题目只能标记 `HOLD`，除非把缺失通道和补救计划明确写入风险项。

## 6. 证据台账字段

`文献证据台账.csv` 至少包含：

```text
record_id,branch_id,relation_type,search_status,language,source,search_date,query,
title,authors,year,journal,doi,firm_level,x_concept,y_concept,mechanism,
sample,identification,evidence_role,claim_supported,claim_challenged,
screen_status,fulltext_status,exclusion_reason,notes
```

`relation_type` 使用 `DIRECT`、`ADJACENT-X`、`ADJACENT-Y`、`ADJACENT-M`、`BACKGROUND`；`search_status` 使用 `LOCATED`、`NOT-LOCATED-WITHIN-BOUNDARY`、`UNKNOWN`；`evidence_role` 使用 `support`、`challenge`、`limit`、`context`；`screen_status` 使用 `included`、`excluded`、`uncertain`。不确定记录不得静默删除。

## 方法来源

- K-Dense 的 evidence ledger/search-boundary 思路：[hypothesis-generation](https://raw.githubusercontent.com/K-Dense-AI/scientific-agent-skills/main/skills/hypothesis-generation/SKILL.md)；
- 系统检索、筛选、PRISMA 和引用核验原则：[literature-review](https://raw.githubusercontent.com/K-Dense-AI/scientific-agent-skills/main/skills/literature-review/SKILL.md)；
- 多来源发现、去重、DOI 和全文获取：[paper-search-mcp](https://github.com/openags/paper-search-mcp)。

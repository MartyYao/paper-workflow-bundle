# 平行趋势检验：子样本（over/under）的处理

> 来源：论文 1 实证经验（2026-07）

## 问题

多期 DID 中，如果被解释变量被拆分为条件子样本（如仅 ε>0 的 over 指标、仅 ε<0 的 under 指标），直接用全样本跑平行趋势检验会发现处理前趋势不平行。

**根因**：ε 的符号本身可能受政策影响——如果政策导致部分企业从 "ε>0" 变为 "ε<0"，那么 over 子样本（仅 ε>0）的成员在政策前后不一致。政策后 ε 符号切换的企业被排除在 over 子样本外，导致处理后的 over 子样本是「幸存者」——政策前 over 子样本包含了后来将变为 under 的企业。

## 解决方法：符号一致子样本

仅保留政策前后 ε 符号一致的企业：

```stata
* 比较 bureau_year 前一年 vs bureau_year 当年的 ε 符号
gen byte sign_before = sign(e_v1) if rel_time == -1
gen byte sign_after  = sign(e_v1) if rel_time == 0
bysort Stkcd: egen sign_before_f = max(sign_before)
bysort Stkcd: egen sign_after_f  = max(sign_after)
gen byte sign_stable = (sign_before_f == sign_after_f) if !missing(sign_before_f) & !missing(sign_after_f)

* 符号一致子样本
gen byte over_stable  = (sign_stable == 1 & sign_before_f == 1)   // 始终 ε>0
gen byte under_stable = (sign_stable == 1 & sign_before_f == -1)  // 始终 ε<0

* 仅在符号一致子样本上跑事件研究
reghdfe over_v1 ib4.rel_time_pos $controls if over_stable == 1, absorb(Stkcd year) vce(cluster prov_id)
```

## 效果（论文 1 实测）

| DV | 修复前 | 修复后 |
|----|--------|--------|
| over_v1 处理前 | t-4 边际显著 (p<0.10) | **全部不显著** |
| over_v1 处理后 | 仅 t=0 显著，之后消失 | **t=0~t+6 全部显著** |
| under_v1 处理前 | t-3/t-2 显著 | **仍然显著**（结构性限制） |

## under 为什么仍然不行

under 子样本（始终 ε<0，~1900 obs）是一个结构性不同的群体：
- 集中在特定行业（G/H/K/D 行业 under 比例 > 50%）
- 企业特征显著不同（Size 更低、Lev 更高、ROA 更低，p<0.001）
- 处理组 under 均值在处理前就在扩大（缺口恶化）

这是一个样本选择问题，不是识别策略问题。论文中坦诚报告 under 的平行趋势局限性，并在主要结论中仅依赖 dev（全样本）和 over（符号一致子样本）。

## 论文中的呈现方式

在事件研究表格中：
- dev_V1/V2：标注「全样本」
- over_V1/V2：标注「符号一致子样本（始终 ε>0）」
- under_V1/V2：标注「符号一致子样本（始终 ε<0）」

在结论中：
- dev 和 over：平行趋势成立，作为核心证据
- under：坦诚说明识别局限性，作为补充分析

## 审稿应对

如果审稿人质疑 under 的平行趋势：
1. 解释结构性问题：ε 符号切换导致子样本选择偏误
2. 展示符号一致子样本的结果：over 通过，under 仍有限制
3. 强调 dev（全样本）是核心 DV，under 是补充分析
4. 引用论文中公开讨论这一限制的段落

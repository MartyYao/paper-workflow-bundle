# 数据变量来源速查（省级大数据局 → 企业）

## 已在 working_data 中的变量

| 类别 | 变量示例 |
|------|---------|
| 被解释变量 | dev_v1, over_v1, under_v1, dev_v2, over_v2, under_v2 |
| 处理变量 | post, treat_score1, d_zhengting, d_admin_gov, d_futing |
| 企业财务 | Size, Lev, ROA, SOE, Growth, TobinQ, FirmAge, Top1, total_revenue |
| 省级控制 | sci_ratio, ln_pop, urban_rate, ln_avg_wage, wage_growth, ln_fiscal_ratio, ln_gdp, gdp_growth, tertiary_share, market_index |
| 机制变量 | pc_any, suspect_rd, RDIN, Bper, srdi_any, high_market |
| 经济后果 | patent_app_t1, patent_inv_t1, TFP_OP_t1, TobinQ_t1 |
| 竞争政策 | post_gt3, info_benefit, keyword_ratio |

## 不在 working_data 中、需要外部拉取的变量

### 机制检验用

| 机制方向 | 所需变量 | CSMAR 来源 | 复杂度 |
|---------|---------|-----------|:---:|
| 抑制寻租 | 招待费/差旅费 | 财务报表附注—管理费用明细 | 高 |
| 缓解信息不对称 | 分析师预测分歧度 | 分析师预测数据库 | 中 |
| 降低制度性交易成本 | 管理费用率（AdminExp/Revenue） | 利润表—管理费用 | 低 |
| 改善信息透明度 | 审计意见 / 信息披露评级 | 审计意见数据库 / 深交所评级 | 中 |
| 跨部门协同 | BTD（会计-税收差异） | 利润表+现金流量表（已有） | 低 |
| 企业数字化转型 | IT人员占比 / 数字化词频 | CSMAR数字化专题 / 年报文本 | 中-高 |

### 构造方法

**BTD（避税程度）**：
```
BTD = (利润总额 - 所得税费用 / 名义税率) / 总资产
```
需要：利润总额（已有或可算）、所得税费用（利润表）、名义税率（25%）

**管理费用率**：
```
admin_ratio = 管理费用 / 营业收入
```
需要：管理费用（利润表）、营业收入（已有 total_revenue）

## 注意事项

- **三步法可用性检查**：M 如果是企业固定特征（pc_any, SOE），直接跳过三步法
- **连续变量 > 二元分组**：RDIN > suspect_rd
- **省-年聚类要求**：机制 M 如果在省-年层面构造，需 ≥ 25 省的聚类数

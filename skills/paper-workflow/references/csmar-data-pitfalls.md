# CSMAR 数据处理陷阱速查

> 本会话中因以下问题导致 do 文件重跑 3+ 次。每次合并 CSMAR 新数据前检查。

## 1. Stkcd 类型不一致

**问题**：working_data 中 `Stkcd` 是字符串（`str6`，如 `"000001"`），但不同 CSMAR 子库的 Stkcd 可能是：
- 字符串 `"000001"` → 直接 merge 即可
- 数值 `1` → 需要 `gen Stkcd_str = string(Stkcd, "%06.0f")` 或 `destring`
- 有些子库字段名是 `Symbol` 而非 `Stkcd`

**解决**：merge 前先确认两边类型一致。
```stata
* 检查 working_data 中 Stkcd 类型
describe Stkcd
* 检查 CSMAR 数据中 Stkcd 类型
use "csmar_file.dta", clear
describe Stkcd Symbol
```

## 2. 年度变量命名不统一

CSMAR 子库使用不同命名：
- `Accper`（会计截止日期）→ `gen year = year(date(Accper, "YMD"))`
- `EndDate`（统计截止日期）→ `gen year = year(date(EndDate, "YMD"))`
- `DecisionDate`（决策日期）
- `Fenddt`（预测终止日）— 分析师预测子库专属

## 3. 变量类型惊喜

- `Audittyp`（审计意见）在某些版本中是**字符串**，需 `destring`
- `AnanmID`（分析师ID）是**字符串**，不能直接用 `collapse (count)`，须用 `egen tag()`
- `Typrep == "A"` 用于筛选合并报表（CSMAR 财务数据库）

## 4. collapse 和字符串

```stata
* ❌ 错误：字符串变量不能用 count
collapse (count) NumAnalyst=AnanmID, by(Stkcd year)

* ✅ 正确：用 egen tag
egen tag_analyst = tag(Stkcd year AnanmID)
bysort Stkcd year: egen NumAnalyst = total(tag_analyst)
collapse (mean) NumAnalyst, by(Stkcd year)
```

## 5. 缺失 Winsor2 时的替代方案

```stata
* 如果 winsor2 未安装
qui sum varname, d
replace varname = r(p1) if varname < r(p1) & !missing(varname)
replace varname = r(p99) if varname > r(p99) & !missing(varname)
```

## 7. 超大 CSV 的分块处理

CSMAR/CNRDS 的批发数据（如专利引用 15.9M 行）不能一次性加载到 Stata 或 Python。

### Python 分块

```python
reader = pd.read_csv(csv_path, usecols=required_cols, dtype=str, chunksize=500000)
chunks = []
for i, chunk in enumerate(reader):
    chunks.append(chunk)
    if i >= max_chunks:  # ~10M rows enough for firm-year aggregation
        break
df = pd.concat(chunks)
```

### Stata 分块

```stata
* 先在 Python 中聚合成 firm-year (10 万行量级)
* 再 import delimited 到 Stata
import delimited "/tmp/aggregated.csv", clear
```

## 8. Stkcd 携带括号、逗号或空格

某些 CSMAR/CNRDS 子库的股票代码包含：`[000001]`、`[601238]`（带方括号），或 `000001，601318`（多代码，中文逗号分隔）。

```python
# Python: 批量清理
df['Stkcd'] = df['Stkcd'].str.replace('[', '', regex=False).str.replace(']', '', regex=False)

# 处理多代码行（爆炸展开）
def clean_stkcd(val):
    parts = str(val).replace('，', ',').split(',')
    return [p.strip() for p in parts if len(p.strip()) == 6]

df['Stkcd_list'] = df['Stkcd'].apply(clean_stkcd)
# 对多代码行做 explode 展开后汇总
```

```stata
* Stata: 清理方括号
replace Stkcd = subinstr(Stkcd, "[", "", .)
replace Stkcd = subinstr(Stkcd, "]", "", .)
```

**注意**：方括号可能不是半角 `[` 而是全角 `［`，检查后再替换。

## 9. 合并后的样本量检验

每次 merge 后打印样本量：
```stata
merge 1:1 Stkcd year using ..., keep(master match) nogen
di "Merge完成, N=" _N
tab _merge  // 检查未匹配比例
```

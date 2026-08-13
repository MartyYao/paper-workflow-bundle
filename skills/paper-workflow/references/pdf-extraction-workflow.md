# PDF 表格提取方法

> 本会话验证的流程：孙光林(2025)表1（31省大数据管理机构）成功提取。

## 场景

需要从学术论文 PDF 中提取表格数据（如省级大数据管理机构成立时间表），但：
- `pymupdf.get_text()` 提取的表格文字分散、残缺
- 表格行列结构丢失
- `vision_analyze` 无法直接处理 PDF 格式

## 方法

### 步骤 1：pymupdf 生成页面图像
```python
import fitz
doc = fitz.open("paper.pdf")
for p in [target_page_index]:  # 0-indexed
    page = doc[p]
    pix = page.get_pixmap(dpi=200)  # 200 DPI 够用
    pix.save(f"/tmp/page_{p+1}.png")
doc.close()
```

### 步骤 2：vision_analyze 读取图像
```
vision_analyze(
    image_url="/tmp/page_3.png",
    question="请读取表1的完整内容，列出所有行和列"
)
```

### 关键参数
- **dpi=200**：中文表格 150-200 DPI 即可，过高会导致超时
- **单页截图**：不要合并多页，逐页处理
- **问题措辞**：明确要求"完整列出所有行列"，避免省略

## 已知限制

- 仅当表格在 PDF 中为可渲染文字时有效（非扫描件 OCR）
- 横向大表可能跨页，需提取多页拼接
- 复杂合并单元格可能解析错误，需人工校对

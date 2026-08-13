---
name: chinese-literature
description: "中文文献检索与采集——两通道策略：CNKI 浏览器注入搜索（主动）、CNKI RSS（被动推送）。用于 paper-workflow 阶段 1 的中文文献层。"
version: 0.1.1
category: research
tags: [CNKI, Chinese, journals, literature-review, academic, RSS]
trigger: "用户需要搜索中文文献、查知网论文、监控中文期刊、做文献综述中的中文部分"
related_skills: [paper-workflow, academic-literature-collector]
---

# Chinese Literature Skill

中文文献检索与采集。两通道策略，按场景自动切换。

## 两通道总览

| 通道 | 技术方案 | 适用场景 | 可靠性 |
|------|---------|---------|--------|
| **CNKI 浏览器搜索** | Camofox + JS 注入（`browser_console`） | 主动关键词搜索、高级检索（CSSCI 过滤）、论文详情、期刊查询 | ✅ 已验证：搜索"数字经济"返回 134,836 条结构化结果 |
| **CNKI RSS** | Python urllib + CookieJar（两步认证） | 日常监控顶刊新论文 | ✅ 稳定，无验证码 |

## 快速使用

### 场景 1：关键词搜索知网

```python
# 1. 确保 Camofox 已启动
# 2. 导航到 CNKI 搜索页
# 3. 注入 JS 执行搜索 + 提取
```

完整流程见 `references/cnki-browser-search.md`，JS 代码见 `scripts/cnki-search.js`。

### 场景 2：监控顶刊 RSS

```python
# 使用 scripts/cnki-rss.py 采集
python3 scripts/cnki-rss.py JJYJ GLSJ --output md
```

## 与 paper-workflow 的集成

在 paper-workflow 的阶段 1（文献检索与综述）中，中文文献部分由本技能提供：

```
paper-workflow 阶段 1 流程（中文部分）:

1. 运行 CNKI RSS 采集 → 获取顶刊最新论文
2. 按用户关键词运行 CNKI 浏览器搜索 → 获取针对性结果
3. 合并 → 去重 → 分类 → 写入 Obsidian 02-文献/
```

**触发条件**：当 paper-workflow 处于阶段 1，且用户明确要求搜索中文文献时，自动加载本技能。

## 验证码处理

CNKI 使用腾讯滑块验证码（`#tcaptcha_transform_dy`）。检测逻辑：

```javascript
const cap = document.querySelector('#tcaptcha_transform_dy');
// SDK 预加载时 top=-1000000px（屏幕外），只有 top>=0 才真正可见
if (cap && cap.getBoundingClientRect().top >= 0) {
  return { error: 'captcha' };
}
```

检测到验证码 → 暂停 → 通知用户手动完成 → 用户确认后重试。

## 注意事项

1. **CNKI 搜索无需登录**，但下载 PDF 需要机构登录
2. **搜索不要太快**——CNKI 对短时间大量请求会触发验证码
3. **Camofox 需要预热**约 15 秒（`camofox-manager.sh start`）
4. **RSS 每刊最多返回 20 篇**，时间范围有限
5. **中文期刊预出版**标注未来月份，用状态文件增量处理

## 本技能依赖

- Camofox 浏览器容器（`~/.hermes/scripts/camofox-manager.sh`）
- Python 3（urllib, xml.etree.ElementTree）
- 可选：Zotero（用于文献管理）

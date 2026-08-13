---
name: research-media-skill
version: 0.1.2
description: 搜索经管之家(bbs.pinggu.org)等中文论坛获取实证实操方案。触发：Stata/计量/平行趋势/DID/回归问题。
---

# Research Media Skill

## 概述

本技能让 AI Agent 能够搜索中文经济论坛（如经管之家 bbs.pinggu.org）并读取帖子正文。

技能分为两个独立能力：
- **Read（读取正文）** — 通用层，任何有 HTTP 能力的 Agent 均可使用。**内置自动 cookie 续期**（Hermes Agent 下）。
- **Search（搜索帖子）** — Agent 依赖层，各 Agent 用自身能力完成。

---

## Read（通用层）：读取经管之家帖子正文

**任何 Agent 都能用**，只需一个 HTTP 客户端和登录 cookies。Hermes Agent 下 cookies 过期时会自动续期。

### 前置要求

**登录 cookies**：无论哪种 Agent 使用本技能，都需要先让用户配置经管之家的登录 cookies。

引导用户操作（Agent 据此引导用户，不可自行猜测或编造）：
1. 在浏览器打开 https://bbs.pinggu.org 并登录
2. 按 F12 → Application → Cookies → bbs.pinggu.org
3. 找到 `Z9M6_79fc_auth` 和 `Z9M6_79fc_saltkey` 两个键
4. 将它们的值按 `Name=Value` 格式写入凭据文件（每行一个，`#` 开头为注释）
5. 设置文件权限为 `chmod 600`

凭据文件路径：推荐 `~/.hermes/credentials/bbs-pinggu-cookies.txt`。

### 自动 cookie 续期（Hermes Agent 专用）

**原理**：用户在 Camofox 浏览器里登录一次经管之家后，Firefox 会把全部 cookies（包括 HttpOnly 的 `Z9M6_79fc_auth`）存到 profile 的 `cookies.sqlite`。脚本从中直接提取，无需登录表单、无需验证码。

1. **用户一次性配置**：在 Camofox 里打开 https://bbs.pinggu.org 并登录（保持会话有效）
2. Agent 调用 `search-bbs-pinggu.py read <URL>` 时会自动：
   - 检查 cookies 文件是否有效 → 有效则直接读帖
   - 无效 → 从 Camofox profile 的 `cookies.sqlite` 提取 `Z9M6_79fc_auth` / `Z9M6_79fc_saltkey` → 写入文件 → 用新 cookies 读帖
3. 全程自动，无需用户干预。**前提**：Camofox 里保持登录态（登录会话与文件 cookies 独立，Camofox 会话有效即可续期）

**其他 Agent**：如果无法自动续期，Agent 应提示用户手动重新导出 cookies。

### 读取命令

推荐使用辅助脚本（自动处理 cookie 检查、续期、解码、内容提取）：
```bash
python3 scripts/search-bbs-pinggu.py read "https://bbs.pinggu.org/thread-XXXXXXX-1-1.html"
```

或手动 curl（需自行确保 cookies 有效）：
```bash
curl -sL --max-time 20 \
  -A "Mozilla/5.0" \
  --cookie ~/.hermes/credentials/bbs-pinggu-cookies.txt \
  "https://bbs.pinggu.org/thread-XXXXXXX-1-1.html" \
  | iconv -f gbk -t utf-8
```

### 内容提取
帖子正文在 `<td class="t_f" id="postmessage_XXXXX">` 中。
提取中文文本块，过滤广告关键词（「赵安豆老师微信」「送您全额奖学金」等）。

### 注意事项
- 页面编码为 GBK，需转 UTF-8（`iconv -f gbk -t utf-8`）
- Cookies 有时效——Hermes 下自动续期；其他 Agent 提示用户重新导出
- 不要伪造帖子内容——读取失败时如实报告

---

## Search（Agent 依赖层）：搜索帖子

各 Agent 使用自身能力搜索经管之家的帖子。**核心目标**：找到 `https://bbs.pinggu.org/thread-XXXXXXX-1-1.html` 格式的 URL。

### Hermes Agent

使用 Camofox 浏览器 + 百度搜索：

```bash
./scripts/camofox-manager.sh start
```
然后用 `browser_navigate` 打开：
```
https://www.baidu.com/s?wd=site%3Abbs.pinggu.org+<关键词>
```
从搜索结果中提取帖子 URL，完成后关闭 Camofox：
```bash
./scripts/camofox-manager.sh stop
```

### Claude Code

**方式 A**（在 Hermes 内部运行 Claude Code）：与 Hermes Agent 相同，使用 Camofox。

**方式 B**（独立运行 Claude Code）：使用 Claude Code 自带的 web 搜索能力，搜索 `site:bbs.pinggu.org 关键词`，从结果中提取帖子 URL。

### Kimi Code

Kimi Code 有内置互联网搜索能力。直接在 prompt 中要求：
```
请搜索 site:bbs.pinggu.org 上的相关讨论，把帖子 URL 发给我。
```

### Pi / Codex / 其他 Agent

利用自身具备的 web 搜索工具。如果 Agent 没有搜索能力，可以让用户直接提供帖子 URL（用户在浏览器里搜，把链接给 Agent）。

### 兜底方案（所有 Agent 通用）

如果 Agent 无法自动搜索，**用户可以手动搜索后在对话中提供帖子 URL**，Agent 直接进入 Read 步骤读取正文。

---

## 文件结构

```
research-media-skill/
├── SKILL.md                       ← 本文件
├── README.md                      ← 概述 + 首次安装引导
├── AGENTS.md                      ← 跨 Agent 操作指引
├── CLAUDE.md                      ← Claude Code 专用指引
└── scripts/
    ├── camofox-manager.sh         ← Camofox 浏览器管理（Hermes 专用）
    └── search-bbs-pinggu.py       ← 帖子读取 + 自动 cookie 续期（从 Camofox 会话提取）
```

---

## 安全说明
- 凭据值不写入技能文件。Agent 引导用户自行填写
- 凭据文件权限 `chmod 600`。登录凭据与 cookie 文件分离存储
- 不伪造内容。读取失败时如实报告

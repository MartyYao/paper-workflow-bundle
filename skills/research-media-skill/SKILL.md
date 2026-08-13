---
name: research-media-skill
version: 0.1.3
description: >
  搜索经管之家(bbs.pinggu.org)等中文论坛获取实证实操方案。触发：Stata/计量/平行趋势/DID/回归问题。
  登录墙站点读帖主路线 = 腾讯 BrowserSkill (bsk) 真实浏览器登录态直连；无 bsk 环境降级为 curl + cookie。
---

# research-media-skill — 中文论坛实操方案检索

## 概述

让 AI Agent 搜索中文经济论坛（如经管之家 bbs.pinggu.org）并读取帖子正文。

两个独立能力：

- **Read（读取正文）** — 两层：**bsk 登录态直连**（Hermes 主路线，零 cookie 操作）；curl + cookie 文件（通用降级层，任何 Agent 可用）
- **Search（搜索帖子）** — Agent 依赖层，各 Agent 用自身能力完成

---

## 路由规则（先读）

| 场景 | 路线 | 说明 |
|------|------|------|
| Hermes 且已装 bsk（`~/.local/bin/bsk`） | **bsk** | 用户真实 Chrome 登录态，即开即用 |
| 无 bsk / 其他 Agent | curl + cookie | 需用户提供 cookie 文件 |
| 搜索帖子 | 百度 `site:`（Camofox 或 Agent 自身搜索） | 见 Search 节 |

---

## Read via bsk（Hermes 主路线）

用户经管之家登录态在真实 Chrome 里天然有效（页面显示 Marty_Yao），无需 cookie 导出或验证码交接。

```bash
SID=$(bsk session start)                        # 打开 Agent Window
bsk navigate --session $SID "https://bbs.pinggu.org/thread-XXXXXXX-1-1.html"
bsk get-html --session $SID --out /tmp/thread.html   # 必须 --out，stdout 管道不可靠
bsk session stop --all                          # 任务结束必须清理
```

正文提取（UTF-8 输出，无 GBK 问题）：

```python
import re, html
raw = open('/tmp/thread.html', encoding='utf-8').read()
posts = re.findall(r'<td class="t_f" id="postmessage_\d+">(.*?)</td>', raw, re.S)
for i, p in enumerate(posts):
    p = re.sub(r'<[^>]+>', ' ', p); p = html.unescape(p)
    p = re.sub(r'\s+', ' ', p).strip()
    if p and len(p) > 30:
        print(f'--- 楼层 {i+1} ---'); print(p[:600])
```

要点：
- navigate 偶发 RPC 超时但页面已加载——先 snapshot 确认，别急着重试
- 登录验证：snapshot 中出现用户账号名（Marty_Yao）即登录态有效；否则用 `bsk request-help` 把控制权交给用户处理登录/验证码
- 楼层 1 常混入 CSS 邀请码样式（.invite 开头），跳过即可
- **隐私边界**：bsk 操作真实浏览器，仅限需要登录态的任务，用完即停会话

## Read via curl（通用降级层）

无 bsk 环境（其他 Agent / 未安装）。需要用户配置经管之家登录 cookies：

1. 浏览器打开 https://bbs.pinggu.org 并登录
2. F12 → Application → Cookies → bbs.pinggu.org
3. 找到 `Z9M6_79fc_auth` 和 `Z9M6_79fc_saltkey` 两个键
4. 按 `Name=Value` 格式写入凭据文件（每行一个，`#` 开头为注释）
5. `chmod 600` 凭据文件

凭据文件路径：`~/.hermes/credentials/bbs-pinggu-cookies.txt`（Hermes）；其他 Agent 按自身约定，**凭据值不写入技能文件**。

读取命令（推荐辅助脚本，自动处理解码与内容提取）：

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

### 注意事项

- 页面编码 GBK，curl 路线需 `iconv -f gbk -t utf-8`（bsk 路线无此问题）
- Cookies 有时效——失效时引导用户重新导出，**不要伪造帖子内容**，读取失败如实报告
- 脚本只支持 `read`/`check` 两个动作；站内搜索页 search.php 有滑动验证码，站内搜索不可用，只能靠百度 `site:` 发现帖子

---

## Search（Agent 依赖层）：搜索帖子

各 Agent 使用自身能力搜索经管之家。**核心目标**：找到 `https://bbs.pinggu.org/thread-XXXXXXX-1-1.html` 格式的 URL。

### Hermes Agent

百度搜索（Camofox 浏览器，无需登录态）：

```
https://www.baidu.com/s?wd=site%3Abbs.pinggu.org+<关键词>
```

启动 Camofox 方式：`~/.hermes/scripts/camofox-manager.sh start`（或按 browser-automation 技能的路由，搜索类任务走 Camofox）；搜完关闭释放内存。从搜索结果提取 `thread-XXXXXXX-1-1.html` 格式 URL，然后进入 Read 步骤。

### Claude Code / Kimi Code / Pi / Codex / 其他 Agent

- 有搜索能力 → 直接搜 `site:bbs.pinggu.org 关键词`
- 无搜索能力 → 让用户手动搜索后提供帖子 URL，Agent 进入 Read 步骤

---

## 文件结构

```
research-media-skill/
├── SKILL.md                       ← 本文件
├── README.md                      ← 概述 + 首次安装引导
└── scripts/
    └── search-bbs-pinggu.py       ← curl 读帖 + 内容提取（通用降级层）
```

---

## 安全说明

- 凭据值不写入技能文件。Agent 引导用户自行填写
- 凭据文件权限 `chmod 600`
- 不伪造内容。读取失败时如实报告
- bsk 路线权限大（可触达用户所有已登录账号）：仅限登录墙任务使用，任务结束立即 `session stop --all`

# paper-workflow-bundle

> Version: v0.1.0（2026-08-25）

经管实证论文全流程技能全家桶聚合仓库：一个 tap 源装齐 `paper-workflow` 及其全部配套技能。

`paper-workflow`（8 阶段论文编排器）依赖 7 个配套技能才能完整运转。本仓库把 8 个技能聚合到单一 GitHub 仓库，支持：

1. **一键安装**：`hermes skills tap add` + 循环 `install`，一条命令装齐全家桶
2. **运行时 bundle**：`/paper-workflow` 一次加载全部 8 个技能
3. **自动同步**：GitHub Action 每日从各源仓库拉取最新版，聚合仓始终是最新镜像

## 快速安装

```bash
curl -fsSL https://raw.githubusercontent.com/MartyYao/paper-workflow-bundle/main/install.sh | bash
```

## 手动安装（等价于脚本做的事）

```bash
# 1. 下载聚合仓库 zip（codeload 静态 CDN，无 GitHub API 限额）
curl -fsSL -o /tmp/pw-bundle.zip https://codeload.github.com/MartyYao/paper-workflow-bundle/zip/refs/heads/main
mkdir -p /tmp/pw-bundle && cd /tmp/pw-bundle && unzip -q ../pw-bundle.zip

# 2. 按类别拷贝 8 个技能
#    research/:    paper-workflow research-topic stata-regression research-discovery chinese-literature research-media-skill
#    writing/:     meng-skills
#    productivity/: journal-submission-docx
for skill in paper-workflow research-topic stata-regression research-discovery chinese-literature research-media-skill; do
  rm -rf ~/.hermes/skills/research/$skill && cp -R paper-workflow-bundle-main/skills/$skill ~/.hermes/skills/research/
done
rm -rf ~/.hermes/skills/writing/meng-skills && cp -R paper-workflow-bundle-main/skills/meng-skills ~/.hermes/skills/writing/
rm -rf ~/.hermes/skills/productivity/journal-submission-docx && cp -R paper-workflow-bundle-main/skills/journal-submission-docx ~/.hermes/skills/productivity/

# 3. （可选）bundle 定义：/paper-workflow 一次加载全部
mkdir -p ~/.hermes/skill-bundles
cp paper-workflow-bundle-main/skill-bundles/paper-workflow.yaml ~/.hermes/skill-bundles/
```

> **为什么不用 `hermes skills install`（2026-08-13 用户反馈修订）**：
> 1. GitHub API 未认证限额 60 次/小时——8 个技能逐个 install 一次装不完（`Could not fetch from any source`）
> 2. registry（clawhub）存在同名 `paper-workflow`（v0.1.0）——install 可能解析到 registry 版而非本仓库版
> 本仓库的 install.sh 直接下载 zip 拷贝，绕开这两个问题。安装后**务必验证版本**（见下方排障）。

## 使用方法

| 方式 | 命令/说法 | 效果 |
|------|-----------|------|
| 自然语言 | 「写论文」「开始写论文」「继续论文」 | 触发 paper-workflow 编排器 |
| 一次加载全部 | `/paper-workflow` | 8 个技能全部加载（bundle） |
| 单个技能 | `/stata-regression`、`/meng-skills` 等 | 只加载一个 |

## 配套技能清单

| 技能名 | 源仓库 | 用途 |
|--------|--------|------|
| paper-workflow | [paper-workflow-skill](https://github.com/MartyYao/paper-workflow-skill) | 8 阶段论文编排器（总调度） |
| research-topic | [research-topic-skill](https://github.com/MartyYao/research-topic-skill) | 阶段 0 双语选题证据、空白/贡献、可行性审计和决策门 |
| meng-skills | [meng-skills](https://github.com/MartyYao/meng-skills) | 中文写作润色、去 AI 味 |
| stata-regression | [Stata-Regression-skill](https://github.com/MartyYao/Stata-Regression-skill) | Stata 编码规范、表格、出图 |
| research-discovery | [research-discovery-skill](https://github.com/MartyYao/research-discovery-skill) | 实证异常结果分层诊断 |
| chinese-literature | [Chinese-Literature-Skill](https://github.com/MartyYao/Chinese-Literature-Skill) | 中文文献检索（CNKI 双通道） |
| journal-submission-docx | [journal-submission-docx-skill](https://github.com/MartyYao/journal-submission-docx-skill) | 期刊投稿版 docx 生成（13 刊模板） |
| research-media-skill | [research-media-skill](https://github.com/MartyYao/research-media-skill) | 经管之家论坛实操方案检索 |

> 注：`aers-index`（本地 AERS 方法论库路由）依赖 `~/hermes/aers/` 本地仓库，不随本包分发。

## 更新

```bash
# 重新运行 install.sh（zip 覆盖式安装，幂等）
curl -fsSL https://raw.githubusercontent.com/MartyYao/paper-workflow-bundle/main/install.sh | bash
```

## 排障

| 症状 | 原因 | 解决 |
|------|------|------|
| `hermes skills list` 显示 paper-workflow 版本 0.1.0 | 装到了 registry（clawhub）同名技能，不是本仓库版 | `hermes skills uninstall paper-workflow`（如可卸载）后重跑 install.sh；或直接重跑 install.sh（zip 覆盖） |
| `hermes skills update` 后版本被降级 | `.hub/lock.json` 里有 registry 同名残留 | install.sh 已自动清理 clawhub 残留；手动清理：删除 `~/.hermes/skills/.hub/lock.json` 中 `paper-workflow` 等条目 |
| 安装报 `Could not fetch from any source` | GitHub API 未认证限额 60 次/小时（用 `hermes skills install` 逐个装时） | 改用本仓库 install.sh（zip 静态 CDN，无 API 限额） |
| 技能显示为 `local` 源、`hermes skills update` 不跟踪 | 本方案就是本地拷贝（有意为之） | 更新 = 重跑 install.sh；如需 hub 托管，先配 `GITHUB_TOKEN` 到 `~/.hermes/.env` 或登录 `gh`，再走 `hermes skills install` |

## 目录结构

```
paper-workflow-bundle/
├── skills/                     # tap 技能源（每技能一个文件夹）
│   ├── paper-workflow/         #   SKILL.md + references/ + scripts/ ...
│   ├── research-topic/         #   SKILL.md + references/ + scripts/ ...
│   ├── meng-skills/
│   ├── stata-regression/
│   ├── research-discovery/
│   ├── chinese-literature/
│   ├── journal-submission-docx/
│   └── research-media-skill/
├── skill-bundles/
│   └── paper-workflow.yaml     # Hermes bundle 定义
├── install.sh                  # 一键安装脚本
├── scripts/sync_skills.py      # 同步脚本（Action 调用）
├── MANIFEST.md                 # 技能↔源仓库↔版本映射
└── .github/workflows/sync.yml  # 每日自动同步
```

## 维护说明

- **本仓库是镜像层**：技能内容只从源仓库单向同步，不在本仓库直接修改
- 修改某个技能 → 改它的源仓库 → 推送到 main → 等每日同步或手动触发 Action
- 新增配套技能 → 更新 `scripts/sync_skills.py` 的映射 + `install.sh` 的 SKILLS 列表 + bundle YAML + 本 README 表格

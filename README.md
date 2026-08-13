# paper-workflow-bundle

论文全流程技能全家桶聚合仓库：一个 tap 源装齐 `paper-workflow` 及其全部配套技能。

`paper-workflow`（8 阶段论文编排器）依赖 6 个配套技能才能完整运转。本仓库把 7 个技能聚合到单一 GitHub 仓库，支持：

1. **一键安装**：`hermes skills tap add` + 循环 `install`，一条命令装齐全家桶
2. **运行时 bundle**：`/paper-workflow` 一次加载全部 7 个技能
3. **自动同步**：GitHub Action 每日从各源仓库拉取最新版，聚合仓始终是最新镜像

## 快速安装

```bash
curl -fsSL https://raw.githubusercontent.com/MartyYao/paper-workflow-bundle/main/install.sh | bash
```

## 手动安装

```bash
# 1. 注册 tap（本仓库 skills/ 目录是技能源）
hermes skills tap add MartyYao/paper-workflow-bundle

# 2. 逐个安装（已安装的会自动跳过）
for skill in paper-workflow meng-skills stata-regression research-discovery \
             chinese-literature journal-submission-docx research-media-skill; do
  hermes skills install "MartyYao/paper-workflow-bundle/skills/$skill" --category research --yes
done

# 3. （可选）bundle 定义：/paper-workflow 一次加载全部
mkdir -p ~/.hermes/skill-bundles
curl -fsSL https://raw.githubusercontent.com/MartyYao/paper-workflow-bundle/main/skill-bundles/paper-workflow.yaml \
  -o ~/.hermes/skill-bundles/paper-workflow.yaml
```

## 使用方法

| 方式 | 命令/说法 | 效果 |
|------|-----------|------|
| 自然语言 | 「写论文」「开始写论文」「继续论文」 | 触发 paper-workflow 编排器 |
| 一次加载全部 | `/paper-workflow` | 7 个技能全部加载（bundle） |
| 单个技能 | `/stata-regression`、`/meng-skills` 等 | 只加载一个 |

## 配套技能清单

| 技能名 | 源仓库 | 用途 |
|--------|--------|------|
| paper-workflow | [paper-workflow-skill](https://github.com/MartyYao/paper-workflow-skill) | 8 阶段论文编排器（总调度） |
| meng-skills | [meng-skills](https://github.com/MartyYao/meng-skills) | 中文写作润色、去 AI 味 |
| stata-regression | [Stata-Regression-skill](https://github.com/MartyYao/Stata-Regression-skill) | Stata 编码规范、表格、出图 |
| research-discovery | [research-discovery-skill](https://github.com/MartyYao/research-discovery-skill) | 实证异常结果分层诊断 |
| chinese-literature | [Chinese-Literature-Skill](https://github.com/MartyYao/Chinese-Literature-Skill) | 中文文献检索（CNKI 双通道） |
| journal-submission-docx | [journal-submission-docx-skill](https://github.com/MartyYao/journal-submission-docx-skill) | 期刊投稿版 docx 生成（13 刊模板） |
| research-media-skill | [research-media-skill](https://github.com/MartyYao/research-media-skill) | 经管之家论坛实操方案检索 |

> 注：`aers-index`（本地 AERS 方法论库路由）依赖 `~/hermes/aers/` 本地仓库，不随本包分发。

## 更新

```bash
hermes skills update          # 更新所有 hub 安装的技能
# 或重新运行 install.sh（已安装的会跳过）
```

聚合仓库每日 UTC 0 点自动从各源仓库同步最新版（也可在 Actions 页手动触发 `sync-skills`）。

## 目录结构

```
paper-workflow-bundle/
├── skills/                     # tap 技能源（每技能一个文件夹）
│   ├── paper-workflow/         #   SKILL.md + references/ + scripts/ ...
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
- 新增配套技能 → 更新 `scripts/sync_skills.py` 的映射 + `install.sh` 的 SKILLS 列表 + 本 README 表格

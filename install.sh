#!/usr/bin/env bash
# paper-workflow 全家桶一键安装脚本
# 用法:
#   curl -fsSL https://raw.githubusercontent.com/MartyYao/paper-workflow-bundle/main/install.sh | bash
# 或本地: bash install.sh
#
# 为什么不用 hermes skills install（2026-08-13 用户反馈修订）：
#   1. GitHub API 未认证限额 60 次/小时——8 个技能逐个 install 一次装不完
#   2. registry 存在同名 paper-workflow（clawhub v0.1.0）——install 可能装错来源
# 本脚本直接下载聚合仓库 zip（codeload 静态 CDN，无 API 限制、不经过 registry），
# 解压拷贝到技能目录，并清理 .hub/lock.json 中的同名残留防止 update 降级。
#
# 安装内容:
#   1. 8 个技能（按类别拷贝到 ~/.hermes/skills/<类别>/）
#   2. bundle 定义（/paper-workflow 一次加载全部）
set -euo pipefail

BUNDLE_REPO="MartyYao/paper-workflow-bundle"
ZIP_URL="https://codeload.github.com/$BUNDLE_REPO/zip/refs/heads/main"
SKILLS_HOME="${HERMES_SKILLS_DIR:-$HOME/.hermes/skills}"
BUNDLES_HOME="${HERMES_SKILL_BUNDLES_DIR:-$HOME/.hermes/skill-bundles}"
TMPDIR_BAK="${TMPDIR:-/tmp}"

# 技能名 → 类别（与 Hermes 本地目录结构一致）。
# 注：macOS bash 3.2 不支持 declare -A，用两列字符串模拟。
CATS="paper-workflow:research research-topic:research meng-skills:writing stata-regression:research research-discovery:research chinese-literature:research journal-submission-docx:productivity research-media-skill:research"

cat_of() { printf '%s\n' "$CATS" | tr ' ' '\n' | grep "^$1:" | cut -d: -f2; }

die() { echo "ABORT: $*" >&2; exit 1; }

[ -d "$SKILLS_HOME" ] || die "技能目录不存在: ${SKILLS_HOME}（先安装 Hermes）"

echo "==> [1/3] 下载聚合仓库（zip 静态 CDN，无 API 限额）"
WORK_DIR="$TMPDIR_BAK/pw-bundle-install"
rm -rf "$WORK_DIR" && mkdir -p "$WORK_DIR"
curl -fsSL -o "$WORK_DIR/bundle.zip" "$ZIP_URL" || die "下载失败: ${ZIP_URL}（检查网络）"
# 用 Python zipfile 解压：macOS unzip 对 zip 内中文文件名（如 _通用CSSCI.md）有编码 bug
python3 - "$WORK_DIR/bundle.zip" "$WORK_DIR" <<'PYEOF'
import sys, zipfile
zf, out = sys.argv[1], sys.argv[2]
with zipfile.ZipFile(zf) as z:
    z.extractall(out)
PYEOF
SRC_DIR="$(find "$WORK_DIR" -maxdepth 1 -type d -name 'paper-workflow-bundle-*' | head -1 || true)"
[ -n "$SRC_DIR" ] || die "解压后找不到技能目录"

echo "==> [2/3] 安装 8 个技能"
for skill in paper-workflow research-topic meng-skills stata-regression research-discovery chinese-literature journal-submission-docx research-media-skill; do
  cat_="$(cat_of "$skill")"
  [ -n "$cat_" ] || die "未定义类别: $skill"
  src="$SRC_DIR/skills/$skill"
  [ -d "$src" ] || { echo "  ⚠️ 源目录缺失: ${src}（跳过）"; continue; }
  dst="$SKILLS_HOME/$cat_/$skill"
  mkdir -p "$SKILLS_HOME/$cat_"
  rm -rf "$dst"
  cp -R "$src" "$dst"
  ver="$(grep -m1 -E '^(version:|[[:space:]]+version:)' "$dst/SKILL.md" 2>/dev/null | sed -E 's/^[[:space:]]*version:[[:space:]]*//' || echo '?')"
  echo "  已安装: $skill (${ver:-无版本号}) → $cat_/"
done

echo "==> [2.5/3] 清理 registry 残留（防止 hermes skills update 降级）"
LOCK="$SKILLS_HOME/../.hub/lock.json"
if [ -f "$LOCK" ]; then
  python3 - "$LOCK" <<'PYEOF'
import json, sys
lock = sys.argv[1]
try:
    with open(lock) as f:
        data = json.load(f)
except Exception:
    sys.exit(0)
names = {"paper-workflow", "research-topic", "meng-skills", "stata-regression", "research-discovery",
         "chinese-literature", "journal-submission-docx", "research-media-skill"}
changed = False

def prune(obj):
    global changed
    if isinstance(obj, dict):
        for k in list(obj.keys()):
            if k in names and isinstance(obj[k], dict) and obj[k].get("source") == "clawhub":
                del obj[k]
                changed = True
            else:
                prune(obj[k])
    elif isinstance(obj, list):
        for item in obj:
            prune(item)

prune(data)
if changed:
    with open(lock, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("  已清理 lock.json 中 clawhub 同名残留（防止 update 降级到旧版）")
else:
    print("  lock.json 无 clawhub 残留（或文件结构未识别，跳过）")
PYEOF
else
  echo "  lock.json 不存在，跳过"
fi

echo "==> [3/3] 安装 bundle 定义（/paper-workflow 一次加载全家桶）"
mkdir -p "$BUNDLES_HOME"
cp "$SRC_DIR/skill-bundles/paper-workflow.yaml" "$BUNDLES_HOME/paper-workflow.yaml"
echo "  bundle 已写入 $BUNDLES_HOME/paper-workflow.yaml"

rm -rf "$WORK_DIR"

echo ""
echo "✅ 安装完成。使用方法："
echo "  · 直接说「写论文」「开始写论文」「继续论文」→ 自动触发 paper-workflow"
echo "  · 输入 /paper-workflow → 一次加载全部 8 个技能"
echo "  · 更新：重新运行本脚本（zip 覆盖，幂等）"
echo ""
echo "⚠️ 验证提示：hermes skills list 应显示 8 个 local 技能。"
echo "   paper-workflow 版本应 ≥ 0.5.0（grep version ~/.hermes/skills/research/paper-workflow/SKILL.md）"
echo "   research-topic 版本应为 0.2.0（grep version ~/.hermes/skills/research/research-topic/SKILL.md）"
echo "   若显示旧版（如 0.1.0），说明装到了 registry 同名技能，请 uninstall 后重跑本脚本。"

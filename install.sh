#!/usr/bin/env bash
# paper-workflow 全家桶一键安装脚本
# 用法:
#   curl -fsSL https://raw.githubusercontent.com/MartyYao/paper-workflow-bundle/main/install.sh | bash
# 或本地: bash install.sh
#
# 安装内容:
#   1. 注册 tap: MartyYao/paper-workflow-bundle
#   2. 安装 7 个配套技能（paper-workflow + 6 个依赖）
#   3. 安装 bundle 定义（/paper-workflow 一次加载全部）
set -euo pipefail

BUNDLE_REPO="MartyYao/paper-workflow-bundle"
SKILLS="paper-workflow meng-skills stata-regression research-discovery chinese-literature journal-submission-docx research-media-skill"

echo "==> [1/3] 注册 tap: $BUNDLE_REPO"
hermes skills tap add "$BUNDLE_REPO" || echo "（tap 可能已存在，继续）"

echo "==> [2/3] 安装 7 个技能（已装过的会自动跳过）"
for skill in $SKILLS; do
  if hermes skills list 2>/dev/null | grep -qw "$skill"; then
    echo "  已安装: $skill（跳过）"
  else
    echo "  安装: $skill"
    hermes skills install "$BUNDLE_REPO/skills/$skill" --category research --yes \
      || echo "  ⚠️ $skill 安装失败，请手动安装: hermes skills install $BUNDLE_REPO/skills/$skill"
  fi
done

echo "==> [3/3] 安装 bundle 定义（/paper-workflow 一次加载全家桶）"
mkdir -p ~/.hermes/skill-bundles
if curl -fsSL "https://raw.githubusercontent.com/$BUNDLE_REPO/main/skill-bundles/paper-workflow.yaml" -o ~/.hermes/skill-bundles/paper-workflow.yaml; then
  echo "  bundle 已写入 ~/.hermes/skill-bundles/paper-workflow.yaml"
else
  echo "  ⚠️ bundle 下载失败，可稍后手动执行上述 curl 命令"
fi

echo ""
echo "✅ 安装完成。使用方法："
echo "  · 直接说「写论文」「开始写论文」→ 自动触发 paper-workflow"
echo "  · 输入 /paper-workflow → 一次加载全部配套技能"
echo "  · 更新: hermes skills update"

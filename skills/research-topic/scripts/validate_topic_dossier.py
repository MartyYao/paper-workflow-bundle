#!/usr/bin/env python3
"""Validate the structural and decision-gate completeness of a topic dossier."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_HEADINGS = [
    "## 1. 研究问题",
    "## 2. 现实观察与研究谜题",
    "## 3. 文献共识",
    "## 4. 空白证据",
    "## 5. 创新与贡献价值",
    "## 6. 研究逻辑",
    "## 7. 可行性审计",
    "## 8. 竞争性解释与证伪",
    "## 9. 质量护栏",
    "## 10. 决策",
]

REQUIRED_MARKERS = [
    "### 空白成因诊断",
    "### 版图位置与检索覆盖",
    "来源谜题：",
    "- X：",
    "- Y：",
    "- M：",
]

REQUIRED_FIELDS = [
    "来源谜题",
    "大问题",
    "制度矛盾",
    "文献事实",
    "文献证据台账 record_id",
    "不能解释之处",
    "未决问题证据 record_id",
    "所属研究分支",
    "精确文献数量及状态",
    "邻近文献数量及状态",
    "覆盖范围和限制",
    "空白状态",
    "已有研究知道什么",
    "仍然不知道什么",
    "检索边界和不确定性",
    "代表性来源",
    "主要空白成因",
    "成因证据",
    "成因证据类型/等级",
    "障碍是否可克服",
    "X 数量",
    "X 类型",
    "X",
    "Y 数量",
    "Y 类型",
    "Y",
    "M",
    "分析单位",
    "时间范围",
    "单向主线",
    "核心数据来源和状态",
    "X 的实际构造与处理组/控制组",
    "Y 的实际构造和替代口径",
    "处理变异、时点和集群数量",
    "决策依据",
    "下一步最小验证",
]

VALID_STATUSES = {"GO", "HOLD", "KILL"}
VALID_X_TYPES = {"government-action"}
VALID_Y_TYPES = {"firm-level"}
VALID_GAP_STATES = {"OCCUPIED", "ADJACENT", "OPEN-WITHIN-BOUNDARY", "UNKNOWN"}
PLACEHOLDER_PREFIXES = (
    "YYYY",
    "一个政府行为",
    "一个企业结果",
    "最小必要机制",
    "研究启发报告中的编号",
    "数据 /",
    "是 / 否",
    "通过 /",
    "待核验",
)
COMPOSITE_Y_PATTERNS = (
    r"就业\s*[+、和与及]\s*创新",
    r"创新\s*[+、和与及]\s*就业",
    r"就业\s*[+、和与及]\s*分红",
    r"就业\s*[+、和与及]\s*投资",
    r"民生责任",
    r"社会使命",
)


def field_values(text: str, label: str) -> list[str]:
    """Return values for exact top-level bullet fields such as ``- X：...``."""

    pattern = rf"^[ \t]*-[ \t]*{re.escape(label)}：[ \t]*(.*?)[ \t]*$"
    return [match.group(1).strip() for match in re.finditer(pattern, text, flags=re.MULTILINE)]


def is_placeholder(value: str) -> bool:
    if not value:
        return True
    if value in {"...", "…", "待填写", "待补充", "暂无"}:
        return True
    return value.startswith(PLACEHOLDER_PREFIXES)


def require_filled_field(text: str, label: str, errors: list[str]) -> str | None:
    values = field_values(text, label)
    if not values:
        errors.append(f"missing field: {label}")
        return None
    value = values[-1]
    if is_placeholder(value):
        errors.append(f"empty or placeholder field: {label}")
        return None
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()

    if not args.path.is_file():
        print(f"ERROR: dossier not found: {args.path}")
        return 2

    text = args.path.read_text(encoding="utf-8")
    errors = [heading for heading in REQUIRED_HEADINGS if heading not in text]
    errors.extend(marker for marker in REQUIRED_MARKERS if marker not in text)

    for label in REQUIRED_FIELDS:
        require_filled_field(text, label, errors)

    statuses = field_values(text, "状态")
    if not statuses:
        errors.append("missing field: 状态")
        selected_status = None
    else:
        invalid_statuses = [status for status in statuses if status not in VALID_STATUSES]
        errors.extend(f"invalid 状态: {status!r}" for status in invalid_statuses)
        selected_status = statuses[-1] if statuses[-1] in VALID_STATUSES else None
        if len(set(statuses)) > 1 and all(status in VALID_STATUSES for status in statuses):
            errors.append("状态 differs between dossier header and decision section")

    x_count = field_values(text, "X 数量")
    if x_count and x_count[-1] != "1":
        errors.append(f"X 数量 must be 1, got {x_count[-1]!r}")
    x_type = field_values(text, "X 类型")
    if x_type and x_type[-1] not in VALID_X_TYPES:
        errors.append(f"X 类型 must be government-action, got {x_type[-1]!r}")

    y_count = field_values(text, "Y 数量")
    if y_count and y_count[-1] != "1":
        errors.append(f"Y 数量 must be 1, got {y_count[-1]!r}")
    y_type = field_values(text, "Y 类型")
    if y_type and y_type[-1] not in VALID_Y_TYPES:
        errors.append(f"Y 类型 must be firm-level, got {y_type[-1]!r}")

    y_values = field_values(text, "Y")
    if y_values and any(re.search(pattern, y_values[-1]) for pattern in COMPOSITE_Y_PATTERNS):
        errors.append("Y appears to be a composite social/firm outcome; retain one firm-level outcome")

    gap_states = field_values(text, "空白状态")
    if gap_states and gap_states[-1] not in VALID_GAP_STATES:
        errors.append(f"invalid 空白状态: {gap_states[-1]!r}")

    if selected_status == "GO":
        if not gap_states or gap_states[-1] != "OPEN-WITHIN-BOUNDARY":
            errors.append("GO requires 空白状态=OPEN-WITHIN-BOUNDARY")

        obstacle = field_values(text, "障碍是否可克服")
        if not obstacle or obstacle[-1].lower() not in {"是", "yes"}:
            errors.append("GO requires 障碍是否可克服=是")

        for label in ("最小可行模型", "识别假设"):
            require_filled_field(text, label, errors)

        confirmation = field_values(text, "用户确认")
        if not confirmation or confirmation[-1] not in {"是", "yes"}:
            errors.append("GO requires 用户确认=是")

    if errors:
        print("INVALID: topic dossier checks failed:")
        for item in errors:
            print(f"- {item}")
        return 1

    print(f"VALID: {args.path} ({selected_status})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Validate the structural completeness of a research-topic candidate dossier."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REQUIRED_HEADINGS = [
    "## 1. 研究问题",
    "## 3. 文献共识",
    "## 4. 空白证据",
    "## 5. 创新与贡献价值",
    "## 6. 研究逻辑",
    "## 7. 可行性审计",
    "## 8. 竞争性解释与证伪",
    "## 9. 质量护栏",
    "## 10. 决策",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()

    if not args.path.is_file():
        print(f"ERROR: dossier not found: {args.path}")
        return 2

    text = args.path.read_text(encoding="utf-8")
    errors = [heading for heading in REQUIRED_HEADINGS if heading not in text]

    if "状态：" not in text and "状态:" not in text:
        errors.append("状态：GO / HOLD / KILL")
    if not any(token in text for token in ("GO", "HOLD", "KILL")):
        errors.append("GO / HOLD / KILL")

    if errors:
        print("INVALID: missing required dossier fields:")
        for item in errors:
            print(f"- {item}")
        return 1

    print(f"VALID: {args.path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Validate the required columns and basic provenance of the evidence ledger."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


REQUIRED_COLUMNS = {
    "record_id",
    "language",
    "source",
    "search_date",
    "query",
    "title",
    "evidence_role",
    "screen_status",
}
VALID_ROLES = {"support", "challenge", "limit", "context"}
VALID_STATUS = {"included", "excluded", "uncertain"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()

    if not args.path.is_file():
        print(f"ERROR: ledger not found: {args.path}")
        return 2

    with args.path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        missing = sorted(REQUIRED_COLUMNS - columns)
        if missing:
            print("INVALID: missing columns: " + ", ".join(missing))
            return 1

        rows = list(reader)

    errors: list[str] = []
    ids: set[str] = set()
    roles: set[str] = set()
    for line_no, row in enumerate(rows, start=2):
        record_id = row.get("record_id", "").strip()
        if not record_id:
            errors.append(f"line {line_no}: empty record_id")
        elif record_id in ids:
            errors.append(f"line {line_no}: duplicate record_id {record_id}")
        ids.add(record_id)

        for field in ("language", "source", "search_date", "query", "title"):
            if not row.get(field, "").strip():
                errors.append(f"line {line_no}: empty {field}")

        role = row.get("evidence_role", "").strip()
        roles.add(role)
        if role not in VALID_ROLES:
            errors.append(f"line {line_no}: invalid evidence_role {role!r}")

        status = row.get("screen_status", "").strip()
        if status not in VALID_STATUS:
            errors.append(f"line {line_no}: invalid screen_status {status!r}")

    if not rows:
        errors.append("ledger has no records")
    for role in ("support", "challenge", "limit"):
        if role not in roles:
            errors.append(f"ledger has no {role} evidence")

    if errors:
        print("INVALID: evidence ledger checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"VALID: {args.path} ({len(rows)} records)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

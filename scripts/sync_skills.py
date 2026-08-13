#!/usr/bin/env python3
"""同步各源仓库的最新技能到聚合仓库 skills/ 目录。

- 源：各独立技能 repo 的 raw.githubusercontent（main 分支）
- 目标：skills/<skill-name>/（SKILL.md + references/templates/scripts/assets/examples）
- 幂等：内容无变化时不产生 git diff（由 Action 的 git diff --quiet 判断是否提交）
"""
import hashlib
import os
import re
import sys
import urllib.parse
import urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(BASE, "skills")
GITHUB = "https://raw.githubusercontent.com/MartyYao"

# skill-name -> (源 repo, 需要拷贝的子目录)
SOURCES = {
    "paper-workflow": ("paper-workflow-skill", ["references"]),
    "meng-skills": ("meng-skills", ["references"]),
    "stata-regression": ("Stata-Regression-skill", ["references", "templates", "scripts", "assets"]),
    "research-discovery": ("research-discovery-skill", []),
    "chinese-literature": ("Chinese-Literature-Skill", ["references", "scripts"]),
    "journal-submission-docx": ("journal-submission-docx-skill", ["references", "templates", "scripts"]),
    "research-media-skill": ("research-media-skill", ["scripts"]),
}
SUBDIRS = ["references", "templates", "scripts", "assets", "examples"]


def fetch(url: str) -> bytes:
    url = urllib.parse.quote(url, safe="/:?=&%")
    req = urllib.request.Request(url, headers={"User-Agent": "paper-workflow-bundle-sync"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def list_repo_files(repo: str) -> list[str]:
    """通过 GitHub API 列出 repo 全部文件路径"""
    url = f"https://api.github.com/repos/MartyYao/{repo}/git/trees/HEAD?recursive=1"
    data = fetch(url)
    import json
    tree = json.loads(data).get("tree", [])
    return [t["path"] for t in tree if t["type"] == "blob"]


def sync_skill(skill: str, repo: str, keep_dirs: list[str]) -> None:
    dst = os.path.join(SKILLS_DIR, skill)
    os.makedirs(dst, exist_ok=True)
    changed = False

    # SKILL.md（必须）
    content = fetch(f"{GITHUB}/{repo}/main/SKILL.md")
    m = re.search(rb"^version:\s*(\S+)", content, re.M)
    ver = m.group(1).decode() if m else "-"
    old = b""
    if os.path.exists(os.path.join(dst, "SKILL.md")):
        old = open(os.path.join(dst, "SKILL.md"), "rb").read()
    if hashlib.sha256(old).hexdigest() != hashlib.sha256(content).hexdigest():
        with open(os.path.join(dst, "SKILL.md"), "wb") as f:
            f.write(content)
        changed = True

    # 子目录：删除不再需要的、更新变化的
    for sub in SUBDIRS:
        subdst = os.path.join(dst, sub)
        if sub not in keep_dirs:
            if os.path.isdir(subdst):
                import shutil
                shutil.rmtree(subdst)
                changed = True
            continue
        files = [p for p in list_repo_files(repo) if p.startswith(f"{sub}/")]
        os.makedirs(subdst, exist_ok=True)
        # 删除本地多余文件
        local = set()
        for root, _, fs in os.walk(subdst):
            for f in fs:
                local.add(os.path.relpath(os.path.join(root, f), subdst))
        for f in local:
            if f not in {p[len(sub) + 1:] for p in files}:
                os.remove(os.path.join(subdst, f))
                changed = True
        # 更新/新增
        for p in files:
            rel = p[len(sub) + 1:]
            out = os.path.join(subdst, rel)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            content = fetch(f"{GITHUB}/{repo}/main/{p}")
            old = b""
            if os.path.exists(out):
                old = open(out, "rb").read()
            if hashlib.sha256(old).hexdigest() != hashlib.sha256(content).hexdigest():
                with open(out, "wb") as f:
                    f.write(content)
                changed = True

    # 版本标注到 MANIFEST
    return changed, ver


def main() -> None:
    changed_any = False
    lines = ["| 技能名 | 源仓库 | 版本 |", "|--------|--------|------|"]
    for skill, (repo, keep_dirs) in SOURCES.items():
        try:
            changed, ver = sync_skill(skill, repo, keep_dirs)
            changed_any = changed_any or changed
            lines.append(f"| {skill} | {repo} | {ver} |")
            print(f"{'✓' if changed else '='} {skill} ({ver})")
        except Exception as e:  # noqa: BLE001
            print(f"✗ {skill}: {e}", file=sys.stderr)
            sys.exit(1)
    with open(os.path.join(BASE, "MANIFEST.md"), "w") as f:
        f.write("# MANIFEST — 技能 ↔ 源仓库映射\n\n")
        f.write("> 由 scripts/sync_skills.py 自动生成，请勿手改。\n\n")
        f.write("\n".join(lines) + "\n")
    print(f"\n同步完成，{'有变更' if changed_any else '无变更'}")


if __name__ == "__main__":
    main()

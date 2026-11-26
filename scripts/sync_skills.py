#!/usr/bin/env python3
"""
sync_skills.py — Audit all 14 UPPERCASE flagship skills (+ optional GitHub parity check).

Zero external dependencies (Python 3.10+ stdlib).
Checks each flagship skill for:
  1. Directory existence & SKILL.md YAML frontmatter (`name:` matches folder, `description:` present)
  2. Standardized README.md presence
  3. Zero leaked secrets or hardcoded user/project strings
  4. Optional `--check-github`: verifies public visibility & latest commit via `gh api`
"""

from __future__ import annotations

import argparse
import getpass
import json
import re
import subprocess
import sys
from pathlib import Path

FLAGSHIP_SKILLS = [
    "DIRECTOR",
    "SAMURAI",
    "STUDIO",
    "SCRIBE",
    "KITSUNE",
    "PRISM",
    "KAGAMI",
    "FORGE",
    "TITAN",
    "XRAY",
    "NOVA",
    "PILOT",
    "WARP",
    "STACK",
]

_ACTIVE_USER = re.escape(getpass.getuser())

SECRET_PATTERNS = [
    ("sk_live", re.compile(r"sk_live_[A-Za-z0-9]+")),
    ("sk_test", re.compile(r"sk_test_[A-Za-z0-9]+")),
    ("sk-proj", re.compile(r"sk-proj-[A-Za-z0-9_-]+")),
    ("ghp_token", re.compile(r"ghp_[A-Za-z0-9]{20,}")),
    ("gho_token", re.compile(r"gho_[A-Za-z0-9]{20,}")),
    ("google_api_key", re.compile(r"AIza[0-9A-Za-z\-_]{20,}")),
    ("aws_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("slack_token", re.compile(r"xoxb-[0-9A-Za-z-]+")),
    ("hardcoded_user_path", re.compile(rf"(?:C:\\\\?Users\\\\|/Users/|/home/){_ACTIVE_USER}(?:[/\\\\]|$)", re.IGNORECASE)),
]

TEXT_EXTENSIONS = {".md", ".py", ".ps1", ".sh", ".js", ".ts", ".json", ".yaml", ".yml", ".toml", ".html", ".css"}


def parse_frontmatter(skill_md: Path) -> tuple[str | None, str | None]:
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.DOTALL)
    if not m:
        return None, None
    fm = m.group(1)
    name_m = re.search(r"^name:\s*(.+?)\s*$", fm, re.MULTILINE)
    desc_m = re.search(r"^description:\s*(.+?)\s*$", fm, re.MULTILINE)
    return (name_m.group(1) if name_m else None), (desc_m.group(1) if desc_m else None)


def scan_secrets(skill_dir: Path) -> list[str]:
    hits: list[str] = []
    for p in skill_dir.rglob("*"):
        if not p.is_file() or "__pycache__" in p.parts:
            continue
        if p.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        content = p.read_text(encoding="utf-8", errors="replace")
        for label, rx in SECRET_PATTERNS:
            for match in rx.finditer(content):
                rel = p.relative_to(skill_dir)
                hits.append(f"{rel} [{label}]")
                break
    return hits


def check_github(owner: str, repo: str) -> tuple[bool, str]:
    try:
        res = subprocess.run(
            ["gh", "api", f"repos/{owner}/{repo}", "--jq", "{private: .private, pushed_at: .pushed_at, branch: .default_branch}"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if res.returncode != 0:
            return False, res.stderr.strip() or f"gh exit {res.returncode}"
        info = json.loads(res.stdout)
        vis = "PRIVATE" if info.get("private") else "PUBLIC"
        sha_res = subprocess.run(
            ["gh", "api", f"repos/{owner}/{repo}/commits/{info.get('branch', 'main')}", "--jq", ".sha[0:7]"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        sha = sha_res.stdout.strip() if sha_res.returncode == 0 else "???????"
        return True, f"{vis} @ {sha}"
    except Exception as exc:
        return False, str(exc)


def main() -> int:
    default_dir = Path.home() / ".gemini" / "config" / "skills"
    parser = argparse.ArgumentParser(description="Audit all 13 UPPERCASE flagship skills (+ optional GitHub sync check)")
    parser.add_argument("--skills-dir", type=Path, default=default_dir, help="Path to skills root directory")
    parser.add_argument("--owner", default="triwahyu45", help="GitHub owner for --check-github")
    parser.add_argument("--check-github", action="store_true", help="Verify remote visibility and HEAD commit via gh CLI")
    args = parser.parse_args()

    skills_dir: Path = args.skills_dir
    if not skills_dir.is_dir():
        print(f"ERROR: skills directory not found: {skills_dir}", file=sys.stderr)
        return 1

    failures = 0
    print(f"Auditing {len(FLAGSHIP_SKILLS)} flagship skills in: {skills_dir}\n")

    for name in FLAGSHIP_SKILLS:
        sdir = skills_dir / name
        issues: list[str] = []

        if not sdir.is_dir():
            issues.append("missing folder")
        else:
            skill_md = sdir / "SKILL.md"
            readme = sdir / "README.md"
            if not skill_md.is_file():
                issues.append("missing SKILL.md")
            else:
                fm_name, fm_desc = parse_frontmatter(skill_md)
                if fm_name != name:
                    issues.append(f"frontmatter name={fm_name!r} != {name!r}")
                if not fm_desc:
                    issues.append("missing frontmatter description")
            if not readme.is_file():
                issues.append("missing README.md")
            secret_hits = scan_secrets(sdir)
            if secret_hits:
                issues.append("security hits: " + ", ".join(secret_hits))

        gh_note = ""
        if args.check_github:
            ok, msg = check_github(args.owner, name)
            if not ok:
                issues.append(f"github check failed: {msg}")
            else:
                gh_note = f" | GitHub: {msg}"

        if issues:
            failures += 1
            print(f"  [FAIL] {name.ljust(10)} -> {'; '.join(issues)}{gh_note}")
        else:
            print(f"  [PASS] {name.ljust(10)} -> clean{gh_note}")

    if args.check_github:
        ok, msg = check_github(args.owner, "NINGYO")
        status = "PASS" if ok else "FAIL"
        if not ok:
            failures += 1
        print(f"  [{status}] {'NINGYO'.ljust(10)} -> MCP repo | GitHub: {msg}")

    print(f"\nSummary: {len(FLAGSHIP_SKILLS) + (1 if args.check_github else 0) - failures} passed, {failures} failed")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

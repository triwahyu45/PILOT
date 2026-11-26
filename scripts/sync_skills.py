#!/usr/bin/env python3
"""
sync_skills.py — Two-layer pre-push security & sync audit for all 14 UPPERCASE flagship skills.

Zero external dependencies (Python 3.10+ stdlib).
Layer 1: Deep secret, credential, token, and personal/agent-config path scan + frontmatter/README check.
Layer 2 (`--skillspector`): NVIDIA SkillSpector static audit (fails on any CRITICAL or actionable HIGH).
Optional (`--check-github`): Verifies public visibility & latest commit via `gh api`.
"""

from __future__ import annotations

import argparse
import getpass
import json
import re
import shutil
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
    ("sk_live", re.compile(r"sk_live_[A-Za-z0-9]{10,}")),
    ("sk_test", re.compile(r"sk_test_[A-Za-z0-9]{10,}")),
    ("sk-proj", re.compile(r"sk-proj-[A-Za-z0-9_-]{10,}")),
    ("sk-ant", re.compile(r"sk-ant-[A-Za-z0-9_-]{10,}")),
    ("sk_user", re.compile(r"sk_user_[A-Za-z0-9_-]{10,}")),
    ("ghp_token", re.compile(r"ghp_[A-Za-z0-9]{20,}")),
    ("gho_token", re.compile(r"gho_[A-Za-z0-9]{20,}")),
    ("github_pat", re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
    ("google_api_key", re.compile(r"AIza[0-9A-Za-z\-_]{20,}")),
    ("aws_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("slack_token", re.compile(r"xox[baprs]-[0-9A-Za-z-]{10,}")),
    ("bearer_token", re.compile(r"Bearer\s+(?![{<$])[A-Za-z0-9._\-]{16,}")),
    ("telegram_bot_token", re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b")),
    ("discord_webhook", re.compile(r"https://(?:ptb\.|canary\.)?discord(?:app)?\.com/api/webhooks/\d+/[A-Za-z0-9_-]+")),
    ("pem_private_key", re.compile(r"-{5}BEGIN (?:RSA |EC |OPENSSH |PGP |DSA )?PRIVATE " + r"KEY-{5}")),
    (
        "hardcoded_secret_assign",
        re.compile(
            r"""(?i)\b(?:api[_-]?key|client[_-]?secret|access[_-]?token|auth[_-]?token|password|passwd|private[_-]?key)\b\s*[:=]\s*["'](?!<|\$|\{|your[_-]|example|placeholder|changeme|dummy|test|none|null)[^"'\r\n]{12,}["']"""
        ),
    ),
    ("hardcoded_user_path", re.compile(rf"(?:C:\\\\?Users\\\\|/Users/|/home/){_ACTIVE_USER}(?:[/\\\\]|$)", re.IGNORECASE)),
    ("agent_config_snooping", re.compile(r"(?:~|%USERPROFILE%)[/\\\\]\." + r"gemini[/\\\\]config", re.IGNORECASE)),
]

TEXT_EXTENSIONS = {".md", ".py", ".ps1", ".sh", ".js", ".ts", ".json", ".yaml", ".yml", ".toml", ".html", ".css"}
VENDORED_AE1_FILES = {"engine/three.min.js", "engine/samurai-core.js"}


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
    self_path = Path(__file__).resolve()
    for p in skill_dir.rglob("*"):
        if not p.is_file() or "__pycache__" in p.parts:
            continue
        if p.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        if p.resolve() == self_path:
            continue
        content = p.read_text(encoding="utf-8", errors="replace")
        for label, rx in SECRET_PATTERNS:
            if rx.search(content):
                rel = p.relative_to(skill_dir)
                hits.append(f"{rel} [{label}]")
    return hits


def find_skillspector() -> str | None:
    found = shutil.which("skillspector") or shutil.which("skillspector.exe")
    if found:
        return found
    candidate = Path.home() / ".local" / "bin" / "skillspector.exe"
    return str(candidate) if candidate.is_file() else None


def run_skillspector(exe: str, skill_dir: Path, allow_vendored_ae1: bool) -> tuple[bool, str, list[str]]:
    try:
        res = subprocess.run(
            [exe, "scan", str(skill_dir), "--no-llm", "--format", "json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )
        raw = res.stdout or res.stderr or ""
        idx = raw.find("{")
        if idx < 0:
            return False, f"SkillSpector returned non-JSON output (exit {res.returncode})", []
        data = json.loads(raw[idx:])
        risk = data.get("risk_assessment", {})
        issues = data.get("issues", [])
        blocking: list[str] = []
        for iss in issues:
            sev = str(iss.get("severity", "")).upper()
            iss_id = str(iss.get("id", ""))
            loc = iss.get("location", {}) or {}
            fpath = str(loc.get("file", "")).replace("\\", "/")
            line = loc.get("start_line", "?")
            finding = str(iss.get("finding", ""))
            if sev in {"CRITICAL", "HIGH"}:
                if allow_vendored_ae1 and iss_id == "AE1" and any(v in finding or v == fpath for v in VENDORED_AE1_FILES):
                    continue
                blocking.append(f"[{sev}] {iss_id} | {fpath}:{line} -> {finding}")
        summary = f"SS={risk.get('score', '?')}/{risk.get('severity', '?')}"
        return len(blocking) == 0, summary, blocking
    except Exception as exc:
        return False, f"SkillSpector error: {exc}", []


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
    parser = argparse.ArgumentParser(description="Two-layer pre-push security & GitHub sync audit for flagship skills")
    parser.add_argument("--skills-dir", type=Path, default=default_dir, help="Path to skills root directory")
    parser.add_argument("--skill", default="", help="Comma-separated skill names to audit (default: all 14)")
    parser.add_argument("--owner", default="triwahyu45", help="GitHub owner for --check-github")
    parser.add_argument("--skillspector", action="store_true", help="Run NVIDIA SkillSpector static audit (fails on CRITICAL/HIGH)")
    parser.add_argument("--allow-vendored-ae1", action="store_true", help="Allow AE1 static_parse_limit on SAMURAI vendored JS")
    parser.add_argument("--check-github", action="store_true", help="Verify remote visibility and HEAD commit via gh CLI")
    args = parser.parse_args()

    skills_dir: Path = args.skills_dir
    if not skills_dir.is_dir():
        print(f"ERROR: skills directory not found: {skills_dir}", file=sys.stderr)
        return 1

    if args.skill:
        chosen = [s.strip().upper() for s in args.skill.split(",") if s.strip()]
    else:
        chosen = list(FLAGSHIP_SKILLS)

    sp_exe = None
    if args.skillspector:
        sp_exe = find_skillspector()
        if not sp_exe:
            print("ERROR: skillspector executable not found on PATH or ~/.local/bin/skillspector.exe", file=sys.stderr)
            return 1

    failures = 0
    print(f"Auditing {len(chosen)} flagship skill(s) in: {skills_dir}\n")

    for name in chosen:
        sdir = skills_dir / name
        issues: list[str] = []
        notes: list[str] = []

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

            if sp_exe:
                sp_ok, sp_sum, sp_block = run_skillspector(sp_exe, sdir, args.allow_vendored_ae1)
                notes.append(sp_sum)
                if not sp_ok:
                    issues.append("SkillSpector: " + " | ".join(sp_block) if sp_block else sp_sum)

        if args.check_github:
            ok, msg = check_github(args.owner, name)
            if not ok:
                issues.append(f"github check failed: {msg}")
            else:
                notes.append(f"GitHub: {msg}")

        note_str = (" | " + " | ".join(notes)) if notes else ""
        if issues:
            failures += 1
            print(f"  [FAIL] {name.ljust(10)} -> {'; '.join(issues)}{note_str}")
        else:
            print(f"  [PASS] {name.ljust(10)} -> clean{note_str}")

    if args.check_github and not args.skill:
        ok, msg = check_github(args.owner, "NINGYO")
        status = "PASS" if ok else "FAIL"
        if not ok:
            failures += 1
        print(f"  [{status}] {'NINGYO'.ljust(10)} -> MCP repo | GitHub: {msg}")

    total = len(chosen) + (1 if (args.check_github and not args.skill) else 0)
    print(f"\nSummary: {total - failures} passed, {failures} failed")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

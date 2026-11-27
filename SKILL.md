---
name: PILOT
description: Enforces strict workspace directory cleanliness (isolating scratch scripts, installers, and temp files) and preserves project state, milestones, and handoff continuity across multi-session chats. Use on every project workspace to keep roots clean and resume work seamlessly.
---

# Workspace Autopilot

Combines **Workspace Cleanliness** (`references/cleanliness-rules.md`) with **Cross-Session Continuity** (`references/continuity-protocol.md`) so every project stays clutter-free and resumable across chat sessions.

---

## Core Rules & One-Click Audit

- **Mandatory Two-Layer Pre-Push Gate**: Before ANY public GitHub push, run `python scripts/sync_skills.py --skill <NAME> --skillspector` (deep secret/token/path scan + NVIDIA SkillSpector 0 `CRITICAL`/`HIGH` audit; add `--allow-vendored-ae1` only for `SAMURAI`).
- **Full Sync Verification**: Run `python scripts/sync_skills.py --check-github` to validate all 18 flagship skills + `NINGYO` against GitHub.
- **Sync `ARSENAL` Hub**: Whenever adding a new flagship skill or shipping a major upgrade, update `triwahyu45/ARSENAL` (`README.md`, `install.ps1`, `install.sh`) so installers and catalog stay in sync.

1. **Zero Root Clutter**: Never drop temporary `.py`, `.ps1`, `.bat`, `.sh`, or test artifacts into workspace roots; isolate them in the designated scratch directory.
2. **Session Continuity**: On new chats in an active project, check existing handoff/state docs first; on major milestones, update project state cleanly so the next session resumes with zero lost context.
3. **Skill Routing & Short Flagship Naming**: Merge domain knowledge into the matching 1-word UPPERCASE flagship skill (`references/`) when relevant; **create a new standalone 1-word ALL-CAPS flagship skill** whenever a learned domain is genuinely unrelated to all existing skills (never create long hyphenated standalone global skill folders).
4. **Mandatory Post-Study Media & Clone Cleanup**: Immediately delete temporary downloaded study videos/audio (`.mp4`, `.wav`, raw frames, `.info.json`) and temporary `gh_push*` git clone directories after finishing skill absorption or push so disk stays clean.

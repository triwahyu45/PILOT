---
name: pilot
description: Enforces strict workspace directory cleanliness (isolating scratch scripts, installers, and temp files) and preserves project state, milestones, and handoff continuity across multi-session chats. Use on every project workspace to keep roots clean and resume work seamlessly.
---

# Workspace Autopilot

Combines **Workspace Cleanliness** (`references/cleanliness-rules.md`) with **Cross-Session Continuity** (`references/continuity-protocol.md`) so every project stays clutter-free and resumable across chat sessions.

---

## Core Rules

1. **Zero Root Clutter**: Never drop temporary `.py`, `.ps1`, `.bat`, `.sh`, or test artifacts into workspace roots; isolate them in the designated scratch directory.
2. **Session Continuity**: On new chats in an active project, check existing handoff/state docs first; on major milestones, update project state cleanly so the next session resumes with zero lost context.

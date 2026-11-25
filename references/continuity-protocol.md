---
name: workspace-continuity
description: Preserves, discovers, and synchronizes project state and conversation handoffs across multiple chat sessions in the same workspace. Triggers whenever starting a new conversation in an active project workspace, asking "what did we do last time", handing off tasks to a fresh chat, or updating workspace milestones.
---

# Workspace Continuity & Cross-Conversation Memory

Maintains seamless continuity between different conversations within the same workspace. Prevents the agent from starting from scratch ("ngawang") in fresh chats, allowing it to instantly know what was built, what problems were solved, and what task comes next.

---

## Scope & Trigger Context

- **Trigger Keywords**: "lanjutkan", "terakhir kita ngapain", "apa konteks workspace ini", "pindah chat", "ganti conversation", "new chat handoff", "workspace state", "resume previous work".
- **Trigger Events**:
  1. **Session Start (Turn 1)** in any workspace that has existing files or `.agents/WORKSPACE_STATE.md`.
  2. **Session Handoff**: When user prepares to open a fresh conversation or compact context.
  3. **Milestone Reached**: When major architectural decisions, bug fixes, or features are completed.

---

## Verified Paths, Commands & Schemas

| Purpose | Verified Path / Command | Behavior |
| :--- | :--- | :--- |
| **Workspace State File** | `<workspace>/.agents/WORKSPACE_STATE.md` | Persistent project memory loaded across chats |
| **Fallback Workspace Rules** | `<workspace>/AGENTS.md` or `.agents/rules/*.md` | Directory-level guidance |
| **Global Conversation DB** | `C:\Users\hando\.gemini\antigravity\conversation_summaries.db` | Antigravity's internal SQLite database indexing all conversation summaries |
| **Workspace Summary Query** | See [references/query-conversations.md](./references/query-conversations.md) | Token-safe lookup of last 3 conversations in workspace |

---

## Proven Fast-Path Workflows

### 1. Turn-1 Context Discovery (When starting a new conversation)
1. Check if `<workspace>/.agents/WORKSPACE_STATE.md` exists:
   - If **exists**: Read the top section (Milestones, Current Focus, Next Actions).
   - Immediately summarize to the user in 1-2 sentences: *"Melanjutkan dari milestone sebelumnya: [ringkasan]. Task berikutnya adalah [task]. Apakah ingin langsung kita eksekusi?"*
2. If **not found** but workspace has files:
   - Run the fast query script in [references/query-conversations.md](./references/query-conversations.md) to fetch the latest conversation titles and summaries matching the workspace path.
   - If a previous conversation exists, bootstrap `.agents/WORKSPACE_STATE.md` using [references/state-schema.md](./references/state-schema.md).

### 2. Live Milestone Sync (During ongoing conversation)
- Whenever a major component, migration, or fix is verified:
  - Append or update the `### Active Milestone` and `### Next Steps` in `<workspace>/.agents/WORKSPACE_STATE.md`.
  - Keep the update ultra-lean (3–5 bullet points max).

### 3. Pre-Handoff Bridge (Before user switches to a fresh chat)
- When conversation context is getting long or user says *"kita lanjut di chat baru"*:
  1. Run the handoff routine detailed in [references/handoff-protocol.md](./references/handoff-protocol.md).
  2. Write the exact pending task, unfinished items, and key decisions into `<workspace>/.agents/WORKSPACE_STATE.md`.
  3. Inform the user: *"State workspace sudah saya update di `.agents/WORKSPACE_STATE.md`. Di chat baru nanti, saya akan otomatis langsung melanjutkan dari titik ini."*

---

## Dead-Ends, Pitfalls & Verified Fixes

- `[Dumping whole past transcripts]` -> `[Context bloat & token waste]` -> `[Only read/write concise 15-20 line state summaries in .agents/WORKSPACE_STATE.md]`.
- `[Relying only on in-memory chat history]` -> `[Lost completely on new conversation click]` -> `[Always persist state to disk inside <workspace>/.agents/]`.
- `[Manual user copying between chats]` -> `[High friction and forgotten details]` -> `[Automate via Turn-1 file check and Pre-Handoff sync]`.

---

## Token-Saving Shortcuts

- **Lazy Read:** Read only the first 50 lines of `.agents/WORKSPACE_STATE.md` during Turn 1.
- **Selective SQLite Query:** When checking past chats, query only `title`, `preview`, and `last_modified_time` for the active workspace URI; never dump raw chat logs.

---

## Reference Sub-Modules

- [references/state-schema.md](./references/state-schema.md) — Standard markdown schema for `WORKSPACE_STATE.md`.
- [references/query-conversations.md](./references/query-conversations.md) — Fast SQLite query script for past workspace conversations.
- [references/handoff-protocol.md](./references/handoff-protocol.md) — Step-by-step protocol for cleanly switching conversations.

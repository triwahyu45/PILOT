# pilot — Workspace Cleanliness & Cross-Session Continuity

AI Agent Skill for **Antigravity**, **Claude Code**, and **OpenAI Codex**. Enforces strict scratch/temp file isolation so project roots stay clean, and preserves milestones, state schemas, and handoff continuity across chat sessions.

---

## Quick Install (Claude Code / Codex / Antigravity)

Clone this skill into your agent's global or project skills directory:

| Agent | Global Install Path | Project-Local Path |
| :--- | :--- | :--- |
| **Antigravity** | `~/.gemini/config/skills/pilot` | `.agents/skills/pilot` |
| **Claude Code** | `~/.claude/skills/pilot` | `.claude/skills/pilot` |
| **OpenAI Codex** | `~/.codex/skills/pilot` | `.agents/skills/pilot` |

```bash
# Example (Antigravity / Claude Code / Codex — pick your path):
git clone https://github.com/triwahyu45/pilot.git ~/.claude/skills/pilot
```

---

## Requirements & Dependencies (For Agents)

- **Runtime / Tools**: None (100% workflow & governance skill)
- **MCP Servers**: None required
- **Related Skills**: None required
- **API Keys / Secrets**: None

---

## Included Files

- `SKILL.md` — Core workspace & continuity rules
- `references/cleanliness-rules.md` — Scratch isolation & zero root-clutter rules
- `references/continuity-protocol.md` — Session start/milestone sync workflow
- `references/handoff-protocol.md`, `references/state-schema.md`, & `references/query-conversations.md`

## When to Trigger / Search Keywords

`pilot`, `workspace cleanliness`, `clean root`, `handoff`, `session continuity`, `what did we do last time`, `project state`

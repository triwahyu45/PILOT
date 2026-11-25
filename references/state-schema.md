# Workspace State Schema (`.agents/WORKSPACE_STATE.md`)

Use this exact structure when creating or updating `<workspace>/.agents/WORKSPACE_STATE.md`. Keep it concise (~20-40 lines total) to minimize token consumption while maximizing information density.

---

## Schema Template

```markdown
# Workspace Project State

- **Project Name / Scope**: <brief 1-line description of the workspace project>
- **Primary Tech Stack**: <frameworks, languages, MCP tools, e.g. Next.js 15, Tailwind, Supabase>
- **Last Updated**: <YYYY-MM-DD HH:MM>

---

## 1. Architectural Decisions & Key Constraints
- Decision 1: <e.g., Using App Router with Server Actions instead of API routes>
- Decision 2: <e.g., Authentication handled via Supabase SSR helpers>

---

## 2. Completed Milestones (What is already working)
- [x] <Milestone 1, e.g., Setup database schema and initial migrations>
- [x] <Milestone 2, e.g., Implemented Google OAuth authentication flow>
- [x] <Milestone 3, e.g., Fixed mobile layout overflow on hero section>

---

## 3. Current In-Progress / Handoff State (Where we left off)
- **Active Task**: <e.g., Refactoring payment checkout webhook handler>
- **Reason for New Chat**: <e.g., Context window compaction; starting fresh chat for clean token budget>
- **Current Blockers / Observations**: <e.g., Stripe signature verification was failing with raw body format>

---

## 4. Next Immediate Actions
1. <Step 1: e.g., Inspect `api/webhooks/stripe/route.ts` raw buffer handling>
2. <Step 2: e.g., Run test suite `npm run test:webhooks`>
3. <Step 3: e.g., Verify webhook payload with Stripe CLI>
```

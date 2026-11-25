# Cross-Conversation Handoff Protocol

Follow this protocol whenever a conversation reaches its token limit, when the user requests a new chat, or when switching focus between major features within the same workspace.

---

## The 4-Step Handoff Sequence

### Step 1: Capture the In-Flight State
Before closing the current conversation, answer these 3 questions:
1. **What was successfully verified in this turn?** (Code edited, tests passing, builds completed).
2. **What remains unfinished or unverified?** (Pending bugs, half-implemented functions, open decisions).
3. **Why is a new conversation being opened?** (e.g., token limit reached, clean slate for testing, new milestone).

### Step 2: Update `<workspace>/.agents/WORKSPACE_STATE.md`
Overwrite or update Section 3 ("Current In-Progress / Handoff State") and Section 4 ("Next Immediate Actions") in `.agents/WORKSPACE_STATE.md`.
- Keep the bullets sharp and actionable.
- Link relevant file paths using relative links (e.g. `[src/auth.ts](file:///path/to/src/auth.ts)`).

### Step 3: Provide the Handoff Brief to the User
Output a crisp 3-sentence message to the user:
> *"State workspace telah diperbarui di `.agents/WORKSPACE_STATE.md`. Ketika Anda membuka conversation baru di workspace ini, saya akan langsung membaca state tersebut dan melanjutkan pekerjaan dari [Task Berikutnya] tanpa harus mengulang penjelasan dari awal."*

### Step 4: First-Turn Resume in the New Conversation
When the user sends their first message in the new chat:
1. Read `.agents/WORKSPACE_STATE.md`.
2. Acknowledge the handoff in one sentence:
   > *"Menyambung dari sesi sebelumnya: kita terakhir sedang mengerjakan [Task]. Berikutnya adalah [Langkah 1]. Apakah ingin langsung saya jalankan?"*

# Querying Past Conversations in Antigravity

Antigravity stores all conversation summaries, titles, and workspace associations inside an internal SQLite database at:
`C:\Users\hando\.gemini\antigravity\conversation_summaries.db`

When entering a workspace where `.agents/WORKSPACE_STATE.md` has not been initialized yet, run this lightweight query to find recent conversation history for the current workspace.

---

## Fast Python One-Liner (Token-Safe)

Run from PowerShell:

```powershell
python -c "
import sqlite3, sys, os

workspace_path = os.getcwd().replace('\\', '/').lower()
db_path = r'C:\Users\hando\.gemini\antigravity\conversation_summaries.db'

con = sqlite3.connect(db_path)
cur = con.cursor()

# Query matching conversations
query = '''
SELECT conversation_id, title, preview, datetime(last_modified_time/1000, 'unixepoch', 'localtime') as last_time
FROM conversation_summaries
WHERE lower(workspace_uris) LIKE '%' || ? || '%'
ORDER BY last_modified_time DESC
LIMIT 3
'''

rows = cur.execute(query, (workspace_path,)).fetchall()
if not rows:
    # Fallback to recent conversations if workspace URI format differs
    rows = cur.execute('''
        SELECT conversation_id, title, preview, datetime(last_modified_time/1000, 'unixepoch', 'localtime')
        FROM conversation_summaries
        ORDER BY last_modified_time DESC
        LIMIT 3
    ''').fetchall()

for cid, title, preview, last_time in rows:
    print(f'[{last_time}] ID: {cid}')
    print(f'Title: {title}')
    print(f'Preview: {preview[:150]}...')
    print('-'*50)
"
```

---

## How to Use the Output

1. Read the `title` and `preview` of the most recent conversation.
2. If the user asks *"terakhir kita ngapain?"*, synthesize the answer directly from the latest entry.
3. Automatically offer to write the initial `.agents/WORKSPACE_STATE.md` so future chats load instantly.

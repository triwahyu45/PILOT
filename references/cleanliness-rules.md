---
name: agent-workspace-cleanliness
description: Enforces strict directory isolation for agent scratch files, test scripts (.ps1, .py, .bat, .sh), experimental programs, and installers. Ensures the workspace root and user directories are never cluttered with loose temporary files.
---

# Agent Workspace Cleanliness & Experiment Isolation

This skill defines mandatory hygiene standards for creating and managing files during agent tasks, experiments, automation runs, and testing.

## Core Rules

### 1. Root Directory Protection
- **Never write loose scripts or artifacts to the workspace root directory.**
- Extensions that must NEVER be dumped loose into root:
  - Scripts: `.ps1`, `.bat`, `.cmd`, `.py`, `.sh`, `.js`
  - Binaries / Packages: `.exe`, `.msi`, `.apk`, `.deb`, `.dex`
  - Temporary test logs & dumps: `*.log`, `*_dump.txt`, `TEST_*.md`, `scratch.*`

### 2. Isolation of Experiments & Automation
- When writing automation scripts, proofs of concept, or exploratory tests, always create a dedicated subfolder:
  ```
  _Agent_Experiments/
    ├── <Topic_Name>/
    │     ├── scripts/
    │     ├── tests/
    │     └── README.md
  ```
- If the work belongs to an existing subproject (e.g. `Detronics`, `AbhinayaUNY_Web`), keep all scripts within that project's existing folder structure (e.g., `Detronics/scripts/`).

### 3. Installer Management
- All downloaded or utility installers must be stored in `_Master_Installer/`:
  - `_Master_Installer/*.exe`
  - `_Master_Installer/*.msi`
- Do not let installers linger loose in the root folder alongside documents or projects.

### 4. Cleanup After Completion
- Before concluding a task, review files created during execution.
- Delete one-off throwaway test scripts with user consent, or move persistent tools into the appropriate project/experiments subfolder.

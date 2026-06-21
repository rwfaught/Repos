# PHASE_01.md

## Phase 01: Foundation

---

## Goal

Create the minimal project skeleton and establish the base directory structure.

This phase defines the physical layout of the system and ensures the project can run basic CLI commands without crashing.

---

## Files to Create

- main.py
- orchestrator/__init__.py
- orchestrator/state.py
- docs/ACTION_LOG.md

---

## Directories to Create (if missing)

- orchestrator/
- providers/
- verifiers/
- agents/
- docs/
- data/
- data/state/
- data/tasks/
- data/artifacts/
- data/logs/

---

## main.py (pseudocode)

- parse command-line arguments

if command == "init":
    call initialize_workspace()

if command == "status":
    call print_status()

---

### initialize_workspace()

- create required directories if they do not exist
- create initial state file if needed
- print a clear success message

---

### print_status()

- print a simple message indicating the system is operational
- no deep logic required

---

## orchestrator/state.py (pseudocode)

function load_state():
    if state file exists:
        read JSON and return data
    else:
        return default state object

function save_state(state):
    write JSON to disk in data/state/

---

## ACTION_LOG.md

If the file does not exist:
- create it in docs/

This file will store phase summaries.

---

## Constraints

- Must not crash when executed
- Must create directories correctly
- Must use root-level structure (NO src/ directory)
- Must keep implementation minimal
- Do NOT implement orchestrator logic yet
- Do NOT implement task system yet
- Do NOT implement providers or verifiers yet

---

## Expected Runtime Behavior

After completion, the following commands should work:

python main.py init  
→ creates all required directories  
→ prints success message

python main.py status  
→ prints a simple system-ready message

---

## Success Criteria

- All required directories exist
- All listed files exist
- No runtime errors occur
- CLI commands execute successfully
- State load/save functions exist (even if minimal)

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was created
   - which files were modified

2. Append a concise entry to:
   docs/ACTION_LOG.md

3. Do NOT proceed to the next phase
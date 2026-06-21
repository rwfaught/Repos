# PHASE_02.md

## Phase 02: State + Task System

---

## Goal

Implement the first real persistent state layer for runs and tasks.

This phase should add:
- a task schema
- run creation and storage
- task persistence
- task loading
- next-task selection

This phase gives the system a durable work model.

---

## Files to Create

- orchestrator/task_schema.py
- orchestrator/run_manager.py

---

## Files to Modify (if needed)

- main.py
- orchestrator/state.py
- docs/ACTION_LOG.md

---

## Data Files Created at Runtime

- data/state/workspace_state.json
- data/runs/<run_id>.json
- data/tasks/<task_id>.json

---

## Task Schema Requirements

Implement a minimal Task structure.

It should include at least:

- id
- run_id
- title
- role
- status
- dependencies
- success_criteria
- files_in_scope
- retry_count

You may also include simple optional fields if helpful, but do NOT over-expand the schema.

---

## orchestrator/task_schema.py (pseudocode)

Define a Task representation.

Possible approach:
- dataclass
- plain class
- simple structured dict helpers

Required functions:

function create_task(data):
    return Task instance

function serialize_task(task):
    return JSON-serializable dict

function deserialize_task(data):
    return Task instance

Keep the schema explicit and minimal.

---

## orchestrator/run_manager.py (pseudocode)

Implement run and task persistence helpers.

Required functions:

function create_run(request_text):
    generate run_id
    build run metadata
    save run JSON to data/runs/<run_id>.json
    update workspace state so active_run_id = run_id
    return run metadata

function save_task(task):
    write JSON to data/tasks/<task_id>.json

function load_task(task_id):
    read JSON and return Task

function load_tasks_for_run(run_id):
    return all tasks belonging to the run

function get_next_task(run_id):
    return the first task where:
        status == "queued"
        and all dependencies are satisfied

Keep logic simple and deterministic.

---

## main.py changes (pseudocode)

Add a minimal command:

if command == "new-run":
    read request text from argument or use a simple stub string
    call create_run(...)
    print run created

Do NOT implement planning yet.
This command only needs to create a run record.

Optional:
- allow a simple manual test task to be created for debugging
- only if this helps validate task persistence cleanly

---

## orchestrator/state.py changes (pseudocode)

Ensure workspace state supports at least:

- workspace_initialized
- active_run_id

If needed, expand the default state object minimally to support Phase 02.

Do NOT overbuild config/state here.

---

## Constraints

- Use JSON for persistence
- Keep schema simple
- Keep logic explicit and readable
- Do NOT implement full orchestrator loop yet
- Do NOT implement providers
- Do NOT implement verifiers
- Do NOT implement planning logic yet
- Do NOT add complex config systems

---

## Expected Runtime Behavior

After this phase, the following should work:

python main.py init  
→ initializes workspace

python main.py new-run  
→ creates a run record
→ sets active_run_id in workspace state

Internal behavior should support:
- saving tasks
- loading tasks
- selecting the next queued task whose dependencies are satisfied

---

## Success Criteria

- Task schema exists and is coherent
- Runs can be created and saved
- Tasks can be created and saved
- Tasks can be loaded from disk
- Next task can be selected deterministically
- No runtime crashes occur
- No future-phase systems are implemented prematurely

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was implemented
   - which files were created or modified

2. Append a concise entry to:
   docs/ACTION_LOG.md

3. Do NOT proceed to the next phase
# PHASE_03.md

## Phase 03: Orchestrator Loop

---

## Goal

Implement the minimal orchestrator execution loop.

This phase connects:
- workspace state
- run system
- task system

It introduces:
- task execution flow
- task state transitions
- artifact creation

This is the first end-to-end system behavior.

---

## Files to Create

- orchestrator/engine.py
- orchestrator/dispatcher.py
- orchestrator/artifact_store.py

---

## Files to Modify (if needed)

- main.py
- orchestrator/run_manager.py
- docs/ACTION_LOG.md

---

## Core Behavior

The system must:

1. Load workspace state
2. Identify active run
3. Select next runnable task
4. Mark task as in_progress
5. Execute task via dispatcher (stub)
6. Create artifact record
7. Mark task as completed
8. Persist all changes
9. Print clear summary

---

## orchestrator/engine.py (pseudocode)

function process_next_task():

    load workspace state

    if no active_run_id:
        print "No active run"
        STOP

    run_id = active_run_id

    task = get_next_task(run_id)

    if no task:
        print "No runnable tasks"
        STOP

    set task.status = "in_progress"
    save task

    result = dispatch_task(task)

    artifact = create_artifact(task, result)
    save artifact

    set task.status = "completed"
    save task

    print summary:
        task id
        task title
        artifact id
        status completed

---

## orchestrator/dispatcher.py (pseudocode)

function dispatch_task(task):

    return {
        "task_id": task.id,
        "status": "success",
        "output": "Stub execution result (Phase 03)"
    }

This is a placeholder.

Do NOT:
- call providers yet
- call roles yet

---

## orchestrator/artifact_store.py (pseudocode)

function create_artifact(task, result):

    generate artifact_id

    build artifact object:
        artifact_id
        task_id
        run_id
        role
        created_at
        status
        output

    save JSON to:
        data/artifacts/<artifact_id>.json

    return artifact

Keep implementation simple.

---

## main.py changes (pseudocode)

Add:

if command == "next":
    call process_next_task()

Keep existing commands unchanged.

---

## Task State Requirements

Tasks must support:

- "queued"
- "in_progress"
- "completed"

No additional states required yet.

---

## Constraints

- Keep implementation minimal and explicit
- Do NOT implement providers yet
- Do NOT implement verifier logic yet
- Do NOT implement role-based execution yet
- Do NOT add routing complexity
- Do NOT introduce retries or failure handling yet
- Use JSON persistence only

---

## Expected Runtime Behavior

After this phase:

python main.py next

Should:

- load active run
- select a queued task
- mark it in progress
- simulate execution
- create artifact
- mark task completed
- print summary

---

## Success Criteria

- `python main.py next` runs without crashing
- A queued task is processed correctly
- Task state transitions persist to disk
- Artifact metadata is written correctly
- Output is clear and readable
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
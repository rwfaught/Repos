# PHASE_07.md

## Phase 07: Verification-Integrated Execution Loop

---

## Goal

Integrate the verifier framework into the orchestrator execution loop.

This phase upgrades the system from:
- "task executed"

to:
- "task executed AND objectively evaluated"

The system must now distinguish between:
- execution success
- verified success

---

## Files to Create

- data/verifier_results/ (directory, created at runtime)

---

## Files to Modify

- orchestrator/engine.py
- orchestrator/task_schema.py (minimal extension only if needed)
- main.py (only if needed for minor adjustments)
- docs/ACTION_LOG.md

---

## Core Behavior

The execution loop must be extended as follows:

1. Load workspace state
2. Identify active run
3. Select next runnable task
4. Mark task as in_progress
5. Execute task via dispatcher
6. Create artifact
7. Run verifier checks
8. Store verifier result
9. Update task status based on verification outcome
10. Persist all changes
11. Print structured summary

---

## Verifier Execution

After artifact creation:

- Determine which verifier checks to run
- For Phase 07, use a simple rule:

    Default behavior:
    - If task.files_in_scope is not empty:
        run "file_exists" check for each file
    - Otherwise:
        skip verification or run a minimal default check

Do NOT introduce complex configuration yet.

---

## Verifier Result Storage

Verifier results must be:

- stored as JSON in:
  data/verifier_results/<task_id>_<timestamp>.json

Each stored result should include:
- task_id
- run_id
- verification result (from VerificationResult.to_dict())
- timestamp

---

## Task Status Update

Task status must now depend on verification:

- If verification passes:
    status = "completed"

- If verification fails:
    status = "verification_failed"

Do NOT introduce retry logic yet.

Do NOT introduce "under_review" yet.

Keep the state model minimal.

---

## orchestrator/engine.py Changes (pseudocode)

After artifact creation:

- run verifier checks
- collect results into VerificationResult
- persist verifier result
- update task status accordingly
- save task

---

## Constraints

- Keep logic simple and explicit
- Do NOT introduce retry loops
- Do NOT introduce planner logic
- Do NOT introduce reviewer loops
- Do NOT introduce dynamic routing
- Do NOT integrate real providers yet
- Do NOT redesign existing components

This phase is integration, not expansion.

---

## Expected Runtime Behavior

Running:

python main.py next

Should now:

- process task
- create artifact
- run verifier checks
- store verifier results
- update task status based on outcome
- print summary including verification result

---

## Success Criteria

- Verifier checks are executed automatically after task execution
- Verification results are stored to disk
- Task status reflects verification outcome
- System remains stable and readable
- No future-phase behavior is introduced prematurely

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was implemented
   - which files were modified

2. Append a concise entry to:
   docs/ACTION_LOG.md

3. Do NOT proceed to future phases
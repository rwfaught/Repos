# PHASE_53.md

## Phase 53: Declared Deterministic Verification Checks

---

## Goal

Deepen the verification layer by allowing bounded, explicit task-declared deterministic verification checks beyond the current implicit `file_exists` behavior tied to `files_in_scope`.

This phase should let a task declare a small closed set of deterministic checks to run against specific targets, while preserving the current execution flow, outcome precedence, and persisted verifier-result model.

This is a **feature-hardening phase**.

It strengthens product truth without broadening into a verifier framework explosion.

---

## Why This Phase Exists

The current system has:

- a functioning bounded execution core
- persistent artifacts and verifier results
- clear outcome classification
- review and recommendation handling
- validated present-tense success on bounded scenarios

That is good.

But the current verification layer remains thin relative to the rest of the architecture.

In practice, task-level verification still centers too heavily on implicit file-existence checks.

That creates a mismatch:

- the system is strong at storing and surfacing workflow state
- the system is still comparatively weak at expressing what was actually verified

This phase closes that gap in a bounded way.

---

## Problems This Phase Must Solve

### Problem 1: Verification Is Too Implicit and Too Narrow

Current task verification is driven mainly by `files_in_scope`, with `file_exists` checks inferred from that list.

That is useful, but too weak for many bounded coding tasks.

A task may need to verify things like:
- a Python file exists
- a Python file passes syntax validation
- a directory exists

The system already has standalone verifier support for a small closed set of checks.

But tasks cannot yet declare those checks explicitly in a structured way.

This phase should make that possible.

---

### Problem 2: Verification Truth Should Be Task-Declared, Not Reconstructed From Convention Alone

Right now, verification intent is carried mostly by convention:
- files in scope imply file existence checks

That is not enough.

The system needs a bounded way for a task to say, explicitly:

- what check should run
- against what target
- using only the currently supported deterministic check set

This phase should add that explicit declaration surface.

---

## Scope Of This Phase

This phase should add the smallest clear task-level verification declaration mechanism that:

1. supports a small closed set of deterministic checks
2. runs those declared checks during normal post-execution verification
3. preserves the current fallback behavior for tasks that do not declare checks
4. stores truthful verifier results using the existing verifier-result persistence model

Choose the smallest implementation that meaningfully improves verification truth.

---

## This Phase Is NOT About

- semantic correctness verification
- arbitrary custom verifier plugins
- test execution as a universal default
- lint framework integration
- broad build-system orchestration
- verifier graphs or policy engines
- changing execution / verification outcome precedence
- changing recommendation behavior
- changing queue behavior
- changing provider semantics
- redesigning the full task schema broadly
- making verification fully domain-general in one step

This phase is about bounded declared deterministic checks only.

---

## Required Capability

The system should gain a small explicit task-level verification surface.

A task should be able to declare one or more verification checks in a structured way.

A minimal acceptable shape is something like:

- optional task field:
  - `verification_checks`

Each entry should minimally declare:
- `check`
- `target`

Example conceptual forms:

- `{"check": "file_exists", "target": "main.py"}`
- `{"check": "python_syntax", "target": "main.py"}`
- `{"check": "directory_exists", "target": "data/tasks"}`

Keep this schema minimal, explicit, and closed.

Do NOT add generic metadata blobs or open-ended verifier configuration.

---

## Supported Check Set

This phase should support only the deterministic checks that already exist in the verifier layer:

- `file_exists`
- `directory_exists`
- `python_syntax`

Do NOT add new verifier types in this phase unless strictly required for coherence.

The point is to expose existing deterministic capability at the task layer, not to invent a large new verification catalog.

---

## Expected Verification Behavior

### Rule 1: Declared Checks Run When Present

If a task declares `verification_checks`, the engine should run those checks as the task’s verification plan.

### Rule 2: Existing Fallback Behavior Remains For Legacy / Simple Tasks

If a task does **not** declare `verification_checks`, preserve the current bounded behavior:
- if `files_in_scope` is non-empty, run implicit `file_exists` checks
- otherwise preserve current minimal/no-check behavior

This matters for backward compatibility and bounded migration.

### Rule 3: Outcome Precedence Remains Unchanged

Final task outcome must still follow current precedence:

1. execution failure wins
2. verification failure after successful execution
3. adequacy/review logic only after successful execution and successful verification
4. completed only when all earlier gates pass

This phase must not change that order.

---

## Files To Modify

Modify only the minimum files required.

Likely candidates:
- `orchestrator/task_schema.py`
- `orchestrator/engine.py`
- verifier-related helper/module(s) only if needed
- targeted tests under `tests/`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

Modify additional files only if clearly necessary.

Do NOT broaden the change into a verifier-system redesign.

---

## Design Rules

1. Keep the verification declaration schema small and explicit.
2. Reuse the existing verifier registry and result structures where possible.
3. Preserve legacy/fallback task behavior.
4. Prefer a closed check set over extensibility theater.
5. Keep verification intent inspectable from the task record itself.
6. Avoid introducing multiple competing verification planning paths.

This phase should make verification more truthful, not more abstract.

---

## Source Of Truth

Verification truth should come from:

- the task’s declared verification checks when present
- existing fallback behavior when absent
- persisted verifier results after execution

Do NOT infer stronger claims than the checks actually performed.

Do NOT claim semantic correctness when only deterministic surface checks ran.

---

## Validation Requirements

This phase must validate at least these cases:

### Test A: Declared `python_syntax` check passes
Create or use a task with:
- `verification_checks = [{"check": "python_syntax", "target": "<valid_python_file>"}]`

Expected:
- execution succeeds
- declared syntax verification runs
- verifier result persists
- task status reflects successful verification path

### Test B: Declared `python_syntax` check fails
Create or use a task with:
- `verification_checks = [{"check": "python_syntax", "target": "<invalid_python_file>"}]`

Expected:
- execution may succeed
- verification fails truthfully
- verifier result persists
- final task status = `verification_failed`

### Test C: Mixed declared checks
Create or use a task with multiple declared checks, such as:
- file exists
- directory exists
- python syntax

Expected:
- all declared checks run
- overall verifier result reflects the combined truth
- persisted verifier record remains inspectable

### Test D: Legacy fallback behavior preserved
Use a task with no `verification_checks` but with `files_in_scope`.

Expected:
- implicit `file_exists` behavior still runs
- no behavior regression for existing tasks

### Test E: Outcome precedence preserved
Confirm that:
- execution failure still wins over verification outcome
- adequacy/review routing still occurs only after successful verification
- no recommendation behavior changes are introduced

### Test F: Existing verifier CLI behavior remains intact
Confirm that standalone verifier CLI behavior still works unchanged for the currently supported check names.

---

## Success Criteria

- tasks can declare a bounded set of deterministic verification checks explicitly
- the engine runs those checks during normal verification flow
- verifier results persist truthfully using the existing result model
- legacy fallback verification behavior is preserved
- outcome precedence remains unchanged
- targeted regression coverage confirms no hidden behavior drift
- verification claims become more meaningful for bounded coding tasks

---

## End Of Phase

STOP after completion.

Then:

1. Summarize:
   - what verification declaration capability was added
   - which files were created or modified

2. Report:
   - how task-declared checks work
   - how fallback behavior was preserved
   - what validation was performed
   - any assumptions or uncertainties

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further

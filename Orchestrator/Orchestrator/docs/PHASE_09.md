# PHASE_09.md

## Phase 09: Execution Failure Handling + Stable Path Resolution

---

## Goal

Correct two observed operational weaknesses in the system:

1. Distinguish execution failure from verification failure when determining final task status.
2. Make filesystem paths resolve relative to the project root instead of the current working directory.

This phase is a targeted hardening phase.

It must improve correctness without redesigning the architecture.

---

## Problems This Phase Must Solve

### Problem 1: Incorrect Final Task Status

Current behavior allows this outcome:

- provider execution returns `status = "error"`
- verification passes
- task is marked `completed`

This is logically incorrect.

Execution failure must be authoritative.

---

### Problem 2: Current Working Directory Dependency

Current behavior depends on running commands from the project root.

If commands are launched from a subdirectory, relative paths may fail and produce misleading behavior such as:

- missing active run
- missing state file
- missing prompt files
- wrong data paths

The system must use stable project-root-relative paths.

---

## Files to Modify

- orchestrator/engine.py
- orchestrator/state.py
- orchestrator/run_manager.py
- orchestrator/artifact_store.py
- orchestrator/dispatcher.py (only if needed for path-safe imports or provider outcome handling)
- providers/ollama_provider.py (only if needed for path-safe behavior)
- agents/planner.py
- agents/coder.py
- agents/reviewer.py
- main.py
- docs/ACTION_LOG.md

---

## Optional New File (Recommended)

- orchestrator/paths.py

If created, this file should define stable root-relative path helpers for the project.

This is recommended because it centralizes path handling and prevents path logic from being duplicated across modules.

---

## Core Behavior Change 1: Outcome Routing

Final task status must now follow this rule order:

### Rule 1: Execution Failure Wins

If provider result has:

- `status == "error"`

Then:
- task status = `execution_failed`

Do NOT treat the task as completed even if verification passes.

Do NOT run later routing logic that assumes successful execution.

Verification may still be recorded for observability, but it must not override execution failure.

---

### Rule 2: Verification Failure After Successful Execution

If provider result has:

- `status == "success"`

and verification fails, then:
- task status = `verification_failed`

---

### Rule 3: Completed Only When Both Succeed

Only set:

- task status = `completed`

when:
- execution status = `success`
- verification passes

---

## Core Behavior Change 2: Stable Path Resolution

All filesystem paths must resolve relative to the project root, not the current working directory.

This applies to:

- workspace state file
- runs directory
- tasks directory
- artifacts directory
- verifier results directory
- role prompt files
- any other persisted system paths

The system should behave correctly whether launched from:
- project root
- a subdirectory
- an absolute command path

---

## Recommended Path Strategy

Create a shared path utility module if helpful.

Example concept:

- determine project root from the location of source files
- expose constants/helpers for:
  - project root
  - data directory
  - docs directory
  - runs directory
  - tasks directory
  - artifacts directory
  - verifier results directory
  - prompt file paths

Do NOT introduce configuration systems for this.
Keep it static and explicit.

---

## orchestrator/engine.py Changes

Update execution flow so that:

1. task becomes `in_progress`
2. provider executes
3. artifact is created
4. verification runs
5. final status is determined by:
   - execution outcome first
   - verification outcome second

Expected logic:

- if result["status"] == "error":
    task.status = "execution_failed"
- else if verification_result.overall_passed is False:
    task.status = "verification_failed"
- else:
    task.status = "completed"

Print summary should clearly show:
- provider
- execution status
- execution error if any
- verification status
- final task status

---

## state.py Changes

Update state file path resolution to use stable project-root-relative paths.

Do NOT change state structure unless strictly necessary.

---

## run_manager.py Changes

Update all run/task path handling to use stable project-root-relative paths.

Do NOT redesign run/task logic.

---

## artifact_store.py Changes

Update artifact output path handling to use stable project-root-relative paths.

Do NOT redesign artifact structure.

---

## Role Module Changes

Update role prompt file paths to resolve relative to the project root or the module location, not the current working directory.

This applies to:
- planner.py
- coder.py
- reviewer.py

Do NOT change role behavior beyond path stability.

---

## main.py Changes

Keep CLI behavior simple.

No major CLI redesign is needed.

Only update behavior if required for:
- path stability
- clearer reporting

---

## Constraints

- Keep the phase tightly scoped
- Do NOT redesign provider abstraction
- Do NOT redesign verification framework
- Do NOT add retry loops
- Do NOT add reviewer routing
- Do NOT add planner logic
- Do NOT introduce config files
- Do NOT add hidden fallback behavior
- Do NOT over-engineer path handling

This phase is about correctness and stability, not expansion.

---

## Validation Requirements

This phase must be validated with at least these cases:

### Test A: Execution Error + Verification Pass
Use unknown provider or forced provider error with existing file in scope.

Expected:
- execution status = error
- verification may pass
- final task status = execution_failed

### Test B: Execution Success + Verification Fail
Use mock provider and missing file in scope.

Expected:
- execution status = success
- verification fails
- final task status = verification_failed

### Test C: Execution Success + Verification Pass
Use mock provider and existing file in scope.

Expected:
- execution status = success
- verification passes
- final task status = completed

### Test D: Run Command From Subdirectory
Run command from outside the project root working directory.

Expected:
- system still finds state, tasks, prompts, and data paths correctly

---

## Success Criteria

- `execution_failed` status is implemented and used correctly
- execution failure no longer results in `completed`
- path handling no longer depends on current working directory
- role prompts load correctly regardless of launch location
- existing provider/verification behavior remains intact
- no architectural drift is introduced

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was implemented
   - which files were modified

2. Report:
   - how execution-vs-verification status is now resolved
   - how project-root-relative path handling works
   - what validation was performed

3. Append a concise entry to:
   docs/ACTION_LOG.md

4. Do NOT proceed further
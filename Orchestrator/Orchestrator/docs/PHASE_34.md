# PHASE_34.md

## Phase 34: Recommendation-Ladder Identity Coherence When Source Artifacts Are Missing

---

## Goal

Harden the recommendation-to-response ladder so explicitly created follow-up review tasks and repair tasks remain coherent with later ladder predicates even when the originating post-execution result has no persisted execution artifact.

This phase should ensure that the system’s response-task creation rules and its later recommendation-created identity rules do not drift apart in edge cases.

This is a hardening phase.

It is NOT about:
- adding new response commands
- changing queue behavior
- adding automation
- redesigning provenance broadly
- changing ordinary successful-path behavior
- broad CLI refactoring

---

## Problems This Phase Must Solve

### Problem 1: Truthful Response Creation Can Fall Outside Later Ladder Recognition

The current response-creation logic does the truthful local thing when no source execution artifact exists:

- it avoids inventing a misleading artifact pointer

That is good.

But later ladder predicates still rely on `source_artifact_id` as part of recommendation-created task identity.

This creates a structural inconsistency:
- a follow-up or repair task can be explicitly and validly created
- yet fail to qualify as recommendation-created under later ladder logic

This phase should remove that inconsistency.

---

### Problem 2: The Ladder Should Stay Coherent at the Edge, Not Just in the Ordinary Path

The recommendation-to-response ladder is now strong in the ordinary case.

This phase should make sure edge conditions do not quietly create a split between:
- what creation commands allow
- what later task-classification surfaces recognize

---

## Files to Modify

Modify only the minimum files required.

Likely candidates:
- `orchestrator/run_manager.py`
- `orchestrator/task_schema.py` (only if truly necessary)
- `main.py` (only if a user-facing surface must reflect the changed logic)
- tests under `tests/`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

Do NOT broaden changes beyond what is necessary to keep ladder identity coherent when source artifacts are missing.

---

## Required Hardening

The system must preserve coherence between:

- explicit response-task creation
- later recommendation-created task recognition

for response tasks created from valid post-execution sources that lack an execution artifact.

A minimal acceptable correction may involve one of the following:

1. refining recommendation-created task predicates so they no longer require `source_artifact_id` in cases where recommendation provenance and source task linkage are already explicit

2. or introducing a small explicit provenance signal that keeps such tasks inside the ladder without inventing misleading artifact lineage

Choose the smallest clear implementation.

Do NOT introduce a large provenance object.
Do NOT add generic metadata blobs.
Do NOT solve this by writing fake artifact IDs.

---

## Behavior Preservation Requirement

This phase must preserve current ordinary-path behavior.

That includes:
- truthful artifact provenance when artifacts exist
- truthful `None` behavior when artifacts do not exist
- explicit follow-up review creation
- explicit repair-task creation
- no hidden automation
- no queue policy changes

This phase should only remove the structural incoherence between valid task creation and later ladder recognition.

---

## Constraints

- Keep this phase tightly scoped
- Do NOT redesign the provenance model broadly
- Do NOT add automation
- Do NOT change queue or execution policy
- Do NOT create new commands unless strictly necessary
- Do NOT bundle in duplicate-awareness or broader `review_reason` cleanup

This is ladder-identity hardening only.

---

## Validation Requirements

Validate at least these cases:

### Test A: Follow-Up Review Task Created From Source Without Execution Artifact

Expected:
- task is created explicitly and truthfully
- no misleading artifact pointer is written
- task still qualifies correctly under later ladder recognition rules

### Test B: Repair Task Created From Source Without Execution Artifact

Expected:
- task is created explicitly and truthfully
- no misleading artifact pointer is written
- task still qualifies correctly under later ladder recognition rules

### Test C: Ordinary Artifact-Present Cases Remain Unchanged

Expected:
- when source execution artifact exists, provenance remains explicit and artifact-accurate

### Test D: No Hidden Behavior Change

Expected:
- no queue policy changes
- no auto-execution
- no routing drift
- existing lifecycle regressions still pass

---

## Success Criteria

- valid response tasks no longer fall outside later ladder identity recognition solely because source execution artifacts are absent
- truthful artifact behavior is preserved
- no misleading lineage is introduced
- no unrelated architectural drift is introduced

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was hardened
   - which files were created or modified

2. Report:
   - how ladder identity now remains coherent when source artifacts are missing
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further

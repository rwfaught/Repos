# PHASE_38.md

## Phase 38: Structuralize Artifact-Missing Ladder Identity

---

## Goal

Harden recommendation-created task identity so artifact-missing edge cases depend less on `recommendation_reason` and more on a small explicit provenance signal.

This phase should preserve the truthful behavior introduced earlier:
- no fake artifact IDs
- no loss of ladder recognition when source artifacts are absent

But it should make the identity path more structurally explicit and less dependent on prose-bearing provenance.

This is a hardening phase.

It is NOT about:
- changing response commands
- queue policy changes
- automation
- redesigning provenance broadly
- removing compatibility behavior entirely
- broad CLI refactoring

---

## Problems This Phase Must Solve

### Problem 1: Artifact-Missing Identity Is Coherent but Not Yet Maximally Crisp

The current recommendation-created predicate is coherent in ordinary and artifact-missing cases.

That is good.

But in the artifact-missing case, ladder recognition still depends partly on `recommendation_reason` as an explicit provenance signal.

This is no longer a defect.
It is now a precision seam.

This phase should make the artifact-missing path more structurally explicit.

---

### Problem 2: Compatibility Residue Should Not Stay Load-Bearing Forever

Legacy fallback parsing and prose-bearing provenance remain understandable as compatibility support.

But they should not remain the preferred identity path for newly created response tasks.

This phase should reduce that pressure without forcing historical migration or redesigning the broader provenance model.

---

## Files to Modify

Modify only the minimum files required.

Likely candidates:
- `orchestrator/task_schema.py` (only if a minimal explicit field is truly necessary)
- `orchestrator/run_manager.py`
- `main.py` (only if any surface must reflect the tightened provenance and only if strictly necessary)
- targeted tests under `tests/`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

Do NOT broaden changes beyond what is necessary to make artifact-missing ladder identity more structurally explicit.

---

## Required Hardening

The system must preserve recommendation-created recognition for valid response tasks created from post-execution sources with no execution artifact, while reducing dependence on `recommendation_reason` for that recognition.

A minimal acceptable correction may involve:

1. introducing one small explicit provenance signal for artifact-missing response tasks
2. or tightening existing helper logic so newly created tasks use a more structural identity path than prose-bearing recommendation reason
3. while preserving compatibility fallback for historical stored tasks where appropriate

Choose the smallest clear implementation.

Do NOT:
- invent fake artifact IDs
- introduce a large provenance object
- add generic metadata blobs
- redesign task persistence broadly
- rewrite historical task files in bulk

---

## Behavior Preservation Requirement

This phase must preserve current ordinary-path behavior.

That includes:
- truthful artifact provenance when artifacts exist
- truthful `None` behavior when artifacts do not exist
- explicit follow-up review creation
- explicit repair-task creation
- duplicate-awareness behavior
- bounded scope inheritance
- no hidden automation
- no queue policy changes

This phase should only make the artifact-missing identity path more explicit and less prose-dependent.

---

## Constraints

- Keep this phase tightly scoped
- Do NOT redesign the provenance model broadly
- Do NOT add automation
- Do NOT change queue or execution policy
- Do NOT bundle in legacy-fallback removal, terminology cleanup, or other watchlist items
- Preserve compatibility for older stored tasks unless a narrow reason requires otherwise

This is identity-precision hardening only.

---

## Validation Requirements

Validate at least these cases:

### Test A: Artifact-Missing Follow-Up Review Still Recognized

Expected:
- follow-up review task created from valid source without execution artifact is still recognized correctly under later ladder predicates
- recognition depends on explicit structural provenance, not only on prose-bearing `recommendation_reason`

### Test B: Artifact-Missing Repair Task Still Recognized

Expected:
- repair task created from valid source without execution artifact is still recognized correctly under later ladder predicates
- recognition depends on explicit structural provenance, not only on prose-bearing `recommendation_reason`

### Test C: Artifact-Present Cases Remain Unchanged

Expected:
- when source execution artifact exists, provenance remains explicit and artifact-accurate
- existing ladder recognition remains correct

### Test D: Historical Compatibility Remains Safe

Expected:
- existing stored tasks with older provenance still behave safely
- no broad migration is required

### Test E: No Hidden Behavior Change

Expected:
- no queue policy changes
- no auto-execution
- no routing drift
- existing lifecycle regressions still pass

---

## Success Criteria

- valid artifact-missing response tasks remain inside the ladder
- ladder recognition for newly created artifact-missing tasks is more structurally explicit than before
- truthful artifact behavior is preserved
- compatibility remains safe
- no unrelated architectural drift is introduced

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was hardened
   - which files were created or modified

2. Report:
   - how artifact-missing ladder identity is now more structurally explicit
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further

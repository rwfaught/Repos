# PHASE_39.md

## Phase 39: Demote Prose-Bearing Fallback to Compatibility-Only Status

---

## Goal

Harden recommendation-created task identity so the active recognition path for newly created tasks is clearly structural-first, while prose-bearing fallback remains only a compatibility path for historical stored tasks.

This phase should preserve safe historical compatibility without allowing prose-bearing fallback to remain equally authoritative for newly created response tasks.

This is a hardening phase.

It is NOT about:
- changing response commands
- queue policy changes
- automation
- redesigning provenance broadly
- removing compatibility behavior entirely
- rewriting historical task files in bulk
- broad CLI refactoring

---

## Problems This Phase Must Solve

### Problem 1: Structural Identity Exists, But Prose-Bearing Fallback Still Shares the Active Predicate

The system now has a cleaner structural identity path for newly created recommendation-derived tasks.

That is good.

But active recommendation-created recognition still allows prose-bearing fallback in the same predicate path.

This is no longer a defect.
It is now a compatibility/governance seam.

This phase should make structural identity clearly primary for newly created tasks.

---

### Problem 2: Compatibility Support Should Remain Safe Without Becoming the Preferred Architecture

Historical stored tasks may still require fallback handling.

That is acceptable.

But compatibility logic should be:
- safe
- narrow
- clearly secondary

It should not remain indistinguishable from the preferred identity path for newly created tasks.

---

## Files to Modify

Modify only the minimum files required.

Likely candidates:
- `orchestrator/run_manager.py`
- `orchestrator/task_schema.py` (only if strictly necessary; likely not needed)
- targeted tests under `tests/`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

Do NOT broaden changes beyond what is necessary to make structural identity clearly primary and prose-bearing fallback clearly compatibility-only.

---

## Required Hardening

The system must preserve:

- structural recognition for newly created recommendation-derived tasks
- safe compatibility for historical stored tasks

But it should tighten the logic so that:

1. newly created tasks are recognized through explicit structural provenance
2. prose-bearing fallback is used only where explicit structural provenance is absent and compatibility support is required

A minimal acceptable correction may involve:

- splitting helper logic into:
  - preferred structural recognition path
  - compatibility fallback path
- or otherwise making the ordering and intent of the predicate explicit in code

Choose the smallest clear implementation.

Do NOT:
- remove compatibility support entirely
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
- safe historical compatibility

This phase should only make the architectural priority of structural identity clearer.

---

## Constraints

- Keep this phase tightly scoped
- Do NOT redesign the provenance model broadly
- Do NOT add automation
- Do NOT change queue or execution policy
- Do NOT bundle in terminology cleanup, descendant-history surfacing, or other watchlist items
- Preserve safe historical compatibility

This is compatibility-path hardening only.

---

## Validation Requirements

Validate at least these cases:

### Test A: Newly Created Artifact-Missing Follow-Up Task Uses Structural Identity

Expected:
- newly created artifact-missing follow-up review task is recognized correctly through structural identity
- recognition does not require prose-bearing fallback

### Test B: Newly Created Artifact-Missing Repair Task Uses Structural Identity

Expected:
- newly created artifact-missing repair task is recognized correctly through structural identity
- recognition does not require prose-bearing fallback

### Test C: Historical Stored Task Still Recognized Safely

Expected:
- a historical task lacking newer structural identity still behaves safely through compatibility fallback
- no migration is required

### Test D: Artifact-Present Cases Remain Unchanged

Expected:
- ordinary artifact-present cases remain explicit and correct

### Test E: No Hidden Behavior Change

Expected:
- no queue policy changes
- no auto-execution
- no routing drift
- existing lifecycle regressions still pass

---

## Success Criteria

- structural identity is clearly primary for newly created recommendation-derived tasks
- prose-bearing fallback is clearly compatibility-only in role and code path
- historical compatibility remains safe
- no unrelated architectural drift is introduced

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was hardened
   - which files were created or modified

2. Report:
   - how structural identity is now primary
   - how compatibility fallback remains safe
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further

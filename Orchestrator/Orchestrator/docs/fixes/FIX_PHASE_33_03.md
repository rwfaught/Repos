# FIX_PHASE_33_03.md

## Fix: Make Repair-Task Artifact Traceability Explicit

---

## Purpose

Correct provenance ambiguity in repair-task creation for failed post-execution recommendation-derived results.

The current repair-task path preserves source task linkage, but artifact linkage is weaker than it should be. This fix must make the repair path more artifact-accurate without broadening the provenance model unnecessarily.

---

## Problem

When a repair task is created from a failed post-execution recommendation-derived result, the system clearly preserves:

- which failed task caused the repair task to exist

But artifact linkage is not equally clear.

If `source_artifact_id` on the repair task points to upstream inherited artifact lineage rather than the artifact produced by the failed task’s own execution, then the system cannot answer clearly enough:

- which failed artifact is actually being repaired?

That weakens inspectability at the exact layer where response-task provenance should be strongest.

---

## Goal

Ensure that repair tasks created from eligible failed recommendation-derived results preserve artifact traceability in a way that clearly points to the failed result artifact being repaired, not just the upstream lineage carried by the failed task.

After this fix:

- task lineage must remain intact
- artifact lineage for repair tasks must become more explicit and more accurate
- the change must remain small and bounded
- no unrelated provenance redesign should be introduced

---

## Files to Modify

Modify only the minimum files required.

Likely candidates:
- `orchestrator/task_schema.py` (only if a minimal explicit field is truly needed)
- `orchestrator/engine.py` (only if failed result artifact capture must be persisted there)
- `orchestrator/run_manager.py`
- `main.py` (only if any surface should display the improved traceability and only if strictly necessary)
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

Do NOT broaden changes beyond what is necessary to make repair-task artifact traceability explicit.

---

## Required Correction

The repair-task creation path must preserve a clear reference to the artifact produced by the failed result task itself, when such an artifact exists.

A minimal acceptable correction may involve one of the following:

1. persist the failed task’s own execution artifact ID onto the task in an explicit field, then use that when creating the repair task

2. or otherwise preserve a clearly named artifact reference that identifies the failed result artifact being repaired

The exact implementation is up to the worker, but it must satisfy this question clearly:

- if a repair task exists, can the system identify the failed result artifact that caused it to exist?

The existing `source_task_id` linkage should remain intact.

---

## Constraints

- Keep this fix tightly scoped
- Do NOT redesign the whole provenance model
- Do NOT redesign artifact storage broadly
- Do NOT change queue or execution policy
- Do NOT add automation
- Do NOT bundle in response-surface wording or other unrelated fixes
- Prefer the smallest explicit correction that makes artifact lineage inspectable

This is a provenance-accuracy fix only.

---

## Traceability Requirements

After the fix, repair-task provenance should answer both:

1. Which failed task caused this repair task?
2. Which failed artifact is being repaired?

Use existing normalized provenance patterns where possible.

If a new explicit field is necessary, keep it small, singular, and narrowly named.
Do NOT introduce a large nested provenance object or generic metadata blob.

---

## Validation Requirements

Validate at least these cases:

### Test A: Failed Result With Artifact

Expected:
- creating a repair task preserves clear linkage to the failed result task
- creating a repair task preserves clear linkage to the failed result artifact

### Test B: Failed Result Without Artifact

Expected:
- repair-task creation still behaves safely and explicitly
- no misleading artifact linkage is written
- task lineage remains intact

### Test C: No Hidden Behavior Change

Expected:
- repair-task creation remains explicit and operator-triggered
- no auto-execution occurs
- no queue policy changes occur

### Test D: Existing Recommendation Lifecycle Regressions Still Pass

Expected:
- existing regression tests for the recommendation/response ladder still pass

---

## Success Criteria

- repair tasks now preserve artifact traceability more accurately
- task lineage remains intact
- the repair-response layer is more auditable
- no unrelated architectural drift is introduced

---

## End of Fix

STOP after completion.

Then:

1. Summarize:
   - what was corrected
   - which files were modified

2. Report:
   - how failed-result artifact traceability is now preserved
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update fix tracking in:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further

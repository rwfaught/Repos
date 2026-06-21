# FIX_PHASE_33_04.md

## Fix: Make Follow-Up Review Artifact Traceability Explicit

---

## Purpose

Correct provenance ambiguity in follow-up review task creation for eligible `needs_review` post-execution recommendation-derived results.

The current follow-up review path preserves source task linkage, but artifact linkage is weaker than it should be. This fix must make the follow-up review path more artifact-accurate without broadening the provenance model unnecessarily.

---

## Problem

When a follow-up review task is created from an eligible `needs_review` post-execution recommendation-derived result, the system clearly preserves:

- which `needs_review` task caused the follow-up review task to exist

But artifact linkage is not equally clear.

If `source_artifact_id` on the follow-up review task points to upstream inherited artifact lineage rather than the artifact produced by the `needs_review` task’s own execution, then the system cannot answer clearly enough:

- which post-execution artifact is this follow-up review supposed to inspect?

That creates provenance ambiguity at the response layer and leaves the follow-up review branch weaker than the repair branch.

---

## Goal

Ensure that follow-up review tasks created from eligible `needs_review` results preserve artifact traceability in a way that clearly points to the `needs_review` result artifact being reviewed, not just the upstream lineage carried by the source task.

After this fix:

- task lineage must remain intact
- artifact lineage for follow-up review tasks must become more explicit and more accurate
- the change must remain small and bounded
- no unrelated provenance redesign should be introduced

---

## Files to Modify

Modify only the minimum files required.

Likely candidates:
- `orchestrator/task_schema.py` (only if a new field is truly necessary; prefer reuse if already available)
- `orchestrator/run_manager.py`
- `main.py` (only if any surface should display the improved traceability and only if strictly necessary)
- `tests/test_phase_32_create_followup_review.py`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

Do NOT broaden changes beyond what is necessary to make follow-up review artifact traceability explicit.

---

## Required Correction

The follow-up review creation path must preserve a clear reference to the artifact produced by the `needs_review` result task itself, when such an artifact exists.

A minimal acceptable correction may involve:

1. using the task’s existing explicit execution artifact field if already available
2. or otherwise preserving a clearly named artifact reference that identifies the `needs_review` result artifact being inspected

The exact implementation is up to the worker, but it must satisfy this question clearly:

- if a follow-up review task exists, can the system identify the `needs_review` result artifact that caused it to exist?

The existing `source_task_id` linkage should remain intact.

---

## Constraints

- Keep this fix tightly scoped
- Do NOT redesign the whole provenance model
- Do NOT redesign artifact storage broadly
- Do NOT change queue or execution policy
- Do NOT add automation
- Do NOT bundle in repair-path fixes or unrelated wording fixes
- Prefer the smallest explicit correction that makes artifact lineage inspectable

This is a provenance-accuracy fix only.

---

## Traceability Requirements

After the fix, follow-up review provenance should answer both:

1. Which `needs_review` task caused this follow-up review task?
2. Which post-execution artifact is being reviewed?

Use existing normalized provenance patterns where possible.

If no relevant result artifact exists, the system should behave safely and explicitly.
Do NOT write misleading artifact linkage.

Do NOT introduce a large nested provenance object or generic metadata blob.

---

## Validation Requirements

Validate at least these cases:

### Test A: `needs_review` Result With Artifact

Expected:
- creating a follow-up review task preserves clear linkage to the `needs_review` source task
- creating a follow-up review task preserves clear linkage to the `needs_review` result artifact

### Test B: `needs_review` Result Without Artifact

Expected:
- follow-up review creation still behaves safely and explicitly
- no misleading artifact linkage is written
- task lineage remains intact

### Test C: No Hidden Behavior Change

Expected:
- follow-up review creation remains explicit and operator-triggered
- no auto-execution occurs
- no queue policy changes occur

### Test D: Existing Recommendation Lifecycle Regressions Still Pass

Expected:
- existing regression tests for the recommendation/response ladder still pass

---

## Success Criteria

- follow-up review tasks now preserve artifact traceability more accurately
- task lineage remains intact
- the follow-up review response layer becomes more auditable
- no unrelated architectural drift is introduced

---

## End of Fix

STOP after completion.

Then:

1. Summarize:
   - what was corrected
   - which files were modified

2. Report:
   - how `needs_review` result artifact traceability is now preserved
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update fix tracking in:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further

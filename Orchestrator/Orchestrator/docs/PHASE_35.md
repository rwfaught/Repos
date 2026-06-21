# PHASE_35.md

## Phase 35: Reduce Semi-Structural Payload in `review_reason`

---

## Goal

Reduce the amount of lineage and recommendation identity meaning carried in `review_reason` so that the field remains primarily explanatory rather than semi-structural.

This phase should preserve current behavior while tightening the boundary between:

- explicit structured provenance
- human-readable explanatory prose

This is a hardening phase.

It is NOT about:
- changing response commands
- changing queue behavior
- adding automation
- redesigning provenance broadly
- rewriting historical task files
- broad CLI refactoring

---

## Problems This Phase Must Solve

### Problem 1: `review_reason` Still Carries Partial Shadow-Schema Meaning

The system is much healthier than it was earlier in the build arc because explicit fields now carry major identity/provenance semantics such as:

- `recommendation_type`
- `recommendation_reason`
- `execution_artifact_id`
- `source_task_id`
- `source_artifact_id`

But `review_reason` still carries fragments that are partly explanatory and partly structural, such as:

- origin recommendation type/reason notes
- source lineage fragments
- result-artifact notes

This is not a current break, but it is schema-drift pressure.

---

### Problem 2: Explanatory Prose Should Not Quietly Re-Becoming a Control Surface

If prose fields keep carrying structural payload at the margins, later code and audits may begin depending on them again.

This phase should reduce that pressure without redesigning the full provenance model.

---

## Files to Modify

Modify only the minimum files required.

Likely candidates:
- `orchestrator/run_manager.py`
- `orchestrator/task_schema.py` (only if a truly minimal explicit field is necessary)
- `main.py` (only if any read surface must reflect the tightened provenance)
- targeted tests under `tests/`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

Do NOT broaden changes beyond what is necessary to reduce semi-structural meaning in `review_reason`.

---

## Required Hardening

Tighten the system so that `review_reason` is no longer carrying load-bearing lineage semantics where explicit fields or narrow helper logic can carry them instead.

A minimal acceptable correction may involve one or more of:

1. reducing or simplifying structured fragments currently embedded into `review_reason`
2. moving any still-load-bearing semantics into existing explicit fields where possible
3. adding the smallest possible new explicit field only if existing fields are truly insufficient
4. updating helper logic so it relies on explicit fields and not prose parsing or prose-like conventions

Choose the smallest clear implementation.

Do NOT:
- introduce a large provenance object
- add generic metadata blobs
- rewrite historical stored data in bulk
- redesign task persistence broadly

---

## Behavior Preservation Requirement

This phase must preserve current ordinary-path behavior.

That includes:
- recommendation-created recognition
- follow-up review creation
- repair-task creation
- truthful artifact provenance
- no hidden automation
- no queue policy changes
- no loss of human-readable trace context

This phase should reduce structural dependence on `review_reason`, not remove useful explanation.

---

## Constraints

- Keep this phase tightly scoped
- Do NOT redesign the provenance model broadly
- Do NOT add automation
- Do NOT change queue or execution policy
- Do NOT bundle in duplicate-awareness or scope-inheritance work
- Preserve readability of persisted task records

This is prose-schema hardening only.

---

## Validation Requirements

Validate at least these cases:

### Test A: Recommendation-Created Identity Still Works

Expected:
- tasks that should qualify as recommendation-created still qualify correctly
- no required recognition path depends on parsing structured fragments out of `review_reason`

### Test B: Follow-Up / Repair Traceability Still Works

Expected:
- follow-up review and repair creation still preserve understandable human-readable context
- explicit provenance remains sufficient for structural identity

### Test C: Historical Compatibility Is Preserved

Expected:
- existing stored tasks continue to behave safely
- no broad migration is required

### Test D: No Hidden Behavior Change

Expected:
- no queue policy changes
- no auto-execution
- no routing drift
- existing lifecycle regressions still pass

---

## Success Criteria

- `review_reason` carries less semi-structural payload than before
- explicit fields remain the main identity/provenance path
- human-readable explanation remains intact
- no unrelated architectural drift is introduced

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was hardened
   - which files were created or modified

2. Report:
   - how `review_reason` is now less semi-structural
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further

# FIX_PHASE_25_01.md

## Fix: Explicit Provider Semantics for `execute-ready-candidate`

---

## Purpose

Correct an architectural inconsistency in the explicit ready-candidate execution path.

The `execute-ready-candidate` command currently allows explicit task selection but does not preserve equally explicit provider behavior if it hardcodes a provider internally.

This fix must align provider handling for explicit ready-candidate execution with the project’s existing execution-surface rules.

---

## Problem

The system already has explicit provider-selection semantics for task execution.

If `execute-ready-candidate` internally hardcodes `provider_name="mock"`, then the command creates a narrower parallel execution path with hidden provider behavior.

That is inconsistent with the project’s existing control model.

The operator should not have explicit control over *which task* is executed while losing explicitness over *how* it is executed.

---

## Goal

Make provider behavior for `execute-ready-candidate` explicit and consistent with the established execution surface.

After this fix:

- provider choice for explicit ready-candidate execution must no longer be hidden
- the command must behave consistently with the project’s existing provider-selection model
- no hidden provider fallback should be introduced beyond already-established command behavior

---

## Files to Modify

Modify only the minimum files required.

Likely candidates:
- `main.py`
- `orchestrator/engine.py` (only if needed for argument plumbing)
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

Do NOT broaden changes beyond what is necessary to restore provider explicitness.

---

## Required Correction

The command:

`python main.py execute-ready-candidate --task <task_id>`

must no longer hardcode the provider internally if that is the current behavior.

A minimal acceptable correction may be one of:

1. support:
   - `python main.py execute-ready-candidate --task <task_id> --provider <name>`
   with the same default provider behavior already used elsewhere

2. or otherwise make provider handling explicitly consistent with the existing command model

Choose the smallest clear implementation.

Do NOT redesign the provider system.

---

## Constraints

- Keep this fix tightly scoped
- Do NOT redesign execution flow broadly
- Do NOT change ordinary `next` behavior
- Do NOT introduce queue reordering
- Do NOT add routing behavior
- Do NOT broaden this into a larger CLI redesign

This is a provider-explicitness fix, not a new phase.

---

## Validation Requirements

Validate at least these cases:

### Test A: Explicit Ready-Candidate Execution With Default Provider Behavior

Expected:
- command uses the same default provider semantics already established elsewhere
- no hidden hardcoded provider remains

### Test B: Explicit Ready-Candidate Execution With Explicit Provider

If `--provider` is implemented:

Expected:
- specified provider is used
- behavior is consistent with existing provider selection rules

### Test C: Ordinary `next` Behavior Unchanged

Expected:
- `next` still behaves as before
- no queue or provider policy regression is introduced

### Test D: Invalid Ready Candidate Still Rejected

Expected:
- provider plumbing does not weaken existing candidate validation behavior

---

## Success Criteria

- `execute-ready-candidate` no longer hides provider choice
- provider handling is consistent with the project’s existing execution model
- no unrelated workflow behavior is changed
- no architectural drift is introduced

---

## End of Fix

STOP after completion.

Then:

1. Summarize:
   - what was corrected
   - which files were modified

2. Append a concise entry to:
   `docs/ACTION_LOG.md`

3. Update fix tracking in:
   `docs/PHASE_INDEX.md`

4. Do NOT proceed further

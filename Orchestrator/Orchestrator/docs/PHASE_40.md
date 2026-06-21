# PHASE_40.md

## Phase 40: Reviewer Recommendation Landing

---

## Goal

Add a disciplined system-readable landing point for reviewer-task output by requiring reviewer-role tasks to produce a small persisted recommendation record in a strict JSON shape.

This phase should convert reviewer output from merely readable text into a bounded recommendation artifact the system can inspect and surface later.

This is a forward feature phase.

It is NOT about:
- automatic repair
- retries
- writeback
- recursive review
- broad routing
- planner-generated decomposition
- free-form interpretation of reviewer prose
- broad schema redesign

---

## Problems This Phase Must Solve

### Problem 1: Reviewer Tasks Can Run, But Their Output Has No Disciplined System Landing Point

The system can already create and execute reviewer tasks.

That is good.

But reviewer output is still not required to land in a strict, inspectable, machine-readable form that the system can persist as recommendation state.

This phase should create that landing point.

---

### Problem 2: Reviewer Output Must Become Structured Without Reopening Fuzzy Parsing

If reviewer output is only loosely interpretable, the system will drift back toward prose parsing and semantic ambiguity.

This phase should avoid that by requiring one strict output shape.

---

## Files to Modify

Modify only the minimum files required.

Likely candidates:
- `orchestrator/engine.py`
- `orchestrator/run_manager.py` (only if a minimal persistence helper is truly needed)
- `orchestrator/reviewer_output.py` (new, recommended)
- `tests/` targeted regression or phase tests
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

Avoid touching `task_schema.py` unless implementation truly requires it.

---

## Required Feature

Reviewer-role tasks must produce recommendation output in a strict JSON-only shape.

A minimal required recommendation record should include:

- `recommendation_type`
- `reason`

Recommendation type must be tightly closed to a bounded allowed set.

Recommended allowed values:
- `accept_result`
- `manual_followup`
- `repair_candidate`

You may refine the exact labels only if strongly justified, but keep the set small and closed.

The output must be valid JSON only.
Do NOT support “interpretable text.”
Do NOT support mixed prose + JSON.
Do NOT support multiple fallback formats.

---

## Recommendation Persistence

When a reviewer-role task completes successfully and its output passes validation:

- persist a recommendation record to disk
- keep persistence inspectable and minimal
- ensure recommendation data is associated with:
  - task ID
  - run ID
  - timestamp
  - validated recommendation payload

Use JSON persistence only.

If a small dedicated recommendation storage path is needed, keep it narrow and explicit.

---

## Validation Rules

Recommendation parsing/validation must apply only to reviewer-role tasks.

Do NOT apply reviewer recommendation validation to:
- coder tasks
- planner tasks
- ordinary execution results
- any task merely because it is in a review-related state

This phase is about reviewer-role output landing, not general semantic interpretation.

---

## Outcome Handling

Recommendation validation should only run after ordinary execution/verification precedence is resolved.

Order must remain:

1. execution failure first
2. verification failure second
3. recommendation validation only after both pass for reviewer-role tasks

If reviewer output is invalid JSON or fails schema validation:
- do not persist a recommendation record
- classify the reviewer task outcome in the smallest bounded way necessary
- do not introduce broad new routing behavior

Choose the smallest explicit handling that preserves inspectability.

---

## Constraints

- Keep this phase tightly scoped
- Do NOT add automatic repair
- Do NOT add retries
- Do NOT add writeback
- Do NOT add recursive reviewer loops
- Do NOT add broad routing
- Do NOT add fuzzy prose parsing
- Do NOT broaden recommendation taxonomy casually
- Prefer a new narrow helper module over spreading parsing logic widely

This is recommendation landing only.

---

## Validation Requirements

Validate at least these cases:

### Test A: Valid Reviewer Recommendation JSON

Expected:
- reviewer-role task output in valid JSON is accepted
- recommendation record is persisted
- stored record is inspectable and minimal

### Test B: Invalid Reviewer Output

Expected:
- invalid JSON or invalid schema is rejected
- no recommendation record is persisted
- no hidden routing occurs

### Test C: Non-Reviewer Task Unchanged

Expected:
- recommendation parsing/validation does not apply to non-reviewer tasks

### Test D: Ordinary Outcome Precedence Preserved

Expected:
- execution failure still wins
- verification failure still wins
- recommendation handling occurs only after those conditions are satisfied for reviewer-role tasks

### Test E: No Hidden Behavior Change

Expected:
- no auto-repair
- no auto-followup creation
- no queue-policy drift
- existing lifecycle regressions still pass

---

## Success Criteria

- reviewer tasks now have a disciplined machine-readable landing point
- recommendation output is JSON-only
- recommendation persistence is minimal and inspectable
- recommendation parsing applies only to reviewer-role tasks
- no unrelated architectural drift is introduced

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was implemented
   - which files were created or modified

2. Report:
   - how reviewer recommendation output is validated
   - how recommendation persistence works
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further

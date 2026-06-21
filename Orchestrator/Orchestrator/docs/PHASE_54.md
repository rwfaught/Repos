# PHASE_54.md

## Phase 54: Bounded Content-Level Deterministic Verification Checks

---

## Goal

Deepen the deterministic verification layer by adding a very small content-level check expansion that plugs into the existing `verification_checks` task surface.

This phase should add exactly two new deterministic verification checks:

- `file_contains_text`
- `json_parses`

The purpose is to make task-declared verification more meaningful for bounded coding and artifact-generation tasks without broadening into a general lint/test/policy framework.

This is a **feature-hardening phase**.

It strengthens verification truth while preserving the project’s bounded, inspectable architecture.

---

## Why This Phase Exists

Phase 53 added a bounded task-level verification declaration surface.

That was the correct step.

But the currently usable check catalog remains very small:

- `file_exists`
- `directory_exists`
- `python_syntax`

This means the system can now declare verification plans explicitly, but the truth-bearing power of those plans is still narrow.

The next missing capability is not more verifier plumbing.

It is a small increase in what can be checked deterministically.

This phase adds that increase in the smallest useful way.

---

## Problems This Phase Must Solve

### Problem 1: Existence Checks Are Often Too Weak For Bounded Coding Tasks

A file can exist and still fail the actual bounded requirement.

Examples:
- expected function name never appears
- expected configuration key is missing
- expected marker line is absent
- expected generated text section is not present

The system needs one exact-text presence check to close part of that gap.

This phase should add that check.

---

### Problem 2: Structured JSON Outputs Need A Minimal Truth Check

Some bounded outputs are JSON artifacts or configuration files.

Currently the verifier layer cannot truthfully answer the minimal question:
- does this file parse as JSON?

That is a useful deterministic check that fits the system’s current design and should be added now.

---

## Scope Of This Phase

This phase should add exactly two new checks to the deterministic verifier catalog:

1. `file_contains_text`
2. `json_parses`

These checks must be usable through the existing `verification_checks` task field added in Phase 53.

Do NOT redesign the declaration system.

Do NOT broaden the verifier layer beyond what is required for these two checks.

---

## This Phase Is NOT About

- regex-based verification
- forbidden-text checks
- YAML parsing
- Markdown heading policy
- test execution
- linter integration
- semantic correctness claims
- arbitrary plugin verifiers
- content scoring systems
- multi-step verifier graphs
- build pipeline orchestration
- schema redesign for verification checks
- changing verification outcome precedence
- changing adequacy/review logic
- changing recommendation behavior

This phase is about one bounded content check and one bounded structured-data check only.

---

## Required Capability

The verifier layer must support two new named checks.

### 1. `file_contains_text`

Purpose:
- verify that a target file exists
- verify that the file contains a required exact text fragment

Minimal required declaration shape:

```json
{
  "check": "file_contains_text",
  "target": "path/to/file.py",
  "text": "def process_next_task"
}
```

You may use a different exact field name than `text` only if strongly justified, but keep it minimal and explicit.

Behavior:
- fail if target does not exist
- fail if target is not a file
- fail if required text is not present
- pass only if the exact text fragment is present

This should be exact substring matching only.
Do NOT add regex support.

### 2. `json_parses`

Purpose:
- verify that a target file exists
- verify that it is readable as valid JSON

Minimal declaration shape:

```json
{
  "check": "json_parses",
  "target": "data/tasks/example.json"
}
```

Behavior:
- fail if target does not exist
- fail if target is not a file
- fail if JSON parsing raises an error
- pass only if JSON parsing succeeds

Do NOT add schema validation.

---

## Verification Declaration Shape

The existing `verification_checks` task field should remain small and explicit.

This phase may minimally extend check entries so that some check types can carry one additional required parameter.

Expected behavior:
- `file_exists`, `directory_exists`, `python_syntax`, `json_parses`
  use only `check` + `target`
- `file_contains_text`
  uses `check` + `target` + exact text field

Do NOT introduce generic metadata blobs or open-ended options maps unless strictly required.

If you need a small optional payload field, keep it narrow and inspectable.

---

## Files To Modify

Modify only the minimum files required.

Likely candidates:
- `orchestrator/task_schema.py`
- `orchestrator/engine.py`
- `verifiers/file_checks.py`
- `verifiers/registry.py`
- possibly `verifiers/base.py` only if structured evidence/messages need a small extension
- targeted tests under `tests/`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

Modify additional files only if clearly necessary.

Do NOT broaden into a verifier redesign.

---

## Design Rules

1. Keep the new checks deterministic and exact.
2. Keep declaration requirements explicit.
3. Reuse the existing verifier registry path.
4. Preserve the current `verification_checks` execution flow from Phase 53.
5. Preserve legacy fallback behavior for tasks without declared checks.
6. Prefer exact substring matching over any pattern language.
7. Keep verifier result messages readable and truthful.
8. Do not imply stronger guarantees than the checks actually provide.

This phase should deepen truth, not widen ambiguity.

---

## Source Of Truth

Verification truth should continue to come from:

- declared task verification checks when present
- existing fallback behavior when absent
- persisted verifier results

This phase must not overclaim:

- `file_contains_text` does not prove correctness
- `json_parses` does not prove schema validity
- passing content checks does not imply semantic adequacy

The system must remain honest about what was actually checked.

---

## Required CLI Preservation

The standalone verifier CLI must remain intact.

This phase should extend it only as needed so that the two new checks can also be run directly in the existing verifier model.

If a check requires one additional argument, keep CLI handling minimal and explicit.

Do NOT redesign the CLI.

---

## Validation Requirements

This phase must validate at least these cases:

### Test A: `file_contains_text` passes
Use a real file containing a known exact string.

Expected:
- check passes
- verifier result persists truthfully
- message/evidence identifies the target and the matched text condition

### Test B: `file_contains_text` fails when text missing
Use a real file that does not contain the required exact string.

Expected:
- check fails
- final task status becomes `verification_failed` when used in task flow
- verifier evidence remains inspectable

### Test C: `json_parses` passes
Use a valid JSON file.

Expected:
- check passes
- persisted verifier result reflects successful parse

### Test D: `json_parses` fails
Use an invalid JSON file.

Expected:
- check fails
- parse error information is captured in evidence/message
- final task status becomes `verification_failed` when used in task flow

### Test E: Mixed declared checks remain coherent
Use a task with a mix of:
- existing checks
- new checks

Expected:
- all declared checks run
- combined result remains truthful and inspectable
- existing Phase 53 declared-check behavior remains intact

### Test F: Legacy fallback behavior preserved
Use a task with no `verification_checks` and non-empty `files_in_scope`.

Expected:
- implicit `file_exists` fallback still runs
- no regression in older task behavior

### Test G: Existing verifier CLI behavior preserved
Confirm:
- old check names still work
- new check names work through the CLI with minimal explicit argument handling
- no unrelated CLI drift occurs

---

## Success Criteria

- exactly two new deterministic checks are added:
  - `file_contains_text`
  - `json_parses`
- both checks work through the verifier registry
- both checks can be used through existing `verification_checks`
- verifier results remain structured, truthful, and inspectable
- legacy fallback behavior remains unchanged
- verification outcome precedence remains unchanged
- targeted regression coverage confirms no hidden drift
- the verifier layer becomes more useful without becoming broad or abstract

---

## End Of Phase

STOP after completion.

Then:

1. Summarize:
   - what checks were added
   - which files were created or modified

2. Report:
   - how each new check works
   - how task declaration shape was extended, if at all
   - how CLI preservation was handled
   - what validation was performed
   - any assumptions or uncertainties

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further

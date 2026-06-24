# Phase 263 - General Answer Artifact Persistence Policy

Boundary:

`PHASE_263_GENERAL_ANSWER_ARTIFACT_PERSISTENCE_POLICY_SOURCE_TEST_DOCS`

## Purpose

Phase 263 defines and codifies the artifact persistence/default-surfacing
policy for structured local `general_answer` review artifacts.

The policy records the current artifact behavior without adding hidden default
writes, live answer generation, model/provider/runtime execution,
service/API/UI behavior, or production behavior.

## Files Changed

Created source:

- `orchestrator/general_answer_artifact_policy.py`

Updated source:

- `orchestrator/manual_review_cli.py`

Created tests:

- `tests/test_phase_263_general_answer_artifact_persistence_policy_contract.py`

Created docs:

- `docs/PHASE_263.md`

Updated docs:

- `docs/TRACKS_AND_OPEN_THREADS.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`

## Policy

Phase 263 adds a small deterministic helper:

`build_general_answer_artifact_persistence_policy(write_review_json_path)`

The policy says artifact persistence is opt-in only via caller-supplied:

`--write-review-json <artifact_json_path>`

The policy says no default artifact path is currently created:

- `default_artifact_path_enabled=false`
- `default_artifact_path=null`
- `artifact_path_source="caller_supplied"` only when persistence is requested

The successful artifact-write notice appears only after successful
caller-supplied artifact persistence:

`Review JSON Artifact Written: <artifact_json_path>`

The notice does not appear when persistence is omitted, input is rejected,
artifact writing fails, or fixture mode is used.

The policy payload is included in successful structured local `general_answer`
review artifacts under:

`artifact_persistence_policy`

## Preserved Behavior

Phase 263 preserves report-only semantics.

Phase 263 preserves existing behavior for:

- normal UTF-8 input
- UTF-8 BOM input
- malformed JSON
- unreadable paths
- non-object JSON
- wrong `request_type`
- unsafe execution requests
- high or unknown risk
- invalid artifact path
- fixtures

## Non-Execution Guarantees

The policy does not implement semantic answer generation.

The policy does not prove answer correctness.

The policy does not execute providers/models/runtimes.

The policy does not perform RAG/local lookup, web lookup,
scheduler/reminder execution, connector execution, worker/Codex dispatch,
service/API/UI behavior, export/package, or production work.

The policy does not broaden the current success criterion.

## Open Thread Status

Phase 263 codifies artifact persistence/default-surfacing policy for the
structured local `general_answer` review artifact lane.

Broader `general_answer` usability remains open.

`PRODUCT_GENERAL_ANSWER_REAL_INPUT_ADAPTER` remains `DEFERRED_VALID`.

`PRODUCT_GENERAL_ANSWER_REAL_INPUT_ARTIFACT_PERSISTENCE` remains
`DEFERRED_VALID`.

`PRODUCT_AUTONOMY_TIER_POLICY` remains `DEFERRED_VALID`; Phase 263 does not
implement autonomy-tier behavior.

## Validation Commands

- `python -m py_compile orchestrator/manual_review_cli.py`
- `python -m py_compile orchestrator/manual_review_runner.py`
- `python -m py_compile orchestrator/lightweight_answer_report.py`
- `python -m py_compile orchestrator/general_answer_artifact_policy.py`
- `python -m unittest discover -s tests -p "test_phase_256_general_answer_real_input_report_only_cli_adapter_contract.py" -v`
- `python -m unittest discover -s tests -p "test_phase_257_general_answer_real_input_review_artifact_persistence_contract.py" -v`
- `python -m unittest discover -s tests -p "test_phase_258_general_answer_json_bom_tolerance_contract.py" -v`
- `python -m unittest discover -s tests -p "test_phase_260_general_answer_review_artifact_write_notice_contract.py" -v`
- `python -m unittest discover -s tests -p "test_phase_263_general_answer_artifact_persistence_policy_contract.py" -v`
- `git diff --check`
- `git status --short`

## PASS Marker

`PHASE263_GENERAL_ANSWER_ARTIFACT_PERSISTENCE_POLICY_SOURCE_TEST_DOCS_PROVEN=PASS`

# Phase 258 - General Answer JSON BOM Tolerance

Boundary:

`PHASE_258_GENERAL_ANSWER_JSON_BOM_TOLERANCE_SOURCE_TEST_DOCS`

## Purpose

Phase 258 fixes UTF-8 BOM tolerance for structured local `general_answer` JSON
input used by:

`--general-answer-input <json_path> [--write-review-json <artifact_json_path>]`

The operator smoke failure showed a visually valid local JSON file could be
rejected as malformed JSON at line 1 column 1 when Windows/PowerShell file
creation introduced a UTF-8 BOM.

## Files Changed

Updated source:

- `orchestrator/manual_review_cli.py`

Created tests:

- `tests/test_phase_258_general_answer_json_bom_tolerance_contract.py`

Updated docs:

- `docs/PHASE_258.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`

## Behavior

Phase 258 changes the structured local JSON reader for `--general-answer-input`
to read with UTF-8 BOM tolerance. Normal UTF-8 JSON and UTF-8 BOM-prefixed JSON
are accepted through the same conservative `general_answer` structured input
path when all existing safety conditions pass.

Phase 258 preserves report-only semantics.

Phase 258 preserves existing rejection behavior for malformed JSON, unreadable
paths, non-object JSON, unsafe input, wrong `request_type`, high/unknown risk,
mutation, scheduler/reminder, RAG/local lookup, web lookup, connector,
provider/model/runtime execution, production-readiness requests, and invalid
artifact paths.

## Non-Execution Guarantees

Phase 258 does not implement semantic answer generation.

Phase 258 does not prove answer correctness.

Phase 258 does not execute providers/models/runtimes.

Phase 258 does not perform RAG/local lookup, web lookup, scheduler/reminder
execution, connector execution, worker/Codex dispatch, service/API/UI behavior,
export/package, or production work.

Phase 258 does not broaden the current success criterion.

## Validation Commands

- `python -m py_compile orchestrator/manual_review_cli.py`
- `python -m py_compile orchestrator/manual_review_runner.py`
- `python -m py_compile orchestrator/lightweight_answer_report.py`
- `python -m unittest discover -s tests -p "test_phase_256_general_answer_real_input_report_only_cli_adapter_contract.py" -v`
- `python -m unittest discover -s tests -p "test_phase_257_general_answer_real_input_review_artifact_persistence_contract.py" -v`
- `python -m unittest discover -s tests -p "test_phase_258_general_answer_json_bom_tolerance_contract.py" -v`
- `git diff --check`
- `git status --short`

## PASS Marker

`PHASE258_GENERAL_ANSWER_JSON_BOM_TOLERANCE_SOURCE_TEST_DOCS_PROVEN=PASS`

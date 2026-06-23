# Phase 260 - General Answer Review Artifact Write Notice

Boundary:

`PHASE_260_GENERAL_ANSWER_REVIEW_ARTIFACT_WRITE_NOTICE_SOURCE_TEST_DOCS`

## Purpose

Phase 260 improves operator usability for the existing structured local
`general_answer` real-input review artifact path.

Phase 260 adds a deterministic CLI notice when a caller-supplied review JSON
artifact is successfully written:

`Review JSON Artifact Written: <artifact_json_path>`

This is UX/reporting only. It does not change report-only semantics.

## Files Changed

Updated source:

- `orchestrator/manual_review_cli.py`

Created tests:

- `tests/test_phase_260_general_answer_review_artifact_write_notice_contract.py`

Updated docs:

- `docs/PHASE_260.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`

## Behavior

When the CLI is invoked with:

`--general-answer-input <input_json_path> --write-review-json <artifact_json_path>`

and the review JSON artifact write succeeds, stdout/result output includes:

`Review JSON Artifact Written: <artifact_json_path>`

The notice is appended only after successful artifact writing. It does not
appear when `--write-review-json` is omitted, when input is rejected before
artifact writing, when artifact writing fails, or when fixture mode is used.

The artifact path remains caller-supplied only. Phase 260 does not invent
default output locations and does not change the artifact schema.

Phase 260 preserves existing behavior for normal UTF-8 input, UTF-8 BOM input,
malformed JSON, unreadable paths, non-object JSON, wrong `request_type`, unsafe
execution requests, high or unknown risk, invalid artifact paths, and fixtures.

## Non-Execution Guarantees

Phase 260 preserves report-only semantics.

Phase 260 does not implement semantic answer generation.

Phase 260 does not prove answer correctness.

Phase 260 does not execute providers/models/runtimes.

Phase 260 does not perform RAG/local lookup, web lookup, scheduler/reminder
execution, connector execution, worker/Codex dispatch, service/API/UI behavior,
export/package, or production work.

Phase 260 does not broaden the current success criterion.

## Validation Commands

- `python -m py_compile orchestrator/manual_review_cli.py`
- `python -m py_compile orchestrator/manual_review_runner.py`
- `python -m py_compile orchestrator/lightweight_answer_report.py`
- `python -m unittest discover -s tests -p "test_phase_256_general_answer_real_input_report_only_cli_adapter_contract.py" -v`
- `python -m unittest discover -s tests -p "test_phase_257_general_answer_real_input_review_artifact_persistence_contract.py" -v`
- `python -m unittest discover -s tests -p "test_phase_258_general_answer_json_bom_tolerance_contract.py" -v`
- `python -m unittest discover -s tests -p "test_phase_260_general_answer_review_artifact_write_notice_contract.py" -v`
- `git diff --check`
- `git status --short`

## PASS Marker

`PHASE260_GENERAL_ANSWER_REVIEW_ARTIFACT_WRITE_NOTICE_SOURCE_TEST_DOCS_PROVEN=PASS`

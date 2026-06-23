# Phase 256 - General Answer Real Input Report-Only CLI Adapter

Boundary:

`PHASE_256_GENERAL_ANSWER_REAL_INPUT_REPORT_ONLY_CLI_ADAPTER_SOURCE_TEST_DOCS`

## Purpose

Phase 256 moves the existing deterministic lightweight `general_answer`
report-only lane from fixture-only CLI proof to a real operator-provided
structured local JSON input file.

The manual review CLI now accepts:

`--general-answer-input <json_path>`

This is usability plumbing only. It does not implement answer generation,
semantic correctness, provider/model/runtime execution, RAG/local lookup, web
lookup, scheduler/reminder execution, connector behavior, worker dispatch,
Codex dispatch, service/API/UI behavior, export/package, production work, or
production readiness.

## Source And Tests

Changed source:

- `orchestrator/manual_review_cli.py`

Created tests:

- `tests/test_phase_256_general_answer_real_input_report_only_cli_adapter_contract.py`

Updated docs:

- `docs/PHASE_256.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`

## CLI Behavior

The new option loads a local JSON file using only the Python standard library.
It accepts only a structured JSON object for a safe low/routine-risk
`general_answer` request.

Accepted input is converted into the existing non-executing structured intake
path with:

- `request_type="general_answer"`
- `allowed_to_answer_directly=True`
- `allowed_to_mutate_files=False`
- `allowed_to_schedule=False`
- `allowed_to_use_local_documents=False`
- `allowed_to_use_web=False`
- `requires_external_connector=False`
- `requires_operator_confirmation=False`
- `required_capabilities=("direct_answer",)`
- `execution_policy="report_only_manual_review_only_non_executing"`

The output preserves the existing manual review rendering shape, including
Assessment, Accepted Facts, Decision, NBM, RESPONSE_METADATA, and the Phase 235
`Lightweight General Answer Report` section for accepted safe input.

Existing CLI behavior remains unchanged for:

- `--help`
- `--list-fixtures`
- `--fixture <fixture_id>`
- existing provider probe packet drafting options

## Rejection Behavior

The adapter deterministically rejects before runner execution when the input is
not a readable structured JSON object, malformed JSON, missing a required path,
or missing required structured fields.

It also rejects or blocks conservatively for wrong request type, high/critical
or unknown/non-low risk, mutation requirements, scheduling/reminder
requirements, local-document/RAG requirements, web lookup requirements,
external connector requirements, provider/model/runtime execution
requirements, and production-readiness claims.

Rejected or blocked inputs return a nonzero result and do not receive an
accepted lightweight answer report.

## Non-Execution Guarantees

Phase 256 does not perform or introduce:

- runtime/probe execution
- provider/model execution
- WSL/Ollama execution
- Hermes/OpenClaw/Discord behavior
- RAG/local-document lookup
- web lookup
- scheduler/reminder execution
- connector execution
- worker dispatch
- Codex dispatch from product code
- service/API/UI implementation
- project-script execution
- source refresh
- export/package
- cleanup/delete/archive
- commit/push
- production task execution

## Caveats And Non-Proofs

Phase 256 accepts a real operator-provided structured local input file for
`general_answer` and preserves report-only semantics.

It does not prove semantic answer correctness, model-backed generation,
provider/runtime/platform execution, live route execution, RAG/local lookup,
web lookup, scheduler/reminder behavior, connector behavior, worker/Codex
dispatch, service/API/UI productization, export/package behavior, production
work, or production readiness.

It does not broaden the current success criterion. The present-tense success
bar remains coding-task focused unless a later explicit boundary changes it.

## Validation Commands

Run from product repo root:

- `python -m py_compile orchestrator/manual_review_cli.py`
- `python -m py_compile orchestrator/manual_review_runner.py`
- `python -m py_compile orchestrator/lightweight_answer_report.py`
- `python -m unittest discover -s tests -p "test_phase_235_general_answer_lightweight_report_only_contract.py" -v`
- `python -m unittest discover -s tests -p "test_phase_243_general_answer_lightweight_report_manual_review_integration_contract.py" -v`
- `python -m unittest discover -s tests -p "test_phase_119_manual_review_cli_adapter_contract.py" -v`
- `python -m unittest discover -s tests -p "test_phase_256_general_answer_real_input_report_only_cli_adapter_contract.py" -v`
- `git diff --check`

## PASS Marker

`PHASE256_GENERAL_ANSWER_REAL_INPUT_REPORT_ONLY_CLI_ADAPTER_SOURCE_TEST_DOCS_PROVEN=PASS`

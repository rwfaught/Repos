# Phase 257 - General Answer Real Input Review Artifact Persistence

Boundary:

`PHASE_257_GENERAL_ANSWER_REAL_INPUT_REVIEW_ARTIFACT_PERSISTENCE_SOURCE_TEST_DOCS`

## Purpose

Phase 257 adds explicit caller-supplied JSON artifact persistence for the
existing real-input `general_answer` manual review output.

Phase 256 allowed a structured local `general_answer` JSON input file to enter
the existing deterministic manual review/lightweight answer report lane. Phase
257 lets the operator persist that review result to a supplied artifact path:

`--general-answer-input <input_json_path> --write-review-json <artifact_json_path>`

This is persistence plumbing only. It does not implement semantic answer
generation, answer correctness proof, model-backed generation, provider/model/
runtime execution, RAG/local lookup, web lookup, scheduler/reminder execution,
connector behavior, worker/Codex dispatch, service/API/UI behavior,
export/package behavior, production work, or production readiness.

## Source And Tests

Changed source:

- `orchestrator/manual_review_cli.py`

Created tests:

- `tests/test_phase_257_general_answer_real_input_review_artifact_persistence_contract.py`

Updated docs:

- `docs/PHASE_257.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`

## CLI Behavior

The new persistence option is explicit and caller-supplied:

- `--write-review-json <artifact_json_path>`

It is accepted only with the real-input general-answer path:

- `--general-answer-input <input_json_path> --write-review-json <artifact_json_path>`

Default behavior remains unchanged:

- fixture review remains stdout-only unless a future boundary explicitly adds
  fixture persistence
- real-input review remains stdout-only unless `--write-review-json` is
  supplied
- `--help`, `--list-fixtures`, `--fixture <fixture_id>`, and existing provider
  probe packet drafting options remain intact

The artifact path is never invented by the CLI.

## Artifact Shape

Accepted persisted artifacts are JSON and include:

- `phase=PHASE_257`
- `artifact_kind=general_answer_real_input_review_artifact_persistence`
- `request_id`
- `request_type`
- `accepted`
- `blocked`
- `cli_result_status`
- `exit_code_intent`
- `manual_review_text`
- `lightweight_answer_report_present`
- `lightweight_answer_report_payload`
- `non_proofs`
- `caveats`
- `no_activity_flags`
- `production_readiness=false`
- `source_input_kind=structured_local_general_answer_json`
- `report_only=true`
- `runtime_execution=false`
- `provider_execution=false`
- `model_execution=false`
- `rag_lookup=false`
- `web_lookup=false`
- `scheduler_execution=false`
- `connector_execution=false`
- `worker_dispatch=false`
- `codex_dispatch=false`
- `service_api_ui=false`

## Rejection Behavior

Phase 257 preserves Phase 256 rejection behavior. Wrong request type,
high/critical or unknown/non-low risk, mutation, scheduling/reminder,
RAG/local lookup, web lookup, connector, provider/model/runtime execution,
production-readiness claims, malformed JSON, missing input path, missing
required fields, and invalid artifact paths return conservative nonzero
results.

Rejected or blocked cases do not receive accepted lightweight answer reports
and do not produce misleading success artifacts.

## Non-Execution Guarantees

Phase 257 does not perform or introduce:

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

Phase 257 preserves report-only semantics.

It does not prove answer correctness, semantic correctness, model-backed
generation, provider/model/runtime behavior, live route execution, RAG/local
lookup, web lookup, scheduler/reminder behavior, connector behavior,
worker/Codex dispatch, service/API/UI productization, export/package behavior,
production work, or production readiness.

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
- `python -m unittest discover -s tests -p "test_phase_257_general_answer_real_input_review_artifact_persistence_contract.py" -v`
- `git diff --check`

## PASS Marker

`PHASE257_GENERAL_ANSWER_REAL_INPUT_REVIEW_ARTIFACT_PERSISTENCE_SOURCE_TEST_DOCS_PROVEN=PASS`

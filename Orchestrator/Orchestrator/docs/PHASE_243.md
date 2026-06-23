# Phase 243 - General Answer Lightweight Report Manual Review Integration

Boundary:

`PHASE_243_GENERAL_ANSWER_LIGHTWEIGHT_REPORT_MANUAL_REVIEW_INTEGRATION_SOURCE_TEST_DOCS`

## Purpose

Integrate the Phase 235 deterministic lightweight `general_answer` report-only
contract into the manual coordinator review runner surface for accepted
low-risk direct-answer cases.

This phase surfaces the existing lightweight report artifact in manual review
output. It does not call a model, provider, runtime, router execution path,
RAG/local-document lookup, web lookup, scheduler, connector, worker dispatch,
Codex dispatch, Hermes, OpenClaw, Discord, WSL, Ollama, export, package,
cleanup, deletion, archive, production task execution, service, API, or UI.

## Source And Tests

Changed source:

- `orchestrator/manual_review_runner.py`

Created tests:

- `tests/test_phase_243_general_answer_lightweight_report_manual_review_integration_contract.py`

Related existing source:

- `orchestrator/lightweight_answer_report.py`
- `orchestrator/coordinator_review_report.py`
- `orchestrator/request_routing.py`

Related existing tests:

- `tests/test_phase_235_general_answer_lightweight_report_only_contract.py`
- `tests/test_phase_123_model_router_policy_manual_review_integration_contract.py`
- `tests/test_phase_118_manual_review_runner_contract.py`
- `tests/test_phase_119_manual_review_cli_adapter_contract.py`

## Integration Behavior

`run_named_fixture_review("safe_direct_answer")` still produces the existing
manual review and router policy output. The runner now also exposes
`lightweight_answer_report_payload` and appends a rendered
`Lightweight General Answer Report` section for the accepted low-risk
`general_answer` direct-answer fixture.

The integrated payload preserves:

- `phase=PHASE_235`
- `artifact_kind=general_answer_lightweight_report_only_contract`
- `request_type=general_answer`
- `production_readiness=false`

The integration complements router policy posture. It does not replace or
weaken the existing manual review report, router policy section, route
selection readiness section, provider evidence section, provider probe packet
status, NBM text, response metadata, non-proofs, or caveats.

Non-general-answer cases, including
`safe_coding_source_test_mutation`, do not receive an accepted lightweight
answer report payload. Blocked or unsafe direct-answer-like cases do not
smuggle lightweight answer acceptance.

## Non-Execution Guarantees

This phase performs deterministic in-process source/test/docs integration only.

It does not perform:

- provider/model/runtime execution
- WSL/Ollama execution
- Hermes/OpenClaw/Discord execution
- route execution or live router proof
- RAG/local-document lookup
- web lookup
- scheduler/reminder execution
- connector execution
- worker dispatch
- Codex dispatch
- export/package
- cleanup/delete/archive
- production task execution
- service/API/UI implementation

## Activity Flags

The Phase 235 lightweight payload keeps all represented activity flags false,
including:

- `mutation_performed=false`
- `execution_performed=false`
- `provider_executed=false`
- `model_executed=false`
- `runtime_executed=false`
- `wsl_executed=false`
- `ollama_executed=false`
- `hermes_executed=false`
- `openclaw_executed=false`
- `discord_executed=false`
- `rag_lookup_performed=false`
- `web_lookup_performed=false`
- `scheduler_executed=false`
- `connector_executed=false`
- `worker_dispatched=false`
- `codex_dispatched=false`
- `export_performed=false`
- `package_performed=false`
- `cleanup_performed=false`
- `deletion_performed=false`
- `archive_performed=false`
- `production_executed=false`

## Caveats And Non-Proofs

This phase is not semantic answer correctness proof, model-backed generation,
provider/runtime execution proof, live router proof, RAG/local lookup proof,
web lookup proof, scheduler/reminder proof, connector proof, worker/Codex
dispatch proof, production task execution proof, service/API/UI
productization, or production readiness.

The rendered lightweight report is a review artifact for an accepted
structured low-risk direct-answer case. It is not coordinator ratification by
itself and does not authorize downstream execution.

## Validation Commands And Results

Run from product repo root:

- `python -m unittest discover -s tests -p "test_phase_243_general_answer_lightweight_report_manual_review_integration_contract.py" -v`
- `python -m unittest discover -s tests -p "test_phase_235_general_answer_lightweight_report_only_contract.py" -v`
- `python -m unittest discover -s tests -p "test_phase_123_model_router_policy_manual_review_integration_contract.py" -v`
- `python -m unittest discover -s tests -p "test_phase_118_manual_review_runner_contract.py" -v`
- `python -m py_compile orchestrator/lightweight_answer_report.py`
- `python -m py_compile orchestrator/manual_review_runner.py`
- `git diff --check`

Results:

- Phase 243 unittest: `Ran 6 tests ... OK`
- Phase 235 unittest: `Ran 9 tests ... OK`
- Phase 123 unittest: `Ran 9 tests ... OK`
- Phase 118 unittest: `Ran 21 tests ... OK`
- Additional Phase 119 CLI adapter regression: `Ran 18 tests ... OK`
- `py_compile orchestrator/lightweight_answer_report.py`: passed with no output
- `py_compile orchestrator/manual_review_runner.py`: passed with no output
- `git diff --check`: passed with line-ending warnings only for touched files

## PASS Marker

`PHASE243_GENERAL_ANSWER_LIGHTWEIGHT_REPORT_MANUAL_REVIEW_INTEGRATION_SOURCE_TEST_DOCS_PROVEN=PASS`

# Phase 235 - General Answer Lightweight Report-Only Contract

## Purpose

Phase 235 adds the smallest deterministic source/test/docs contract for a
lightweight `general_answer` report-only lane.

The lane accepts only structured low-risk `general_answer` requests where a
direct report-only answer surface is allowed. It produces a reviewable artifact
with clear classification, accepted facts, caveats, non-proofs, no-activity
flags, and an operator-visible next action.

This phase productizes lane shape only. It does not call a model, provider,
runtime, live router, RAG/local-document lookup, web lookup, scheduler,
connector, Hermes, OpenClaw, Discord, WSL/Ollama, worker dispatch, Codex
dispatch, export/package, cleanup/delete/archive, or production task behavior.

## Source And Tests

Created source:

- `orchestrator/lightweight_answer_report.py`

Created tests:

- `tests/test_phase_235_general_answer_lightweight_report_only_contract.py`

## Contract Shape

The source exposes:

- `build_lightweight_general_answer_report(request)`
- `render_lightweight_general_answer_report(report)`
- `lightweight_general_answer_report_to_dict(report)`

The report includes:

- `phase=PHASE_235`
- `artifact_kind=general_answer_lightweight_report_only_contract`
- `request_id`
- `request_type=general_answer`
- `user_intent_summary`
- `accepted`
- `outcome_classification`
- `report_text`
- `accepted_facts`
- `blocked_conditions`
- `missing_requirements`
- `caveats`
- `non_proofs`
- `recommended_next_action`
- `activity_flags`
- `production_readiness=false`

## Acceptance Behavior

A request is accepted only when:

- `request_id` is present.
- `request_type` is exactly `general_answer`.
- `user_intent_summary` is present.
- `risk_level` is low/routine.
- The request does not require mutation, scheduling, local documents/RAG, web,
  external connector, provider/model/runtime execution, or production
  readiness.

Accepted reports classify as:

`general_answer_lightweight_report_only_accepted`

## Blocking Behavior

The lane blocks or rejects:

- missing `request_id`
- missing `user_intent_summary`
- wrong `request_type`
- high or critical risk
- requests requiring file mutation
- requests requiring scheduling or reminders
- requests requiring local documents or RAG
- requests requiring web lookup
- requests requiring an external connector
- requests implying provider/model/runtime execution
- requests claiming production readiness

Blocked reports classify as:

`general_answer_lightweight_report_only_blocked`

## Activity Flags

All execution/activity flags remain false:

- `mutation_performed`
- `execution_performed`
- `provider_executed`
- `model_executed`
- `runtime_executed`
- `wsl_executed`
- `ollama_executed`
- `hermes_executed`
- `openclaw_executed`
- `discord_executed`
- `rag_lookup_performed`
- `web_lookup_performed`
- `scheduler_executed`
- `connector_executed`
- `worker_dispatched`
- `codex_dispatched`
- `export_performed`
- `package_performed`
- `cleanup_performed`
- `deletion_performed`
- `archive_performed`
- `production_executed`

## Caveats And Non-Proofs

Phase 235 does not prove:

- semantic correctness
- model-backed generation
- provider execution
- runtime execution
- live router behavior
- RAG/local lookup
- web lookup
- scheduler/reminder execution
- connector execution
- worker dispatch
- Codex dispatch
- production readiness

It does not broaden the current coding-task success criterion into general
semantic answer quality or production readiness.

## Validation

- `python -m unittest discover -s tests -p "test_phase_235_general_answer_lightweight_report_only_contract.py" -v`
  - PASS
- `python -m py_compile orchestrator/lightweight_answer_report.py`
  - PASS
- `git diff --check`
  - PASS

`PHASE235_GENERAL_ANSWER_LIGHTWEIGHT_REPORT_ONLY_CONTRACT_SOURCE_TEST_DOCS_PROVEN=PASS`

# Phase 265 - General Answer Local-First Fallback Policy

## Boundary

`PHASE_265_GENERAL_ANSWER_LOCAL_FIRST_FALLBACK_POLICY_SOURCE_TEST_DOCS`

## Purpose

Phase 265 codifies a deterministic non-executing local-first/fallback policy
for structured local `general_answer` requests.

The policy records when a structured local request may be treated as a
report-only local answer candidate, when clarification is required, when a
manual-review/block posture is required, and when requests for execution,
lookup, dispatch, or service/API/UI behavior must be blocked.

This phase does not implement answer generation, answer correctness proof,
provider/model/runtime execution, RAG/local lookup, web lookup,
scheduler/reminder execution, connector behavior, worker dispatch, Codex
dispatch, service/API/UI behavior, export/package behavior, production work,
or production readiness.

## Files Changed

Created source:

- `orchestrator/general_answer_local_first_policy.py`

Updated source:

- `orchestrator/manual_review_cli.py`

Created tests:

- `tests/test_phase_265_general_answer_local_first_fallback_policy_contract.py`

Created docs:

- `docs/PHASE_265.md`

Updated docs:

- `docs/TRACKS_AND_OPEN_THREADS.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`

## Policy

Phase 265 adds:

`build_general_answer_local_first_fallback_policy(request)`

The helper returns JSON-safe policy metadata with stable fields for request
type, local-first enablement, report-only posture, false execution flags,
recommended answer posture, fallback posture, clarification/block posture,
missing requirements, blockers, and caveats.

For low-risk structured `general_answer` requests with a user intent summary
and accepted local facts, the policy reports:

- `recommended_answer_posture=local_report_only_answer_candidate`
- `fallback_posture=manual_review`
- `clarification_required=false`
- `block_required=false`
- `answer_generation_authorized=false`

If accepted local facts or user intent details are missing, the policy reports
`clarify_before_answer`.

If provider/model/runtime execution, RAG/local lookup, web lookup,
scheduler/reminder execution, connector behavior, worker dispatch, Codex
dispatch, or service/API/UI behavior is requested, the policy reports
`blocked_execution_request` and keeps every execution flag false.

High-risk or unknown/non-low-risk structured `general_answer` requests report
`manual_review_or_block` and do not authorize answer generation.

Non-`general_answer` requests report `not_applicable`.

## Artifact Integration

Successful structured local `general_answer` review artifacts written through
the existing caller-supplied path:

`--general-answer-input <input_json_path> --write-review-json <artifact_json_path>`

now include the policy payload under:

`general_answer_local_first_policy`

Fixture output remains unchanged. The existing
`artifact_persistence_policy` payload remains unchanged. The successful
artifact-write notice remains exactly:

`Review JSON Artifact Written: <artifact_json_path>`

## Open Thread Status

Phase 265 codifies the local-first/fallback policy for the current structured
local `general_answer` report-only artifact lane.

Broader `general_answer` usability remains open.

`PRODUCT_GENERAL_ANSWER_REAL_INPUT_ADAPTER` remains `DEFERRED_VALID`.

`PRODUCT_GENERAL_ANSWER_REAL_INPUT_ARTIFACT_PERSISTENCE` remains
`DEFERRED_VALID`.

`PRODUCT_AUTONOMY_TIER_POLICY` remains `DEFERRED_VALID`; Phase 265 does not
implement autonomy-tier behavior.

## Non-Proofs

Phase 265 does not prove:

- semantic answer correctness
- semantic answer generation
- model-backed generation
- provider/model/runtime execution
- live route execution
- RAG/local lookup
- web lookup
- scheduler/reminder execution
- connector execution
- worker/Codex dispatch from product code
- service/API/UI behavior
- export/package behavior
- production work
- current-success broadening
- production readiness

## Validation Commands

- `python -m py_compile orchestrator/manual_review_cli.py`
- `python -m py_compile orchestrator/manual_review_runner.py`
- `python -m py_compile orchestrator/lightweight_answer_report.py`
- `python -m py_compile orchestrator/general_answer_artifact_policy.py`
- `python -m py_compile orchestrator/general_answer_local_first_policy.py`
- `python -m unittest discover -s tests -p "test_phase_256_general_answer_real_input_report_only_cli_adapter_contract.py" -v`
- `python -m unittest discover -s tests -p "test_phase_257_general_answer_real_input_review_artifact_persistence_contract.py" -v`
- `python -m unittest discover -s tests -p "test_phase_258_general_answer_json_bom_tolerance_contract.py" -v`
- `python -m unittest discover -s tests -p "test_phase_260_general_answer_review_artifact_write_notice_contract.py" -v`
- `python -m unittest discover -s tests -p "test_phase_263_general_answer_artifact_persistence_policy_contract.py" -v`
- `python -m unittest discover -s tests -p "test_phase_265_general_answer_local_first_fallback_policy_contract.py" -v`
- `git diff --check`
- `git status --short`

## Marker

`PHASE265_GENERAL_ANSWER_LOCAL_FIRST_FALLBACK_POLICY_SOURCE_TEST_DOCS_PROVEN=PASS`

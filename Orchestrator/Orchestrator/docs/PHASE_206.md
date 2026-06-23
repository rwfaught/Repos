# Phase 206 - Route Mediated Provider Smoke Runner Contract

## Purpose

Phase 206 adds the smallest source/test/docs seam for a future
route-mediated provider smoke proof runner. It prepares a controlled runner,
CLI, and caller-supplied artifact path for a later operator runtime proof.

This phase does not execute a route, provider, model, runtime, HTTP endpoint,
WSL, Ollama, Hermes, OpenClaw, Discord, worker dispatch, or production
behavior.

## Source And Tests

Created source:

- `orchestrator/route_mediated_provider_smoke_runner.py`
- `orchestrator/route_mediated_provider_smoke_cli.py`

Created tests:

- `tests/test_phase_206_route_mediated_provider_smoke_runner_contract.py`

## Contract Summary

The runner defines a JSON-safe artifact containing:

- `phase=PHASE_206`
- `artifact_kind=route_mediated_provider_smoke_runner_contract`
- `route_marker=ORCH_ROUTE_PROVIDER_SMOKE_OK`
- `prompt=Return exactly: ORCH_ROUTE_PROVIDER_SMOKE_OK`
- `target_model=qwen3:30b-a3b-instruct-2507-q4_K_M`
- `disallowed_model=qwen3.6:35b-a3b`
- `fallback_candidate=qwen3.6:27b`
- Request intake/harness evidence
- Route recommendation/readiness evidence
- Explicit route execution boundary evidence
- Provider call through route path evidence
- Captured HTTP/status/JSON/model/marker evidence
- Persisted artifact path evidence
- Displayed/reviewable outcome evidence
- Route path packet review
- Non-proofs
- `production_readiness=false`

The runner distinguishes dry artifact preparation, review of caller-supplied
captured results, and future runtime execution mode. The future runtime mode is
explicitly rejected during Phase 206.

## CLI Safety

The CLI default is dry-run/artifact-shape only. It supports caller-supplied
captured-result review without provider/model execution. The
`--allow-provider-call` flag is accepted only so Phase 206 can reject it
explicitly and reviewably.

Phase 206 does not authorize runtime execution.

## Reviewer Behavior

The reviewer reuses the Phase 202 route-path proof packet review posture. It
rejects:

- Direct marker `ORCH_PROVIDER_SMOKE_OK` as route-mediated proof
- Wrong returned model
- Missing route evidence fields
- Production readiness claims

It accepts only a complete caller-supplied shape with
`ORCH_ROUTE_PROVIDER_SMOKE_OK`, returned model
`qwen3:30b-a3b-instruct-2507-q4_K_M`, and all Phase 202 route-path evidence
fields present. Even an accepted review is review/contract acceptance only,
not proof that runtime execution occurred.

## Model Policy

- Active route/proof target: `qwen3:30b-a3b-instruct-2507-q4_K_M`
- Disallowed target: `qwen3.6:35b-a3b`
- Disallowed reason: Roger reported it locks up the laptop every time;
  installed inventory is not runtime suitability proof.
- Fallback candidate: `qwen3.6:27b`
- Current practical policy: test 30B and below only; treat 35B as off-limits
  for this laptop target.

## Current Gap

Current success remains unmet until actual route-mediated provider execution
is proven by a later operator runtime boundary:

request intake/harness -> route recommendation/readiness -> explicit route
execution boundary -> provider call through route path -> captured response ->
persisted artifact -> displayed/reviewable outcome.

## Validation

- `python -m unittest discover -s tests -p "test_phase_206_route_mediated_provider_smoke_runner_contract.py" -v`
  - PASS
- `python -m py_compile orchestrator/route_mediated_provider_smoke_runner.py`
  - PASS
- `python -m py_compile orchestrator/route_mediated_provider_smoke_cli.py`
  - PASS
- `git diff --check` - PASS
- `git diff --cached --check` - PASS

`PHASE206_ROUTE_MEDIATED_PROVIDER_SMOKE_RUNNER_SOURCE_TEST_DOCS_PROVEN=PASS`

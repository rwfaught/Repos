# Phase 208 - Route Mediated Provider Smoke Execution Adapter

## Purpose

Phase 208 adds an explicit guarded route-mediated provider smoke execution
adapter so a later operator boundary can perform the first live
route-mediated provider smoke proof.

This phase adds source/test/docs only. It does not execute a provider, model,
HTTP endpoint, Ollama, WSL, route runtime, worker dispatch, Hermes, OpenClaw,
Discord, or production behavior.

## Source And Tests

Updated source:

- `orchestrator/route_mediated_provider_smoke_runner.py`
- `orchestrator/route_mediated_provider_smoke_cli.py`

Created tests:

- `tests/test_phase_208_route_mediated_provider_smoke_execution_adapter_contract.py`

Updated tests:

- `tests/test_phase_206_route_mediated_provider_smoke_runner_contract.py`

## Adapter Guards

The adapter can reach an injected provider callable only when all guards are
present:

- `allow_route_execution=True`
- `allow_provider_call=True`
- `execution_mode=route_mediated_provider_smoke_execution`
- `target_model=qwen3:30b-a3b-instruct-2507-q4_K_M`
- `route_marker=ORCH_ROUTE_PROVIDER_SMOKE_OK`
- `production_readiness=False`
- A caller-supplied provider callable is provided

The adapter rejects missing allow flags, missing execution mode,
`qwen3.6:35b-a3b`, fallback candidate `qwen3.6:27b` as active target, wrong
marker, production readiness claims, and missing provider callable.

## Artifact Shape

The adapter assembles a JSON-safe artifact with:

- `phase=PHASE_208`
- `artifact_kind=route_mediated_provider_smoke_execution_adapter_contract`
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
- Persisted artifact path evidence when caller-supplied output is used
- Displayed/reviewable outcome evidence
- Route path packet review
- Phase 206 runner review
- Activity flags
- Non-proofs
- `production_readiness=false`

Fake/injected successful adapter tests may mark route/provider/model/
generation/API-generate path flags true only for the injected callable path.
Those flags are not live runtime proof.

## CLI Safety

Default CLI behavior remains help, dry-run, or captured-result review only.
The future runtime-shaped CLI path requires:

- `--execute-route-smoke`
- `--allow-route-execution`
- `--allow-provider-call`
- `--out-dir <path>`

In this phase, tests use only an in-process fake provider callable. No live
HTTP/Ollama transport is invoked.

## Model Policy

- Active route/proof target: `qwen3:30b-a3b-instruct-2507-q4_K_M`
- Route marker: `ORCH_ROUTE_PROVIDER_SMOKE_OK`
- Disallowed target: `qwen3.6:35b-a3b`
- Disallowed reason: Roger reported it locks up the laptop every time;
  installed inventory is not runtime suitability proof.
- Fallback candidate: `qwen3.6:27b`
- Current practical policy: test 30B and below only; treat 35B as off-limits
  for this laptop target.

## Current Gap

Source/test acceptance is not runtime proof. Only a future operator artifact
with actual captured execution evidence may prove route-mediated provider
runtime execution.

Current success remains unmet until actual route-mediated provider execution
is proven.

## Validation

- `python -m unittest discover -s tests -p "test_phase_208_route_mediated_provider_smoke_execution_adapter_contract.py" -v`
  - PASS
- `python -m unittest discover -s tests -p "test_phase_206_route_mediated_provider_smoke_runner_contract.py" -v`
  - PASS
- `python -m py_compile orchestrator/route_mediated_provider_smoke_runner.py`
  - PASS
- `python -m py_compile orchestrator/route_mediated_provider_smoke_cli.py`
  - PASS
- `git diff --check` - PASS
- `git diff --cached --check` - PASS

`PHASE208_ROUTE_MEDIATED_PROVIDER_SMOKE_EXECUTION_ADAPTER_SOURCE_TEST_DOCS_PROVEN=PASS`

# Phase 212 - Route Mediated Provider Smoke Live Transport Adapter

## Purpose

Phase 212 adds an explicit live Ollama transport adapter path for the future
route-mediated provider smoke proof.

This phase adds source/test/docs only. It does not execute a provider, model,
HTTP endpoint, Ollama, WSL, route runtime, worker dispatch, Hermes, OpenClaw,
Discord, or production behavior.

## Source And Tests

Updated source:

- `orchestrator/route_mediated_provider_smoke_runner.py`
- `orchestrator/route_mediated_provider_smoke_cli.py`

Created tests:

- `tests/test_phase_212_route_mediated_provider_smoke_live_transport_adapter_contract.py`

Updated tests:

- `tests/test_phase_206_route_mediated_provider_smoke_runner_contract.py`
- `tests/test_phase_208_route_mediated_provider_smoke_execution_adapter_contract.py`

## Adapter Guards

The live adapter can reach transport only when all guards are present:

- `execute_live_ollama_route_smoke=True`
- `allow_route_execution=True`
- `allow_provider_call=True`
- `allow_ollama_http=True`
- `execution_mode=live_ollama_route_mediated_provider_smoke_execution`
- `target_model=qwen3:30b-a3b-instruct-2507-q4_K_M`
- `route_marker=ORCH_ROUTE_PROVIDER_SMOKE_OK`
- `prompt=Return exactly: ORCH_ROUTE_PROVIDER_SMOKE_OK`
- `production_readiness=False`
- A caller-supplied output path

The adapter rejects missing live execution flags, missing allow flags,
`qwen3.6:35b-a3b`, fallback candidate `qwen3.6:27b` as active target, wrong
marker, wrong prompt, production readiness claims, and missing output path.

## Request Body

The future live Ollama request body is JSON-safe:

- `model=qwen3:30b-a3b-instruct-2507-q4_K_M`
- `prompt=Return exactly: ORCH_ROUTE_PROVIDER_SMOKE_OK`
- `stream=false`
- `options.num_ctx=4096`
- `options.num_predict=64`
- `options.temperature=0`

The default URL is `http://127.0.0.1:11434`, and the endpoint path is
`/api/generate`. Tests use only injected transport and do not call the endpoint.

## Artifact Shape

A successful future live run writes a JSON-safe artifact with:

- `phase=PHASE_212`
- `artifact_kind=route_mediated_provider_smoke_live_transport_adapter_contract`
- `route_marker=ORCH_ROUTE_PROVIDER_SMOKE_OK`
- `prompt=Return exactly: ORCH_ROUTE_PROVIDER_SMOKE_OK`
- `target_model=qwen3:30b-a3b-instruct-2507-q4_K_M`
- `disallowed_model=qwen3.6:35b-a3b`
- `fallback_candidate=qwen3.6:27b`
- `ollama_url`
- `request_body_redacted_or_safe`
- Request intake/harness evidence
- Route recommendation/readiness evidence
- Explicit route execution boundary evidence
- Provider call through route path evidence
- Captured HTTP/status/JSON/model/marker evidence
- Persisted artifact path evidence
- Displayed/reviewable outcome evidence
- Route path packet review
- Phase 206 runner review
- Phase 208 adapter review
- Activity flags
- Non-proofs
- `production_readiness=false`

## Classification

Fake/injected transport validation is classified as:

`test_injected_live_transport_shape_valid_not_runtime_proof`

The runtime classification:

`route_mediated_provider_smoke_runtime_marker_pass`

is reserved for a later operator boundary with actual live HTTP evidence:
HTTP status `200`, JSON parse success `true`, returned model exactly
`qwen3:30b-a3b-instruct-2507-q4_K_M`, marker present in the response text,
`done=true` when present, and persisted artifact path recorded.

Phase 212 source/test acceptance itself never claims runtime proof.

## CLI Safety

Default CLI behavior remains help, dry-run, or captured-result review only.
The future live runtime path requires:

- `--execute-live-ollama-route-smoke`
- `--allow-route-execution`
- `--allow-provider-call`
- `--allow-ollama-http`
- `--out-dir <path>`
- optional `--ollama-url http://127.0.0.1:11434`

Tests use only an in-process injected transport callable. No live HTTP/Ollama
transport is invoked.

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

Phase 212 adds a live transport adapter path only. It does not run provider,
model, Ollama, or HTTP.

Fake/injected transport validation is not runtime proof. The actual live
route-mediated provider smoke proof still requires a later operator runtime
boundary.

Current success remains unmet until actual route-mediated provider execution
is proven.

## Validation

- `python -m unittest discover -s tests -p "test_phase_212_route_mediated_provider_smoke_live_transport_adapter_contract.py" -v`
  - PASS
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

`PHASE212_ROUTE_MEDIATED_PROVIDER_SMOKE_LIVE_TRANSPORT_ADAPTER_SOURCE_TEST_DOCS_PROVEN=PASS`

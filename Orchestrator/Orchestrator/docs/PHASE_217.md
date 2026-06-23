# Phase 217 - Route Mediated Provider Smoke Live Transport Failure Artifact

## Purpose

Phase 217 patches the Phase 212 live route-mediated provider smoke transport
path so live transport failures produce structured JSON failure artifacts
instead of raw traceback-only evidence.

This phase is source/test/docs only. It does not execute a provider, model,
Ollama, HTTP endpoint, WSL, route runtime, worker dispatch, OpenClaw, Hermes,
Discord, or production behavior.

## Source And Tests

Updated source:

- `orchestrator/route_mediated_provider_smoke_runner.py`
- `orchestrator/route_mediated_provider_smoke_cli.py`

Created tests:

- `tests/test_phase_217_route_mediated_provider_smoke_live_transport_failure_artifact_contract.py`

## Failure Artifact Behavior

After all live adapter guards pass and the live transport boundary is entered,
an exception raised by the transport call is classified as:

`live_ollama_transport_exception_not_runtime_proof`

The failure artifact preserves:

- `accepted=false`
- `production_readiness=false`
- `target_model=qwen3:30b-a3b-instruct-2507-q4_K_M`
- `disallowed_model=qwen3.6:35b-a3b`
- `fallback_candidate=qwen3.6:27b`
- `route_marker=ORCH_ROUTE_PROVIDER_SMOKE_OK`
- `prompt=Return exactly: ORCH_ROUTE_PROVIDER_SMOKE_OK`
- `ollama_url`
- endpoint shape `POST local_ollama_http/api/generate`
- JSON-safe request body fields: `model`, `prompt`, `stream=false`,
  `options.num_ctx=4096`, `options.num_predict=64`, and
  `options.temperature=0`
- exception type and sanitized exception message
- captured HTTP/status/JSON/model/marker evidence with `http_status=null`,
  `json_parse_success=false`, empty returned model, empty response text,
  `done=null`, and `marker_present=false`

The activity flags record that the route boundary was entered and the generate
transport call was attempted, but provider/model/Ollama execution is not
accepted without response evidence.

## CLI Behavior

When the live CLI path is invoked with `--out-dir` and the transport call
raises, the CLI writes the structured failure artifact, prints the JSON payload
through the normal output field, emits a concise error, and returns a nonzero
exit code. It does not classify the result as a runtime pass.

Guard failures before the live transport boundary remain guard rejections.

## Phase 216 Relationship

Phase 216 remains failed:

`PHASE_216_ROUTE_MEDIATED_PROVIDER_SMOKE_LIVE_RUNTIME_OPERATOR_PROOF=FAIL_CLI_TRACEBACK_BEFORE_ARTIFACT_VALIDATION`

Phase 216 Retry 1 remains a read-only diagnostic confirming import/help worked
and the live failure escaped before structured artifact validation.

Phase 217 does not convert Phase 216 into runtime proof. It only makes a future
live transport failure reviewable as structured non-proof evidence.

## Current Gap

A failure artifact is evidence of failure shape, not a route-mediated runtime
marker pass. A future retry must still perform the live route-mediated smoke.

Current success remains unmet until an actual live artifact classifies as:

`route_mediated_provider_smoke_runtime_marker_pass`

## Validation

- `python -m unittest discover -s tests -p "test_phase_217_route_mediated_provider_smoke_live_transport_failure_artifact_contract.py" -v`
  - PASS
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

`PHASE217_ROUTE_MEDIATED_PROVIDER_SMOKE_LIVE_TRANSPORT_FAILURE_ARTIFACT_SOURCE_TEST_DOCS_PROVEN=PASS`

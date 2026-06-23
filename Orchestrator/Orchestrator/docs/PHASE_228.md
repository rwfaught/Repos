# Phase 228 - Route Mediated Provider Smoke Live Runtime Proof Registration

## Purpose

Phase 228 registers the accepted operator proof:

`PHASE_216_RETRY3_ROUTE_MEDIATED_PROVIDER_SMOKE_LIVE_RUNTIME_OPERATOR_PROOF=PASS`

This is a documentation registration phase only. It records the operator-supplied
live runtime proof for the route-mediated provider marker smoke path. It does
not run Ollama, call `/api/generate` or `/api/chat`, execute Hermes, OpenClaw,
Discord, WSL, provider/model work, worker dispatch, sustained-load tests,
long-context tests, production tasks, or cleanup/archive behavior.

## Proof Boundary

- Source commit before proof: `a336b36acd9cb75942ab9781395a0a9f6949c52b`
- Proof label:
  `PHASE_216_RETRY3_ROUTE_MEDIATED_PROVIDER_SMOKE_LIVE_RUNTIME_OPERATOR_PROOF=PASS`
- Boundary: exactly one live local Ollama `/api/generate` call through the
  route-mediated live transport CLI.
- Ollama URL: `http://127.0.0.1:11434`
- Target model: `qwen3:30b-a3b-instruct-2507-q4_K_M`
- Disallowed model: `qwen3.6:35b-a3b`
- Route marker: `ORCH_ROUTE_PROVIDER_SMOKE_OK`
- Prompt: `Return exactly: ORCH_ROUTE_PROVIDER_SMOKE_OK`
- Options: `num_ctx=4096`, `num_predict=64`, `temperature=0`,
  `stream=false`
- CLI exit code: `0`
- Artifact phase: `PHASE_212`
- Artifact kind:
  `route_mediated_provider_smoke_live_transport_adapter_contract`
- Mode: `live_ollama_transport_review_only`
- Classification: `route_mediated_provider_smoke_runtime_marker_pass`
- Accepted: `true`
- Production readiness: `false`

## Evidence Artifacts

- Success artifact path:
  `C:\Users\accou\AppData\Local\Temp\orchestrator_phase216_retry3_route_mediated_provider_smoke_live_runtime_20260623_045735\phase_212_route_mediated_provider_smoke_live_transport_adapter_artifact.json`
- Success artifact SHA-256:
  `4706cbd610183fcf760f33eebccd9fbe49ee64f3cb4bd8b645089350df948861`
- CLI stdout path:
  `C:\Users\accou\AppData\Local\Temp\orchestrator_phase216_retry3_route_mediated_provider_smoke_live_runtime_20260623_045735\phase216_retry3_cli_stdout.json`
- CLI stdout SHA-256:
  `c4d93f12bd30e6b828fc4618633fd88195df87b0d9cbb5759cfd65e8c7efc211`
- CLI stderr path:
  `C:\Users\accou\AppData\Local\Temp\orchestrator_phase216_retry3_route_mediated_provider_smoke_live_runtime_20260623_045735\phase216_retry3_cli_stderr.txt`
- CLI stderr SHA-256:
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

## Captured Evidence

- `http_status=200`
- `json_parse_success=true`
- `returned_model=qwen3:30b-a3b-instruct-2507-q4_K_M`
- `response_text=ORCH_ROUTE_PROVIDER_SMOKE_OK`
- `done=true`
- `done_reason=stop`
- `marker_present=true`

Activity flags:

- `route_executed=true`
- `provider_executed=true`
- `api_generate_called=true`
- `model_executed=true`
- `ollama_executed=true`
- `hermes_executed=false`
- `openclaw_executed=false`
- `discord_executed=false`
- `wsl_executed=false`
- `worker_dispatched=false`
- `production_executed=false`

After the proof, `ollama ps` showed
`qwen3:30b-a3b-instruct-2507-q4_K_M` loaded at 18 GB, 100% GPU, context
4096, until 4 minutes from then. GPU after proof was
`18272 MiB / 24463 MiB`. The final repo status after the operator proof was
clean against `origin/main`.

## Registration Result

The route-mediated provider smoke runtime marker path is now accepted for this
single narrow marker-smoke boundary. Phase 217's failure-shape caveat remains
historical for earlier failed attempts, but the Phase 216 Retry 3 operator proof
supplies the later live artifact classified as
`route_mediated_provider_smoke_runtime_marker_pass`.

## Caveats And Non-Proofs

This proof is narrow. It proves only the route-mediated provider marker-smoke
runtime path for the exact target, marker, prompt, options, CLI boundary, and
artifact evidence above.

It does not prove semantic correctness, real workload sufficiency, long-context
behavior, sustained-load stability, production readiness, Hermes behavior,
OpenClaw behavior, Discord behavior, WSL behavior, worker dispatch, or general
provider/model suitability.

It does not authorize use of `qwen3.6:35b-a3b`.

Earlier model acquisition required `OLLAMA_MAX_TRANSFER_STREAMS=1` after the
default multi-stream pull hit Windows resource write failures. A host crash
occurred when Hermes was contacted during acquisition. This registration
preserves those as operational caveats, not as proven root cause.

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

`PHASE228_ROUTE_MEDIATED_PROVIDER_SMOKE_LIVE_RUNTIME_PROOF_REGISTRATION_DOCS_PROVEN=PASS`

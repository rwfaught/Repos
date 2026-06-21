# Package Manifest

## Host Entrypoints

| File | Purpose |
|---|---|
| `init_openclaw_wsl.ps1` | Accepts or prompts for a generic distro name, selects an OpenClaw package spec, stages configuration, and optionally starts installation. |
| `watch_openclaw_wire.ps1` | Watches supervised install state and opens the authenticated dashboard from Windows when the dashboard verifier requests operator input. |
| `Start-OpenClawRuntime.ps1` | Runs a hidden supervisor and foreground PowerShell WSL wrapper, validates live runtime readiness, and precisely stops matching wrapper/anchor processes. |

## Install Pipeline

| File | Purpose |
|---|---|
| `bootstrap_openclaw_wsl.sh` | Installs Linux prerequisites, Ollama, selected models, and the configured OpenClaw package spec. |
| `run_openclaw_supervised_wire.sh` | Runs bootstrap, verification, optional Discord setup, and report stages. |
| `run_openclaw_install_from_config.sh` | Retained config-driven runner used by bootstrap recovery guidance. |
| `apply_openclaw_repro_compat_layer_v1_7.sh` | Validates exact, pinned-version, or latest-package identity and applies the legacy compatibility layer only to its matching package. |
| `patch_openclaw_readonly_external_plugins_v1_7.sh` | Provides the Discord setup compatibility patch. |

## Verification And Optional Features

| File | Purpose |
|---|---|
| `verify_openclaw_baseline.sh` | Verifies baseline OpenClaw and Ollama configuration. |
| `verify_openclaw_dashboard.sh` | Verifies dashboard and gateway behavior. |
| `verify_openclaw_optional_models.sh` | Verifies optional model availability. |
| `openclaw_gateway_auth_helper_v1.sh` | Supports dashboard authentication handoff. |
| `configure_openclaw_discord_v1.sh` | Optional Discord configuration using prompt, environment, or token-file reference. |
| `verify_openclaw_discord_v1.sh` | Base Discord verification helper. |
| `verify_openclaw_discord_v1_7.sh` | Supervised Discord verification stage. |
| `verify_openclaw_runtime_readiness.sh` | Restarts the gateway and gates completion on final gateway and Discord readiness. |
| `write_wire_ratification_report_v1_7.sh` | Produces the supervised install report from generated markers. |

## Routing Payload

| File | Purpose |
|---|---|
| `local_worker_routing_v1.json` | Declarative local worker routing scaffold retained for compatibility. |
| `Get-LocalWorkerRoutingConfig_v1.ps1` | Reads and validates routing configuration. |
| `Invoke-LocalWorkerRouting_v1.ps1` | Routing wrapper referenced by the runtime bridge. |
| `Invoke-LocalWorkerRoutingRuntimeBridge_v1.ps1` | Staged routing bridge retained by the current installer contract. |
| `Invoke-LocalWorkerLiveProbeAdapter_v1.ps1` | Adapter required by the routing bridge when its live mode is selected. |

## Documentation

`README.md`, `QUICK_START.md`, `PACKAGE_MANIFEST.md`, `MIGRATION_REPORT.md`, `VALIDATION_REPORT.md`, `MODEL_ROSTER_AND_RAG_BENCHMARK_LEDGER.md`, `RAG_METADATA_SCHEMA_AND_RETRIEVAL_CONTRACT.md`, and `RAG_MINIMAL_IMPLEMENTATION_PLAN.md` define operation, scope, proof, accepted model acquisition state, RAG embedding benchmark policy, the accepted RAG metadata schema/retrieval contract, and the documentation-only future minimal RAG implementation plan.

Global operator wrappers are stored in the sibling `tools` directory as `openclaw-install.ps1/.cmd` and `openclaw-bot.ps1/.cmd`.

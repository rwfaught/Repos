# Supported Executable Surfaces

## Operator quick start

Run commands from `Orchestrator/Orchestrator` with the checked-in Windows
interpreter:

```text
.venv\Scripts\python.exe -m orchestrator.operator_coding_task_packet_cli
```

This is the single `CANONICAL_SUPPORTED` operator entry point. It is the
canonical-alpha coding-task packet lifecycle, not a general product CLI and
not a provider/model selection surface. See
[`OPERATOR_CODING_TASK_PACKET_CLI_RUNBOOK.md`](OPERATOR_CODING_TASK_PACKET_CLI_RUNBOOK.md)
for packet shape, authorization, and trusted-worker requirements.

The safe no-worker probes are deliberately limited:

```text
.venv\Scripts\python.exe -m orchestrator.operator_coding_task_packet_cli
.venv\Scripts\python.exe -m orchestrator.operator_coding_task_packet_cli --reconcile --data-root <existing-or-empty-data-root>
```

The first prints a blocked JSON usage result; the second is read-only lifecycle
reconciliation. Supplying `--packet-json` together with a worker command is an
execution request and must be separately authorized. This CLI has no `--help`
mode; use this document and the runbook instead.

For repository validation, use the separate supported developer test command:

```text
.venv\Scripts\python.exe -B scripts\run_deterministic_tests.py
```

It is `TEST_OR_REFERENCE_ONLY`, not an operator product command. It discovers
every `tests/test_*.py` module and uses a temporary data root; see
[`DETERMINISTIC_TESTING.md`](DETERMINISTIC_TESTING.md).

## Classification rules

`CANONICAL_SUPPORTED` means the supported current operator route. Every other
status below is intentionally noncanonical:

- `LEGACY_RETAINED` remains callable for compatibility/history but must not be
  presented as current product operation.
- `DIAGNOSTIC_DIRECT_ENTRY` is a bounded inspection, fixture, dry-report, or
  explicitly caller-scoped tool; it is not a product operator route.
- `TEST_OR_REFERENCE_ONLY` is for deterministic tests, test runners, and
  import-only/reference modules.
- `RETIRED_DO_NOT_RUN` names historical scripts that may start services, call
  providers, rewrite files, or otherwise act outside the current contract.

When an executable-looking surface is not listed, do not promote it by
convenience: inspect its source, its current callers, and this document first.
If it can perform provider/model/platform work, start services, or mutate a
non-disposable location, require a separate authorization boundary.

## Source-backed inventory

The inventory was generated from the current tree: eight non-test Python files
contain a `__main__` guard; there are 216 `tests/test_*.py` modules, 214 of
which have a direct `unittest` guard. The two without a direct guard remain
discovered by the deterministic runner. The 34
`orchestrator/product_task_packet_*readback.py` modules have no direct-entry
guard and are import/test reference surfaces.

| Surface and invocation | Purpose and current references | State mutation / provider capability | Classification and evidence |
| --- | --- | --- | --- |
| `orchestrator.operator_coding_task_packet_cli` — `.venv\Scripts\python.exe -m orchestrator.operator_coding_task_packet_cli` | Canonical structured coding-task packet lifecycle. Referenced by the canonical runbook, `CAPABILITY_REALITY_MAP.md`, `CURRENT_SUCCESS_CRITERION.md`, and `test_canonical_alpha_runtime.py`. | Empty/invalid invocation is no-activity; `--reconcile` is read-only. An explicitly authorized packet plus `--worker-command` persists records and launches only the selected trusted local worker. | `CANONICAL_SUPPORTED`. The module exposes `main`, parses canonical/reconcile modes, and the runbook identifies this as the authoritative canonical-alpha route. |
| `main.py` — `.venv\Scripts\python.exe main.py <command>` | Historical 49-command compatibility/control surface. `tests/test_main_compatibility_map.py` asserts its exact command set; historical docs reference it. | Several commands initialize state, create records, execute tasks, or select providers. | `LEGACY_RETAINED`. It has no canonical delegates and is explicitly described as noncanonical in the canonical runbook. Do not use it for current alpha operation. |
| `orchestrator.manual_review_cli` — `python -m orchestrator.manual_review_cli ...` | Deterministic fixture/manual-review adapter, documented in `MANUAL_REVIEW_CLI_RUNBOOK.md` and covered by Phase 119–121 tests. | Normally no provider/worker/runtime action; optional `--write-review-json` writes only to the caller-supplied path. | `DIAGNOSTIC_DIRECT_ENTRY`. It is explicitly not a productized CLI or execution path. |
| `orchestrator.dry_mvp_loop_cli` — `python -m orchestrator.dry_mvp_loop_cli --out-dir <dir>` | Thin dry-MVP demo/readback, documented in `DRY_MVP_LOOP_DEMO_CLI.md` and covered by `test_dry_mvp_loop_demo_cli.py`. | Writes demo task/dry-result artifacts only under the caller-supplied output directory; no provider/worker execution. | `DIAGNOSTIC_DIRECT_ENTRY`. A dry demonstration, not the supported operator path. |
| `orchestrator.tiny_vertical_tracer_cli` — `python -m orchestrator.tiny_vertical_tracer_cli ...` | Deterministic Phase 169 dry tracer report; documented in `TINY_VERTICAL_TRACER_CLI_RUNBOOK.md`. | Read-only except optional dry-artifact output to a caller-supplied directory; source states provider/route/worker execution is false. | `DIAGNOSTIC_DIRECT_ENTRY`. Its dry report is not live routing or product operation. |
| `orchestrator.route_mediated_provider_smoke_cli` — `python -m orchestrator.route_mediated_provider_smoke_cli ...` | Historical provider-smoke adapter, covered by Phase 206/208/212/217 tests. | Dry/review modes may write caller-scoped artifacts. Source also contains guarded injected-provider and live-Ollama execution branches. | `DIAGNOSTIC_DIRECT_ENTRY`. Do not invoke any execute/live-Ollama variant without a separate provider/runtime authorization. |
| `tools/phase85_ollama_live_smoke.py` — `python tools/phase85_ollama_live_smoke.py` | Historical guarded Ollama smoke harness, documented in `PHASE_85.md` and protected by `test_phase_85_ollama_live_smoke_guard.py`. | With `ORCH_PHASE85_ALLOW_LIVE_OLLAMA=YES`, it can call the Ollama provider. | `RETIRED_DO_NOT_RUN`. Its old guard does not make live provider execution part of the current supported contract. |
| `scripts/run_deterministic_tests.py` — `.venv\Scripts\python.exe -B scripts\run_deterministic_tests.py` | Standard deterministic unittest discovery runner, documented in `DETERMINISTIC_TESTING.md`. | Uses a temporary data root; no provider/model/network/WSL/production execution. | `TEST_OR_REFERENCE_ONLY`. This is the supported validation command, not an operator product command. |
| `scripts/run_phase_51_local_validation.sh` | Historical targeted Phase 51 validation script. | Creates timestamped `test_logs` output and runs a limited test subset. | `TEST_OR_REFERENCE_ONLY`. It is historical/narrow and not the deterministic-suite replacement. |
| `run_acceptance_tests.sh` | Historical WSL-oriented acceptance script; its source hard-codes `/home/roger/codex/projects`, starts Ollama, and may pull a model. | Mutates project data/logs, starts services, calls a provider, and may download a model. | `RETIRED_DO_NOT_RUN`. Never use it as a validation shortcut. |
| `update_from_shell.2026-04-18.sh` | Historical repository update script. | Copies backup files and rewrites project documentation/process files. | `RETIRED_DO_NOT_RUN`. It is a dated broad mutation script, not a current maintenance entry point. |
| `tests/test_*.py` (216 modules; 214 direct `unittest` guards) | Regression tests, including fixture and phase modules. The deterministic runner discovers the whole collection. | Tests use controlled fixtures/temporary state; they are not product/operator commands. | `TEST_OR_REFERENCE_ONLY`. Invoke through the deterministic runner, not by treating a test module as an operational surface. |
| `orchestrator/product_task_packet_*readback.py` (34 import-only modules) and directly imported phase/fixture modules | Deterministic governance/readback and fixture contracts, primarily called from matching tests and described in `OPERATOR_CODEBASE_MAP.md`. | They expose source/test report shapes; no CLI/main dispatcher is present. | `TEST_OR_REFERENCE_ONLY`. Readback/reference status is not worker dispatch, provider execution, or an operator command. |

## What this contract does and does not prove

This contract proves current source/documentation classification and the
canonical command location. It does not prove semantic correctness, safe
untrusted-worker execution, provider/model quality, service/API/UI behavior,
production readiness, or a product wedge. The canonical CLI's trusted-local
worker path remains a separately authorized local execution decision; it does
not authorize provider/model/platform behavior.

`UNRESOLVED_REQUIRES_CTO_DECISION`: none identified in the current executable
inventory. Classification is limited to the surfaces above; a future surface
with materially different compatibility requirements needs CTO review before
being declared supported.

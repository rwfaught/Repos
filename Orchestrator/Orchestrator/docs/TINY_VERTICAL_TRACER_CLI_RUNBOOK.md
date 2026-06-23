# Tiny Vertical Tracer CLI Runbook

## Purpose

The tiny vertical tracer CLI-compatible adapter provides a product-internal
command surface over the Phase 169 dry tracer report. It renders the existing
deterministic `safe_direct_answer` dry vertical flow and can optionally write
the JSON dry artifact to a caller-supplied directory.

It is not provider execution, route execution, live routing, worker dispatch,
service/API/UI productization, semantic correctness proof, or production
readiness.

## Commands

Run from the product repo root:

`python -m orchestrator.tiny_vertical_tracer_cli --help`

`python -m orchestrator.tiny_vertical_tracer_cli --list-fixtures`

`python -m orchestrator.tiny_vertical_tracer_cli --fixture safe_direct_answer`

`python -m orchestrator.tiny_vertical_tracer_cli --fixture safe_direct_answer --format json`

`python -m orchestrator.tiny_vertical_tracer_cli --fixture safe_direct_answer --write-artifact --out-dir <caller_supplied_dir>`

## Expected Output Fields

Successful output should include:

- `phase=PHASE_169`
- `artifact_kind=tiny_vertical_tracer_dry_report`
- `fixture_id=safe_direct_answer`
- `recommended_route=local_first_answer`
- `provider_catalog_key=local_model_candidate`
- `model_metadata_evidence_name=qwen3.6:27b`
- `route_selection_readiness=future_probe_ready_qwen36_27b_evidence_registered`
- `readiness_status=not_ready_for_execution`
- `outcome_classification=dry_vertical_flow_reviewable_not_executable`
- `provider_selection_allowed=false`
- `provider_execution_allowed=false`
- `route_execution_allowed=false`
- `generation_allowed=false`
- `production_readiness=false`

JSON output exposes the same dry report payload plus
`adapter_phase=PHASE_176`.

## Artifact Writing Behavior

Without `--write-artifact`, the adapter renders to stdout only and does not
persist a file.

With `--write-artifact --out-dir <caller_supplied_dir>`, the adapter writes the
Phase 169 JSON dry artifact only inside the caller-supplied directory and
prints `written_json_path=<path>` in text mode. The persistence classification
is `test_dry_artifact_persistence_not_route_execution`.

`--write-artifact` without `--out-dir` returns non-zero and does not write an
artifact. Unknown fixtures return non-zero and do not write an artifact.

Only `safe_direct_answer` is accepted in Phase 176.

## No-Execution Posture

The adapter preserves false execution authority for provider selection,
provider execution, route execution, generation, and production readiness.

The adapter also preserves no activity for provider/model execution, route
execution, worker dispatch, Codex dispatch, Ollama/WSL/OpenClaw/Hermes/
Discord, RAG/web/scheduler/connector behavior, service/API/UI behavior,
cleanup/delete/archive, and production execution. In the written-artifact case,
only dry artifact persistence may be true.

## Troubleshooting

- If `--list-fixtures` does not show `safe_direct_answer`, verify the module is
  being run from the product repo root.
- If `--write-artifact` fails, provide `--out-dir <caller_supplied_dir>`.
- If a fixture other than `safe_direct_answer` is supplied, the Phase 176
  adapter rejects it conservatively by design.
- Use `--format json` when a caller needs structured payload inspection.

## Non-Proofs

Phase 176 does not prove provider/model execution, route execution, live
routing, worker dispatch, Codex dispatch inside the product harness, semantic
correctness, model loadability, VRAM sufficiency, RAG/web/scheduler/connector
behavior, service/API/UI productization, cleanup/delete/archive behavior,
production execution, or production readiness.

The CLI adapter is a deterministic command surface over an existing dry report
contract only.

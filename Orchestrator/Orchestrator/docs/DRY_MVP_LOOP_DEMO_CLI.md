# Dry MVP Loop Demo CLI

Boundary: `DRY_MVP_LOOP_DEMO_CLI_SOURCE_TEST_DOCS`

## Purpose

This seam adds a thin standard-library readback surface over the deterministic dry MVP loop.

It writes demo task and dry-result artifacts only to a caller-supplied output directory.

## Usage

```powershell
python -m orchestrator.dry_mvp_loop_cli --out-dir <caller_supplied_dir> --format text
python -m orchestrator.dry_mvp_loop_cli --out-dir <caller_supplied_dir> --format json
```

## Non-Proofs

The CLI does not dispatch a real worker, call a model/provider/runtime, mutate project files, select a product wedge, implement Phase 387, or prove semantic correctness.

## Recommended Next Boundary

`DRY_MVP_INTEGRATED_ACCEPTANCE_SOURCE_TEST_DOCS`

# Phase 121 - Manual Review CLI Runbook And Golden Smoke Contract

## Status

Locally docs/test-proven.

Marker:

`PHASE121_MANUAL_REVIEW_CLI_RUNBOOK_GOLDEN_SMOKE_LOCAL_DOCS_TEST_PROVEN=PASS`

## Purpose

Add an operator-facing runbook and golden smoke contract for the manual review
CLI-compatible adapter proven through Phase 120.

## Changed Files

- `docs/MANUAL_REVIEW_CLI_RUNBOOK.md`
- `tests/test_phase_121_manual_review_cli_runbook_golden_contract.py`
- `docs/PHASE_121.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`

## Runbook Added

`docs/MANUAL_REVIEW_CLI_RUNBOOK.md` documents the manual adapter purpose,
fixture-listing and fixture-review commands, expected fixture IDs, expected
review sections, exit-code posture, golden smoke interpretation, and
troubleshooting guidance.

## Golden Smoke Test Added

`tests/test_phase_121_manual_review_cli_runbook_golden_contract.py` verifies
the runbook content and the stable adapter behavior through
`build_manual_review_cli_output(...)` without shelling out to providers,
platforms, runtimes, or external services.

## Validation Performed

- `git status --short --branch`
- `python -m unittest tests.test_phase_121_manual_review_cli_runbook_golden_contract`
- `python -m unittest tests.test_phase_119_manual_review_cli_adapter_contract`
- `python -m orchestrator.manual_review_cli --list-fixtures`
- `python -m orchestrator.manual_review_cli --fixture safe_direct_answer`
- `python -m orchestrator.manual_review_cli --fixture safe_coding_report_only`
- `python -m orchestrator.manual_review_cli --fixture production_execution_blocked; Write-Output "LASTEXITCODE=$LASTEXITCODE"`
- `git status --short --branch`

## Source Snapshot Refresh Status

`C:\Users\accou\Desktop\Repos\Source Files\Update-SourceFiles.ps1` was run
after validation. Generated ZIP files under `Source Files` were not staged.

## Git Staging Proof

Root commit staging used explicit `git add` commands for the intended Phase 121
files only. `git diff --cached --name-status` was used to verify no generated
ZIP files were staged.

## Git Commit/Push Status

Committed with:

`git commit -m "Add manual review CLI runbook"`

Pushed to `origin/main`.

## Explicit Non-Proofs

Phase 121 does not prove service/API/UI productization, CLI framework
expansion, source behavior changes to `manual_review_cli.py`, live prompt
inference, raw prompt-to-route implementation, natural-language intent
inference, regex classification, live routing, route execution, worker
execution, Codex or Relay invocation from product code, concrete substrate
selection, provider/model/runtime/platform selection or execution, RAG/local
lookup, web lookup, scheduler/reminder implementation, connector execution,
file mutation behavior, artifact export/package behavior, cleanup, deletion,
archive, production execution, or production readiness.

## Caveats

- The golden smoke contract documents and tests deterministic adapter behavior
  only.
- Blocked fixture non-zero exit is conservative stop behavior, not a crash.
- Runbook success is not coordinator acceptance, worker dispatch, route
  execution, service/API/UI, or production readiness.

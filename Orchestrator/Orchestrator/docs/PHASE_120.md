# Phase 120 - Manual Review CLI Module Entrypoint Fix

## Status

Locally source/test/smoke-proven.

Marker:

`PHASE120_MANUAL_REVIEW_CLI_MODULE_ENTRYPOINT_LOCAL_SOURCE_TEST_SMOKE_PROVEN=PASS`

## Purpose

Fix the Phase 119 manual review CLI adapter so module invocation works with:

`python -m orchestrator.manual_review_cli ...`

Operator smoke before this fix proved direct calls to
`build_manual_review_cli_output(...)` worked for fixture listing, safe fixture
rendering, report-only fixture rendering, and conservative production-execution
blocking. The module entrypoint guard was missing, so `python -m
orchestrator.manual_review_cli ...` produced no visible output.

## Changed Files

- `orchestrator/manual_review_cli.py`
- `tests/test_phase_119_manual_review_cli_adapter_contract.py`
- `docs/PHASE_120.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`

## Fix Added

- `main(argv=None)` now reads `sys.argv[1:]` when invoked as a module.
- `main(...)` prints `output_text` to stdout and `error_text` to stderr.
- The module now exits through `raise SystemExit(main())` under the standard
  `if __name__ == "__main__":` guard.

## Validation Performed

- `git status --short --branch`
- `python -m py_compile orchestrator/manual_review_cli.py orchestrator/manual_review_runner.py orchestrator/coordinator_review_report.py orchestrator/fixture_packet_pipeline.py`
- `python -m unittest tests.test_phase_119_manual_review_cli_adapter_contract`
- `python -m orchestrator.manual_review_cli --list-fixtures`
- `python -m orchestrator.manual_review_cli --fixture safe_direct_answer`
- `python -m orchestrator.manual_review_cli --fixture safe_coding_report_only`
- `python -m orchestrator.manual_review_cli --fixture production_execution_blocked`
- `git status --short --branch`

## Explicit Non-Proofs

Phase 120 remains read-only/manual-adapter level. It does not prove
service/API/UI productization, CLI framework expansion, live prompt inference,
raw prompt-to-route implementation, natural-language intent inference, regex
classification, live routing, route execution, worker execution, Codex or Relay
invocation from product code, concrete substrate selection,
provider/model/runtime/platform selection or execution, RAG/local lookup, web
lookup, reminder/scheduler implementation, connector execution, file mutation
behavior, artifact export/package behavior, cleanup, deletion, archive,
production execution, or production readiness.

## Caveats

- This phase fixes module invocation only.
- The adapter still renders deterministic review text; it is not coordinator
  acceptance, worker dispatch, route execution, service/API/UI, or production
  readiness.

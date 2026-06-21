# Manual Review CLI Runbook

## Purpose

The manual review CLI-compatible adapter is a local manual review handle for
deterministic fixture-based coordinator review output. It is useful for
checking the Phase 118 through Phase 120 review path from a module invocation.

It is not productized CLI/UI, live routing, worker dispatch, or execution.

## Commands

Run from the product repo root:

`python -m orchestrator.manual_review_cli --list-fixtures`

`python -m orchestrator.manual_review_cli --fixture safe_direct_answer`

`python -m orchestrator.manual_review_cli --fixture safe_coding_report_only`

`python -m orchestrator.manual_review_cli --fixture production_execution_blocked`

## Expected Fixture IDs

- `ambiguous_needs_clarification`
- `platform_provider_external_boundary`
- `production_execution_blocked`
- `safe_coding_docs_only_mutation`
- `safe_coding_report_only`
- `safe_coding_source_test_mutation`
- `safe_direct_answer`
- `substrate_smuggling_blocked`
- `unknown_capability_blocked`

## Expected Review Sections

Successful review text should include these sections:

- `Assessment`
- `Accepted Facts`
- `Decision`
- `NBM`
- `Deliverable/Command`
- `RESPONSE_METADATA`

## Exit-Code Posture

- `--list-fixtures` returns `0`.
- Accepted safe fixtures return `0`.
- Blocked or conservative fixtures may return non-zero by design.
- Non-zero for blocked fixtures is not a crash; it is conservative stop behavior.

## Golden Smoke Interpretation

Success means deterministic manual adapter invocation works.

Success does not mean coordinator acceptance, worker dispatch, route execution,
production readiness, provider/model execution, RAG, web lookup,
scheduler/reminder behavior, connector access, file mutation behavior,
cleanup/delete/archive, or service/API/UI.

## Troubleshooting

- If `python -m orchestrator.manual_review_cli ...` prints nothing, check for
  a missing `if __name__ == "__main__": raise SystemExit(main())` module
  entrypoint guard.
- If a blocked fixture returns non-zero, capture `$LASTEXITCODE` rather than
  treating that as a product defect.
- Use `git status --short --branch` before and after smoke to confirm no
  mutation.

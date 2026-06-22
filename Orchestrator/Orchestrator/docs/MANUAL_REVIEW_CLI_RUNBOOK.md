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

Default manual review output includes provider probe packet status, but does
not authorize probe packet drafting.

`python -m orchestrator.manual_review_cli --fixture safe_direct_answer --draft-provider-probe-packet --authorize-probe-boundary --probe-kind read_only_future_probe_plan --probe-surface provider_runtime_surface --probe-scope read_only_probe_command_draft --expected-evidence captured_future_probe_output`

The provider probe packet command is paperwork only. It drafts deterministic
manual review metadata for a future boundary and does not execute a probe,
provider, model, runtime, worker, RAG, web, scheduler, connector, route, or
production behavior.

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
- `Router Policy`
- `Provider Probe Packet`

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

Provider probe packet status does not mean probe authorization, provider availability proof,
model availability proof, provider runtime import,
provider/model execution, route execution, or production readiness. If
authorization, scope, or expected evidence is missing, the status should remain
blocked/missing requirements.

Phase 130 registered an operator golden smoke of the explicit paperwork command
with expected rendered metadata and clean git status; the command exit code was
not separately captured. Phase 131 registered a separate read-only local
Ollama `/api/tags` proof. That provider surface visibility is not generation,
chat, model correctness, route execution, worker dispatch, or production
readiness.

Phase 133 registered a separate read-only local Ollama `/api/show` metadata
proof for `qwen3-30b-24k:latest`; Phase 134 registers that proof in source
docs/ledgers without rerunning it. Metadata visibility is not generation,
chat, semantic correctness, model loadability, VRAM sufficiency, route
execution, worker dispatch, RAG/web/scheduler/connector work, or production
readiness.

Phase 135 and Phase 136 registered git checkpoint proofs for the Phase 130
through Phase 134 provider-proof ledger chain. Commit/push checkpoint language
means source publication of prior proof ledgers only; it does not rerun manual
review, execute provider probes, invoke models, execute routes, or prove
production readiness.

## Troubleshooting

- If `python -m orchestrator.manual_review_cli ...` prints nothing, check for
  a missing `if __name__ == "__main__": raise SystemExit(main())` module
  entrypoint guard.
- If a blocked fixture returns non-zero, capture `$LASTEXITCODE` rather than
  treating that as a product defect.
- Use `git status --short --branch` before and after smoke to confirm no
  mutation.

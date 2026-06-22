# Provider Probe Boundary Packet

## Purpose

The provider probe boundary packet is a deterministic, non-executing airlock
between router/provider policy and any future provider/runtime probe. It drafts
reviewable paperwork for what would need to be authorized before a local
provider, frontier provider, worker/Codex boundary, RAG/local-document
boundary, web/research boundary, scheduler/reminder boundary, connector, or
platform/runtime surface could be probed.

It does not execute probes, providers, models, runtimes, platforms, workers,
RAG, web, schedulers, connectors, routes, or production behavior.

## Packet Inputs

The packet request records:

- `request_id`
- `source_router_recommendation`
- `requested_probe_kind`
- `requested_surface`
- `operator_authorized_probe_boundary`
- `allowed_probe_scope`
- `expected_evidence`
- `stop_conditions`
- `caveats`

The source router recommendation must be a structured Phase 126-style
router/provider recommendation envelope. Missing, blocked, or clarification
recommendations are rejected.

## Packet Draft

Accepted drafts preserve:

- provider catalog key, tier, and future allowed probe boundary
- requested probe kind and surface
- purpose
- allowed operations
- explicit exclusions
- validation expectations
- expected evidence
- stop conditions
- non-proofs
- activity flags
- caveats
- `coordinator_acceptance_required=true`

All activity flags remain false. Catalog entries whose execution flags are
false may still draft future-boundary paperwork, but that paperwork is not
execution authority.

## Blocking Rules

Packet drafting blocks when:

- structured router recommendation is missing
- operator probe-boundary authorization is missing
- allowed probe scope is missing
- expected evidence is missing
- the router recommendation is `block` or `ask_clarification`
- the provider catalog key is `provider_blocked_or_unavailable`
- the catalog posture is unsupported for future probe paperwork
- any source activity flag claims execution or probing already occurred

## Non-Proofs

The packet is not provider/model execution, provider/model availability proof,
runtime/platform execution, worker/Codex dispatch, route execution, RAG/local
lookup, web lookup, scheduler/reminder execution, connector execution, or
production readiness.

Future provider/runtime proof remains a separate explicitly authorized
boundary.

## Manual Review Status

Phase 128 surfaces provider probe packet status in manual review artifacts.
By default, manual review does not authorize packet drafting; it reports the
missing authorization, allowed scope, and expected evidence requirements.

An explicit deterministic test/request path may provide authorization, scope,
and expected evidence to prove that packet paperwork is draftable, but the
result remains non-executing and coordinator acceptance is still required
before any future probe boundary.

## CLI Draft Adapter

Phase 129 adds an explicit manual review CLI adapter path for provider probe
packet paperwork:

`python -m orchestrator.manual_review_cli --fixture safe_direct_answer --draft-provider-probe-packet --authorize-probe-boundary --probe-kind read_only_future_probe_plan --probe-surface provider_runtime_surface --probe-scope read_only_probe_command_draft --expected-evidence captured_future_probe_output`

The CLI path is deterministic manual review output only. It does not probe a
provider, import a runtime, execute a model, dispatch a worker, perform lookup,
schedule work, execute a route, or prove production readiness.

# Local-First Model Router Policy

## Purpose

The local-first model/router policy is a deterministic, non-executing contract
for recommending boundary posture from structured request metadata. It helps
decide whether a request should stay local-first, require frontier/provider
review under a separate boundary, move to a worker/Codex boundary, move to
RAG/local-document lookup, move to scheduler/reminder handling, move to
web/research handling, or block/clarify.

The policy does not execute providers, models, workers, RAG, web lookup,
schedulers, connectors, runtimes, platforms, or production behavior.

## Recommendation Fields

Each recommendation records:

- `request_id`
- `recommended_route`
- `provider_posture`
- `confidence`
- `reason`
- `fallback`
- `escalation_posture`
- `required_boundary`
- `blocked_conditions`
- `missing_requirements`
- `non_proofs`
- `activity_flags`

## Route Outcomes

- `local_first_answer`: low-risk answer/report posture may stay local-first
  when direct answer is explicitly allowed and no missing/high-risk/retrieval
  condition blocks it.
- `worker_codex_boundary`: coding and file-mutation routes require a bounded
  worker/Codex boundary; this is not dispatch.
- `rag_local_document_boundary`: local-document lookup routes require a
  RAG/local-document boundary; this is not lookup.
- `scheduler_reminder_boundary`: reminder routes require scheduler/reminder
  confirmation and boundary; this is not scheduling.
- `web_research_boundary`: research routes require explicit web/research
  boundary; this is not browsing.
- `separate_provider_or_platform_boundary_required`: provider/model and
  platform/runtime capabilities require separate authority.
- `block`: production execution is blocked unless a future explicit production
  boundary authorizes it.
- `ask_clarification`: missing or invalid request type, confidence, or
  capability authority must be clarified before routing.

## Escalation Posture

Escalation is posture only. Frontier/provider review may be recommended only
as a separately authorized boundary and never as implicit provider/model
execution. Coding/file work moves to a worker boundary only as a required
boundary recommendation; the policy does not dispatch a worker or invoke Codex.

## Non-Proofs

The policy preserves non-proofs including:

- `router_policy_is_not_provider_execution`
- `router_policy_is_not_model_execution`
- `router_policy_is_not_live_router`
- `router_policy_is_not_worker_dispatch`
- `router_policy_is_not_route_execution`
- `router_policy_is_not_rag_lookup`
- `router_policy_is_not_web_lookup`
- `router_policy_is_not_scheduler_execution`
- `router_policy_is_not_production_readiness`

All no-activity flags remain false.

## Relationship To Intake Routing

This policy sits after structured request intake and route validation doctrine.
It does not infer raw natural-language intent, validate route envelopes, admit
execution, select providers/models/runtimes/platforms, or override capability
registry maturity. It uses structured route/request metadata as evidence for a
recommended next boundary only.

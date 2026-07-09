# Local-First Capability Routing Triage

## Purpose

Orchestrator should recommend the least powerful executor that can reasonably
handle a task while keeping owner control and reviewability visible. This
triage surface is deterministic and inspectable. It recommends a route; it
does not execute that route.

## Supported routes

- `deterministic_code_only`: use a bounded local deterministic check when the
  task is simple and validation is available.
- `local_model_candidate`: consider a local model attempt for moderate,
  reviewable drafting or summarization. A model such as Qwen 3.6 27B is only a
  candidate reference; this surface does not run or validate it.
- `frontier_model_or_codex_required`: recommend a stronger reasoning boundary
  for high-complexity coding or architecture work.
- `external_api_required`: identify a task whose requested tool/API dependency
  must be handled in a separate owner-approved integration boundary.
- `human_review_or_blocked`: stop or clarify when risk, privacy, missing
  authority, live runtime need, or lack of reviewability makes automated
  routing unsafe.

## Capability factors

The classifier requires explicit values for complexity, code-generation need,
long-context need, safety risk, privacy sensitivity, external tool/API need,
live runtime need, mistake tolerance, deterministic validation availability,
and whether local output can be reviewed before action.

The ordering is intentionally conservative: high-consequence or regulated work
goes to human review first; external dependencies are deferred; complex coding
is escalated; simple deterministic work stays local; reviewable moderate drafting
can become a local-model candidate.

## Operator commands

```text
python -m orchestrator.capability_routing_cli --summary --format markdown
python -m orchestrator.capability_routing_cli --task local_model_drafting_candidate --format markdown
python -m orchestrator.capability_routing_cli --task frontier_coding_architecture --format markdown
```

The summary groups the five deterministic fixtures by route. A selected task
report shows the capability factors, rationale, blockers or deferrals, and next
bounded action.

## Relationship to existing routing

This surface is a capability-level triage layer. It does not replace the
existing model/provider policy or provider evidence registry. A future
authorized execution boundary may use this recommendation as an input, but
must independently validate authority, availability, and execution conditions.

## Non-proofs

The triage does not prove model competence, Qwen loadability, Codex behavior,
provider availability, route execution, semantic correctness, production
readiness, first product wedge selection, or Phase 387 resumption.

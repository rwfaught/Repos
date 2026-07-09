# Objective-to-Route-to-Packet V1 Candidate Loop

## What this adds

The objective loop connects three existing ideas into one operator-facing
surface:

1. Roger supplies an objective string.
2. Deterministic fixed-signal intake converts it into explicit capability
   factors.
3. The capability router recommends the least powerful reasonable route.
4. Orchestrator produces an owner-review packet and neutral dossier/case
   bridge readback where the objective is sufficiently specified.
5. The report names the next bounded action without executing it.

The objective text is not treated as authoritative semantic understanding.
Recognized signals are intentionally visible, and insufficiently specified
objectives are routed to human review/clarification.

## How to run

From the experimental worktree:

```text
python -m orchestrator.objective_route_packet_cli --objective "Summarize these internal policy notes for staff review" --format markdown
python -m orchestrator.objective_route_packet_cli --objective "Classify this fixed status list into three labels" --format markdown
python -m orchestrator.objective_route_packet_cli --objective "Design a multi-module architecture migration with compatibility constraints" --format markdown
python -m orchestrator.objective_route_packet_cli --objective "Sync live CRM records through an external API" --format markdown
python -m orchestrator.objective_route_packet_cli --objective "Review this regulated financial decision with sensitive personal data" --format markdown
```

The first command is the intended local-model-candidate proving workflow. It
returns a readable route, rationale, deterministic-first steps, owner-review
packet, neutral-case relationship, and next bounded action.

## Route behavior

- Simple fixed classification routes to `deterministic_code_only`.
- Reviewable drafting or summarization routes to `local_model_candidate`.
- Complex architecture or multi-module coding routes to
  `frontier_model_or_codex_required`.
- Live CRM/API/integration objectives route to `external_api_required` and are
  deferred to a separate boundary.
- Regulated, sensitive, high-stakes, or unclear objectives route to
  `human_review_or_blocked`.

## Packet and neutral-case posture

The packet is a deterministic readback artifact. It records route rationale,
safe local posture, owner approval, blockers, evidence produced, and next
action. The neutral dossier/case bridge is structural compatibility evidence;
it does not select a product wedge or authorize Phase 387.

## Explicit non-proofs

This loop does not prove natural-language intent understanding, model
competence, local-model loadability, provider/API availability, Codex behavior,
route execution, owner approval, packet persistence, semantic correctness, or
production readiness. It does not run models, APIs, providers, WSL, Ollama,
Hermes, or external services.

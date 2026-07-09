# Local AI Consulting Sandbox Experiment

## Boundary and posture

`GPT56_LOCAL_AI_CONSULTING_SANDBOX_AUTONOMOUS_BUILDOUT` is an isolated
experiment on `experiment/gpt56-local-ai-consulting-wedge`, based at
`a882bb960f9686f62bd316276716fe2047141f52`. It is not accepted project state,
does not mutate authoritative `main`, and does not ratify a product wedge.

The client-facing offer is a fictional `$150 Local AI Efficiency Audit` for
Roger, acting as a local AI consultant for small businesses. The primary
scenario is the fictional Springfield HVAC Service Company.

## Files in this sandbox surface

- `orchestrator/local_ai_consulting_audit_packet.py`
- `tests/test_local_ai_consulting_audit_packet.py`
- `docs/LOCAL_AI_CONSULTING_SANDBOX_EXPERIMENT.md`

## Product-shaped flow

The deterministic source surface now exposes an inspectable flow:

1. `build_local_ai_consulting_fixture_library()` provides the fictional
   scenario library.
2. `build_audit_intake()` creates a structured intake record with the offer,
   target user, business profile, source basis, workflow facts, friction,
   repeated tasks, intervention candidates, questions, and unclear claims.
3. `classify_risk_privacy_posture()` preserves controls and marks human review
   as required.
4. `classify_do_not_automate_yet()` preserves deferred actions as explicit
   human-decision items.
5. `build_audit_review_gate()` reports required-field coverage, open questions,
   contradictions, owner approval requirement, and execution lockout.
6. `build_internal_implementation_packet()` produces the internal packet and
   readback.
7. `build_client_readable_audit_report()` produces the client-facing report.
8. `build_local_ai_consulting_audit_flow()` returns the complete deterministic
   intake-to-report evidence surface.

The recommended first implementation is still only a scenario-local
recommendation: a staff-facing missed-call and service-inquiry follow-up draft
assistant using supplied notes, with human review and no autonomous action.

## Review and evaluation shape

The focused tests cover intake fields, deterministic generation of every major
surface, risk/privacy controls, deferred automation items, question and
contradiction preservation, recommendation presence, explicit non-proofs,
product-wedge posture, Phase 387 posture, execution lockouts, and the complete
intake-to-report flow.

Expected targeted validation is:

```text
python -m py_compile orchestrator\local_ai_consulting_audit_packet.py
python -m unittest -v tests.test_local_ai_consulting_audit_packet
git diff --check
```

## What this does not prove

This sandbox does not prove runtime/provider/model execution, semantic
correctness, production readiness, customer value, real business applicability,
autonomous sending, external integration, or successful use with real customer
data. It does not contain phone, CRM, email, calendar, dispatch, billing, or
messaging integration code. Phase 387 remains unset/not resumed, and no first
product wedge is selected or ratified.

## CTO compare-back

CTO should compare the three allowed files, their full diff, targeted test
output, and dirty-tree status against the authoritative main repository. The
compare-back should ask whether the flow is coherent and inspectable, whether
the risk and human-review boundaries are legible, and whether the evidence
remains clearly separate from live capability or product acceptance.

Any promotion, ratification, integration, runtime proof, or product-direction
decision requires a separate explicitly authorized boundary.

## One-more-pass direction

If another sandbox-only pass is authorized, the next useful increment would be
to add more fictional scenario fixtures and a cross-fixture comparison report,
while preserving the same deterministic schema and non-proof posture. That
would test generality without introducing external data, integrations, or
runtime behavior.

# Local AI Consulting Sandbox Experiment

## Boundary and posture

`GPT56_LOCAL_AI_CONSULTING_SANDBOX_AUTONOMOUS_INTEGRATION_WEDGE` is an isolated
follow-on experiment on `experiment/gpt56-local-ai-consulting-wedge`, verified
at starting commit `70c218ca9fc6a1efbed305b678160c08e92e6053`. It is not accepted project state,
does not mutate authoritative `main`, and does not ratify a product wedge.

The client-facing offer is a fictional `$150 Local AI Efficiency Audit` for
Roger, acting as a local AI consultant for small businesses. The primary
scenario is the fictional Springfield HVAC Service Company.

## Files in this sandbox surface

- `orchestrator/local_ai_consulting_audit_packet.py`
- `tests/test_local_ai_consulting_audit_packet.py`
- `orchestrator/local_ai_consulting_campaign.py`
- `tests/test_local_ai_consulting_campaign.py`
- `docs/LOCAL_AI_CONSULTING_SANDBOX_EXPERIMENT.md`

## Product-shaped flow

The deterministic source surface exposes an inspectable flow:

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

The integration pass adds a bounded Path A adapter bridge plus the Path B
product-shaped packet spine. `build_local_ai_consulting_case_packet()` maps the
intake into the existing neutral case-packet fields.
`build_dossier_case_bridge_readback()` then calls the existing dossier mapping
and neutral task-readiness surfaces and reports preservation checks. This keeps
the existing neutral dossier/case semantics authoritative rather than
duplicating or modifying them.

The recommended first implementation is still only a scenario-local
recommendation: a staff-facing missed-call and service-inquiry follow-up draft
assistant using supplied notes, with human review and no autonomous action.

The bridge is structurally ready for owner review under the existing neutral
task-readiness report. That is structural compatibility evidence only; it is
not semantic readiness or product acceptance.

## Multi-stage campaign pass

The campaign pass chooses Path D: a partial adapter/readback bridge. A
consulting-specific owner packet and self-review layer now cover four fictional
fixtures: low-risk internal knowledge/helpdesk, owner-reviewed drafting and
reporting, regulated or sensitive data, and external-integration-heavy work.

Each packet separates locally safe exploration, owner approval, missing inputs,
external dependencies, deferred automation, and explicit non-proofs. The
readback classifies each fixture as owner-review ready, missing input, blocked
by sensitivity, or blocked by external integration, then compares the packets
through the existing neutral dossier/case adapter. The neutral adapter remains
authoritative; this campaign does not select a product wedge or resume Phase
387.

## Review and evaluation shape

The focused tests cover intake fields, deterministic generation of every major
surface, risk/privacy controls, deferred automation items, question and
contradiction preservation, recommendation presence, explicit non-proofs,
product-wedge posture, Phase 387 posture, execution lockouts, the complete
intake-to-report flow, and the adapter bridge into the existing neutral
dossier/case task-readiness surfaces.

Expected targeted validation is:

```text
python -m py_compile orchestrator\local_ai_consulting_audit_packet.py tests\test_local_ai_consulting_audit_packet.py
python -m py_compile orchestrator\local_ai_consulting_campaign.py tests\test_local_ai_consulting_campaign.py
python -m unittest -v tests.test_local_ai_consulting_audit_packet tests.test_local_ai_consulting_campaign tests.test_dossier_case_task_readiness tests.test_dossier_case_mapping tests.test_dossier_case_mapping_readback
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
the risk and human-review boundaries are legible, whether the adapter preserves
the neutral dossier/case spine, and whether the evidence remains clearly
separate from live capability or product acceptance.

Any promotion, ratification, integration, runtime proof, or product-direction
decision requires a separate explicitly authorized boundary.

## One-more-pass direction

The campaign comparison is now present. A later sandbox-only pass could test
additional fixture variation or improve packet wording, while preserving the
same deterministic schema and non-proof posture. Any promotion, ratification,
runtime proof, or product-direction decision requires a separate explicitly
authorized boundary.

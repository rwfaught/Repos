# Coordinator-Agent Loop Architecture

## Purpose

Orchestrator is not intended to become a deterministic keyword classifier with
worker-shaped output. The intended architecture is a governed loop:

```text
operator prompt
  -> intake interpretation
  -> coordinator plan
  -> capability route
  -> worker handoff
  -> worker result
  -> review/evaluation
  -> retry, escalate, accept, or block
  -> coordinator closeout
  -> operator cockpit/readback
```

The current implementation is a dry-run architecture surface. It proves the
control seams and state transitions without calling a model, dispatching a
worker, or executing a task.

## Ownership boundaries

### Deterministic Python owns

- typed state objects and serialization;
- explicit route vocabulary and safety gates;
- bounded packet shape and handoff exclusions;
- deterministic checks and validation tripwires;
- review action transitions;
- evidence/readback formatting;
- execution lockouts and non-proof declarations.

Deterministic Python must not pretend to understand ambiguous natural language
or make semantic claims that require reasoning evidence.

### The reasoning model owns in the future

- interpreting an operator prompt into a structured objective;
- extracting nuanced constraints, assumptions, risks, and missing information;
- proposing a coordinator plan inside the allowed governance envelope;
- explaining uncertainty and asking useful clarification questions.

The current `interpret_operator_prompt()` function is an explicit stub seam.
Future local-model execution should plug into that seam through the strict
contract in `orchestrator/local_model_reasoning_contract.py` and the disabled
provider interface in `orchestrator/local_model_provider_stub.py`. The model
must return structured interpretation, not hidden control flow, and its output
must remain subject to deterministic validation and operator approval.

### The coordinator owns

- deciding whether intake is sufficient for planning;
- combining interpretation with capability policy;
- selecting a worker type as a recommendation;
- creating a bounded plan and handoff;
- preserving approval gates and stop conditions;
- reviewing worker/evaluator evidence;
- choosing accept, retry recommendation, escalation, block, or clarification;
- producing operator-facing closeout.

The coordinator does not silently dispatch work or grant authority that the
operator/boundary did not provide.

### Workers own

- executing only the explicitly handed-off bounded scope after authorization;
- producing a result artifact and validation evidence;
- reporting failure, uncertainty, and scope violations;
- stopping when the handoff is insufficient or contradictory.

Workers do not rank product direction, broaden scope, or ratify completion.

### Reviewer/evaluator owns

- checking result shape and stated validation evidence;
- classifying the result as `accept`, `needs_retry`, `escalate`, `blocked`, or
  `needs_operator_clarification`;
- preserving failure and uncertainty rather than smoothing them into success.

Evaluation is not semantic correctness proof unless a separately authorized
evaluation method supports that claim.

### The operator owns

- supplying or correcting the objective;
- approving model/provider/runtime boundaries;
- approving worker handoffs and mutations;
- deciding whether to accept, retry, escalate, or stop after readback;
- ratifying product direction and production claims.

## Dry-run command

```text
python -m orchestrator.coordinator_agent_loop_cli --objective "Summarize these internal policy notes for staff review" --format operator
```

Use `--format operator` for the concise PM/founder readback. It combines the
coordinator's decision, safe local planning steps, owner approval gates,
blocked/deferred conditions, evidence produced, next bounded action, and the
neutral dossier/case relationship. `--format markdown` remains available for
the full internal control-flow readback, and the default `--format json`
remains the machine-readable surface.

The operator packet reuses the existing objective-route owner packet and its
neutral dossier/case adapter readback. This connects control-flow evidence to
the neutral substrate without changing that substrate or selecting a product
wedge. A case bridge is withheld when intake cannot establish a safe objective.

When a future provider returns raw text, the coordinator records the raw output
and its normalization classification before applying the existing contract.
Only strict JSON or the explicitly allowed empty-think/end-marker wrapper can
be accepted. Prose, multiple candidates, malformed JSON, and authority-shaped
fields remain rejected or quarantined and fall back to deterministic intake.

The report shows intake, plan, route, worker handoff, synthetic dry result,
review action, coordinator closeout, and explicit non-proofs. For a deterministic
objective the dry worker result can be accepted as a bounded stub result. Local
model, frontier/Codex, API, and human-review routes remain clarify/escalate/
blocked without execution.

For contract-only seam testing, a caller may supply JSON without invoking a
model:

```text
python -m orchestrator.coordinator_agent_loop_cli --objective "Classify this fixed status list into three labels" --format operator --model-output-json <structured-json>
```

Accepted structured reasoning is still only candidate intake data. Malformed,
low-confidence, ambiguous, unsupported, overreaching, or high-risk responses
are rejected or quarantined and the deterministic intake fallback is retained.
The model response cannot select a route, create a plan, authorize execution,
dispatch a worker, or satisfy operator approval.

## Future local-model authorization checklist

Before the intake model seam can execute, a separate boundary must define:

- approved local provider/model and fresh capability evidence;
- prompt and structured-output contract;
- privacy/redaction handling;
- timeout, failure, and retry policy;
- persistence and artifact ownership;
- deterministic schema validation;
- operator approval and stop conditions;
- proof required to distinguish model output from semantic correctness.

Until then, the loop is architecture/readback evidence only.

## Non-proofs

This architecture does not prove model competence, local-model availability,
worker dispatch, task execution, retry execution, API/provider execution,
semantic correctness, product value, production readiness, product-wedge
selection, or Phase 387 resumption.

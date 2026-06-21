# Prompt To Envelope Inference

## Purpose

This doctrine defines the future boundary for turning raw prompt text into
structured intake and candidate route envelopes.

- Raw prompt interpretation is not execution.
- Prompt inference is not route admission.
- Prompt inference is not provider/model selection.
- Prompt inference is not worker substrate selection.
- Prompt inference is not permission to mutate, schedule, retrieve, connect,
  execute, export, package, or perform production work.
- Inference output is proposal evidence only until validated and admitted.

## Inference Boundary

Future prompt-to-envelope inference may infer only proposal evidence from raw
prompt text, including:

- candidate request type
- tentative intent summary
- possible required capabilities
- missing inputs
- risk signals
- whether clarification is needed
- whether a separate boundary may be required

Future prompt-to-envelope inference must not infer these without explicit
operator declaration:

- file mutation permission
- scheduling/reminder confirmation
- connector authorization
- local document source authority
- web/research boundary
- provider/model/runtime/platform execution
- worker substrate selection
- production execution
- cleanup/delete/archive authority
- export/package authority

## Confidence And Clarification Rules

Confidence handling must be conservative:

- Low confidence must produce `needs_clarification`.
- Conflicting signals must produce `needs_clarification`.
- Missing permission must block mutation, scheduling, connector, retrieval, and
  execution routes.
- High-risk tasks require an explicit boundary or operator confirmation.
- Inferred route type alone is never sufficient for execution.

## Fixture Discipline

Future prompt-to-envelope fixtures are the proof layer for this behavior.

Fixture cases must include at least:

- simple direct answer
- coding report-only
- coding mutation request
- local document lookup request
- web research request
- reminder/scheduler request
- connector-required request
- file operation request
- platform/runtime/provider/model request
- ambiguous request
- unsafe or unsupported request
- substrate-smuggling request
- cleanup/delete/archive request
- export/package request
- production execution request

Fixtures must prove both positive classification and conservative blocking.

## Output Shape

Future inference output is structured intake, not execution. It should map
toward Phase 111 `RequestIntakeRecord` fields without requiring immediate code
changes:

- `request_id`
- `observed_request_summary`
- `request_type`
- `confidence`
- `required_capabilities`
- `missing_inputs`
- `risk_level`
- `execution_policy`
- `recommended_next_action`
- `requires_operator_confirmation`
- `requires_external_connector`
- `allowed_to_answer_directly`
- `allowed_to_mutate_files`
- `allowed_to_schedule`
- `allowed_to_use_local_documents`
- `allowed_to_use_web`
- `reasoning_summary_for_operator`
- `caveats`
- `intake_source`

Any inferred output remains proposal evidence only until route-envelope
validation, capability assessment, risk doctrine review, and coordinator
admission decision occur.

## Stop Conditions

Prompt-to-envelope inference must stop or produce clarification/blocking when
any of these are present:

- ambiguity
- missing required permission
- conflicting request signals
- unsupported capability
- blocked/external capability
- substrate smuggling
- high-risk action without confirmation
- insufficient source authority
- request requires platform/external track
- request would require production execution

## Non-Proofs

This doctrine does not prove:

- prompt-to-envelope implementation
- model/provider inference
- live router
- route execution
- RAG/local lookup
- web lookup implementation
- scheduler/reminder implementation
- connector execution
- file mutation behavior
- provider/model/runtime/platform execution
- production readiness

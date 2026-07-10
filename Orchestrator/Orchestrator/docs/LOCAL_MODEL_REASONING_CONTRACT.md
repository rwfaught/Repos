# Local-Model Reasoning Contract

## Purpose

This fork contains a contract-only seam for future local-model intake
reasoning. It defines how an operator objective could be presented to a model
and how a structured interpretation could be validated before the coordinator
sees it.

The seam is disabled by default. The static provider accepts caller-supplied
JSON for deterministic tests and demos; it does not invoke a model. The
coordinator continues to own policy, routing, planning, handoff, review, and
approval gates.

## Request shape

`LocalModelInterpretationRequest` contains:

- `contract_version`
- `request_id`
- `objective`
- `requested_outcome`
- `owner_context`

## Response shape

`StructuredModelInterpretation` contains only intake fields:

- request/objective identity;
- normalized objective;
- a schema-validated capability task;
- matched signal categories;
- confidence;
- clarification needs;
- risk flags and assumptions.

It does not contain route authorization, worker selection, coordinator plans,
handoff authority, execution flags, or operator approval.

## Validation and fallback

The validator requires the exact contract fields, matching request identity,
valid capability values, confidence of at least `0.70`, and no clarification
request. Extra authority-shaped fields are rejected. Low-confidence,
ambiguous, and high-risk interpretations are quarantined. Any rejection,
quarantine, disabled provider result, provider exception, or provider result
that claims execution causes deterministic signal-based intake to be used.

When a validated stub interpretation is accepted, it is passed into the
existing deterministic `create_capability_route()` policy. The model does not
choose the route directly.

## Raw-output normalization

`normalize_local_model_output()` preserves the exact raw text and extracts at
most one JSON object. Strict JSON is classified as `strict_json`. The only
embedded wrapper artifacts currently allowed are an empty `<think></think>`
prefix and `[end of text]` suffix, which produce `extracted_embedded_json`.

The normalizer reports these explicit states:

- `strict_json`
- `extracted_embedded_json`
- `rejected_malformed_json`
- `rejected_multiple_json_candidates`
- `rejected_no_json_candidate`
- `rejected_authority_or_execution_claim`
- `quarantined_ambiguous_output`

Unclassified prose or wrapper text is quarantined, not stripped. Multiple
top-level objects are rejected. Wrapper-looking text inside a quoted JSON
string is preserved because extraction only considers object delimiters outside
quoted strings. Extracted candidates still pass through
`validate_local_model_interpretation()` before coordinator intake can consume
them.

## Dry-run provider seam

- `DisabledLocalModelProvider` reports that the seam is unavailable.
- `StaticLocalModelProvider` returns caller-supplied data for tests.
- Both explicitly report `execution_performed=False`.

No provider, runtime, network, subprocess, Ollama, WSL, or Qwen import is used
by this seam.

## Non-proofs

This contract proves only source/test behavior around a structured boundary. It
does not prove local-model execution, Qwen availability or competence,
provider behavior, semantic correctness, coordinator autonomy, route
authorization, worker dispatch, production readiness, product value, or
product-wedge selection.

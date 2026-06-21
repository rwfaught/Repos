# INTAKE_TRIAGE_DESIGN_02.md

## Intake/Triage Design 02: Machine-Readable Outcome Shapes

---

## Goal

Define the minimum machine-readable outcome objects for the intake judgment layer established in `INTAKE_TRIAGE_DESIGN_01_REVISED.md`.

This artifact should specify how the three intake outcomes:

- `proceed`
- `clarify`
- `blocked`

are represented in structured form so that future software surfaces, orchestration layers, and human-facing interfaces can consume the same intake judgment without inventing their own meanings.

This is a **design artifact**.

It is not:
- an implementation phase
- an API design
- a transport specification
- a planner phase
- a UX copy spec
- a full intake ontology

Its job is narrower:

to define the smallest stable machine-readable intake outcome contract before any intake implementation begins.

---

## Why This Artifact Exists

`INTAKE_TRIAGE_DESIGN_01_REVISED.md` defined the constitutional intake boundary.

That artifact established:
- what `proceed`, `clarify`, and `blocked` mean
- how they differ
- what each outcome permits
- which architectural dangers they are meant to prevent

That was necessary first.

But until those outcomes have stable machine-readable shapes, future implementation work will still be at risk of drift.

Without structured outcome objects, different surfaces may start inventing their own ad hoc representations of:
- what clarification is needed
- what kind of blocked condition occurred
- whether decomposition is allowed
- what the operator should do next

That would recreate the same semantic-fork danger the project is already trying to avoid elsewhere.

This artifact exists to define one intake outcome contract before any surface implements it.

---

## Core Design Question

If the intake layer decides `proceed`, `clarify`, or `blocked`, what exact structured object should it return so that:

- software can act on it deterministically
- humans can understand it clearly
- future interfaces do not invent alternate meanings
- non-`proceed` outcomes cannot silently trigger decomposition

This artifact answers that question.

---

## Required Design Outcome

Define a minimum structured outcome contract for intake judgment.

At minimum, every intake outcome object must answer these questions:

1. What is the outcome?
2. Is decomposition permitted?
3. What explanation should be shown to a human?
4. If clarification is required, what input is missing?
5. If blocked, what kind of obstacle is present?
6. What is the next allowed operator-facing action?

The shapes must remain:

- explicit
- small
- non-overlapping
- transport-agnostic
- compatible with the current architectural discipline

---

## What This Artifact Is NOT About

This artifact is NOT about:

- how the intake judgment is computed
- how many clarification turns are allowed
- implementing planners
- implementing service interfaces
- deciding HTTP response formats
- defining authentication
- defining idempotency or locking
- defining the full decomposition schema
- building connector capability models in full
- writing final UX text for all cases

This artifact defines output shapes only.

---

## Required Base Shape

All intake outcomes should share a common base shape.

A minimum acceptable common structure is:

```json
{
  "outcome": "<proceed|clarify|blocked>",
  "decomposition_permitted": true,
  "human_explanation": "..."
}
```

This common base must be extended by outcome-specific fields.

### Required common fields

- `outcome`
  - one of:
    - `proceed`
    - `clarify`
    - `blocked`

- `decomposition_permitted`
  - boolean
  - must be:
    - `true` only for `proceed`
    - `false` for `clarify`
    - `false` for `blocked`

- `human_explanation`
  - plain-language explanation suitable for operator visibility
  - must remain legible and actionable

This base shape is required because future surfaces must not infer decomposition permission from prose alone.

---

## Outcome-Specific Shapes

### 1. Proceed Shape

`proceed` means bounded decomposition may begin.

Minimum shape:

```json
{
  "outcome": "proceed",
  "decomposition_permitted": true,
  "human_explanation": "I have enough to frame this into bounded work."
}
```

Optional future fields may be added later, but this artifact should keep `proceed` minimal.

The important requirement is:
- no additional field should be required just to authorize decomposition
- `proceed` must remain the simplest shape

### 2. Clarify Shape

`clarify` means decomposition is not yet allowed because a bounded interpretive input is missing.

Minimum shape:

```json
{
  "outcome": "clarify",
  "decomposition_permitted": false,
  "human_explanation": "I can help, but I still need to know whether your source data will be screenshots, CSV exports, or manual entries.",
  "clarification_request": {
    "question": "What is the source form of the input data?",
    "required_input_kind": "source_format"
  }
}
```

### Required `clarify` fields

- `clarification_request`
  - object
  - required for `clarify`

Inside it, required fields should include:

- `question`
  - the bounded clarification question to present

- `required_input_kind`
  - short machine-readable label for the missing distinction
  - examples:
    - `source_format`
    - `output_format`
    - `time_range`
    - `target_scope`

This field should stay narrow and descriptive.
It is not a full ontology.

### Clarify rules

- `clarify` must not include decomposition-ready task content
- `clarify` must not silently encode a preferred interpretation as if judgment were already settled
- `clarify` exists to request one bounded missing input, not to mask speculative planning

### 3. Blocked Shape

`blocked` means decomposition is not allowed because a non-interpretive blocking condition is present.

Minimum shape:

```json
{
  "outcome": "blocked",
  "decomposition_permitted": false,
  "human_explanation": "I cannot do this yet because no note source is connected.",
  "blocked_reason": {
    "type": "missing_connector",
    "detail": "No note source is currently available to inspect."
  }
}
```

### Required `blocked` fields

- `blocked_reason`
  - object
  - required for `blocked`

Inside it, required fields should include:

- `type`
  - machine-readable blocked subtype

- `detail`
  - short explanation of the actual obstacle

### Allowed baseline blocked subtypes

This artifact should preserve a minimum blocked subtype set:

- `missing_input`
- `missing_permission`
- `missing_connector`
- `unsupported_capability`
- `policy_restricted`
- `insufficient_evidence`

The labels may evolve later, but this baseline set should be treated as the starting contract.

### Blocked rules

- `blocked` must not contain a clarification question in disguise
- `blocked` must not permit decomposition
- `blocked` must name the obstacle class explicitly
- `blocked` must not collapse into generic failure prose

---

## Required Next-Action Surface

Each outcome should also expose a small machine-readable next-action field.

This field exists so future software surfaces do not have to infer the next permitted move from explanation prose alone.

Minimum field:

- `next_action`

### Proposed allowed values

- for `proceed`
  - `begin_decomposition`

- for `clarify`
  - `request_clarification`

- for `blocked`
  - `surface_blocked_condition`

### Example full shapes

#### Proceed

```json
{
  "outcome": "proceed",
  "decomposition_permitted": true,
  "human_explanation": "I have enough to frame this into bounded work.",
  "next_action": "begin_decomposition"
}
```

#### Clarify

```json
{
  "outcome": "clarify",
  "decomposition_permitted": false,
  "human_explanation": "I can help, but I still need to know whether your source data will be screenshots, CSV exports, or manual entries.",
  "clarification_request": {
    "question": "What is the source form of the input data?",
    "required_input_kind": "source_format"
  },
  "next_action": "request_clarification"
}
```

#### Blocked

```json
{
  "outcome": "blocked",
  "decomposition_permitted": false,
  "human_explanation": "I cannot do this yet because no note source is connected.",
  "blocked_reason": {
    "type": "missing_connector",
    "detail": "No note source is currently available to inspect."
  },
  "next_action": "surface_blocked_condition"
}
```

---

## Decomposition Control Rule

This artifact must explicitly protect one rule:

**No intake outcome other than `proceed` may authorize internal task decomposition.**

That means:

- `clarify` cannot create bounded tasks yet
- `blocked` cannot create bounded tasks yet
- future interfaces must not treat good explanations as permission to proceed anyway

This rule is critical.

Without it, the intake outcome object becomes descriptive prose rather than a real control boundary.

---

## Human vs Machine Layers

This artifact should preserve both layers clearly:

### Machine layer
- structured fields
- stable labels
- deterministic control meaning

### Human layer
- `human_explanation`
- bounded clarification question where relevant
- actionable obstacle explanation where relevant

Neither layer should replace the other.

Machine fields alone are too cold and underspecified for operators.
Human prose alone is too fuzzy for software control.

The design must keep both.

---

## Relationship To Future Interfaces

This artifact is transport-agnostic.

These outcome objects should be consumable by:
- CLI surfaces
- future APIs
- future GUIs
- future automation clients

That is why the fields must remain:
- interface-neutral
- semantically stable
- not dependent on one transport style

This matters because the project has already ratified the principle that future interfaces must remain adapters over one governing layer rather than invent alternate control semantics.

---

## Protected Non-Goals

This design rejects the following premature moves:

- embedding decomposition plans into `clarify`
- embedding hidden workaround behavior into `blocked`
- using prose alone to encode control meaning
- creating interface-specific outcome meanings
- turning `required_input_kind` into a large taxonomy too early
- turning blocked subtype labels into a full ontology now
- adding confidence scores or fuzzy ranking systems at this stage

The point is to define a stable minimum contract, not a large intake framework.

---

## Deliverable Shape

This artifact should establish:

1. the common base shape for intake outcomes
2. the minimum required fields for:
   - `proceed`
   - `clarify`
   - `blocked`
3. the required blocked subtype baseline
4. the required clarification-request shape
5. the `next_action` control field
6. the explicit non-`proceed` decomposition prohibition

No implementation plan is required yet.

No phase packet should be opened until this contract is judged coherent.

---

## Validation Standard

This artifact is acceptable only if it:

- makes intake outcomes machine-readable without becoming bloated
- keeps decomposition permission explicit rather than inferential
- preserves the distinction between ambiguity and blockage
- gives both software and operators legible intake results
- remains transport-agnostic
- does not drift into API or planner implementation detail

---

## Expected Next Step After This Artifact

If this artifact is ratified, the likely next move would be either:

- a third intake design artifact for intake-judgment input shape and evidence sources
- or a bounded implementation phase for a minimal service-level intake judgment surface

Neither should begin until this outcome contract is judged sound.

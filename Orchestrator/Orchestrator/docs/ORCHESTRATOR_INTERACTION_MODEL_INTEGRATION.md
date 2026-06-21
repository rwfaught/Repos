# ORCHESTRATOR_INTERACTION_MODEL_INTEGRATION.md

## Purpose

This companion artifact gives the minimal repo integration plan for `ORCHESTRATOR_INTERACTION_MODEL.md`.

It should be used only if the operator chooses to admit the interaction model as a repo document.

Do not treat this as implementation authority by itself.

---

## Recommended File Addition

Add:

- `docs/ORCHESTRATOR_INTERACTION_MODEL.md`

This should be a governance/operating-protocol artifact.

It should not be classified as a phase, fix, product strategy memo, or product design memo.

---

## Minimal Cross-Reference Amendments

### 1. Amend `docs/ORCHESTRATOR_METHOD.md`

Recommended insertion location:

After `Part VIII — Method 2.0 Live Rules`, before `Final instruction`.

Recommended section:

```md
---

# Part IX — Interaction Model

Conversational Orchestrator behavior is treated as a prototype surface for the eventual framework Orchestrator.

Response protocols are not merely stylistic. They model future system-control semantics, including active-layer detection, document-authority classification, decision-membrane visibility, approval gates, ratification state changes, handoff boundaries, report intake, evidence-based closure, and re-entry discipline.

The authoritative interaction model is defined in `ORCHESTRATOR_INTERACTION_MODEL.md`.

This does not authorize new work by itself. It constrains how Orchestrator sessions should interpret their own behavior during project development and how future framework work should understand the control semantics being prototyped in conversation.
```

### 2. Amend `docs/STARTUP_BRIEF.md`

Recommended insertion location:

Startup script step 1 read list.

Add:

```md
- `ORCHESTRATOR_INTERACTION_MODEL.md`
```

Recommended insertion after the read list:

```md
Also preserve the distinction between Conversational Orchestrator and Framework Orchestrator: the project sessions are not merely planning conversations; they are prototype executions of the control semantics the framework should eventually internalize.
```

### 3. Amend `docs/PROJECT_CONTEXT.md`

Recommended insertion location:

Near the top-level project identity/context section.

Add:

```md
During development, Orchestrator exists in two coupled forms: Conversational Orchestrator, the disciplined operating mode used in project sessions, and Framework Orchestrator, the eventual local-first product intended to internalize those same governance semantics. The conversation is therefore not merely planning about the product; it is also a prototype surface for the product's future control behavior.
```

### 4. Optional Amendment To `docs/PROJECT_VISION.md`

Recommended only if the operator wants the dual-form concept in the constitutional layer.

Recommended insertion location:

Under `What The Project Is`, after the paragraph ending with `The project should be understood as a governing layer, not as agent theater.`

Add:

```md
During development, that governing layer is being modeled in two coupled forms: the conversational Orchestrator that coordinates repo-truth-governed project work with the operator, and the eventual framework Orchestrator that should internalize the same control semantics locally. The conversation is a scaffold for the framework, not a separate activity.
```

Use the optional amendment cautiously. `PROJECT_VISION.md` should remain constitutional and should not absorb too much operating-protocol detail.

---

## Action Log Entry

If the document is admitted, append a concise action log entry similar to:

```md
- ORCHESTRATOR_INTERACTION_MODEL admitted: added `docs/ORCHESTRATOR_INTERACTION_MODEL.md` to make explicit the dual-form development model in which Conversational Orchestrator acts as a prototype surface for Framework Orchestrator control semantics; cross-referenced in method/startup/context docs without authorizing new product work.
```

---

## Codex Handoff Prompt

```text
You are performing a documentation-only governance update for the local-first Orchestrator project.

Add `docs/ORCHESTRATOR_INTERACTION_MODEL.md` exactly from the provided artifact.

Then make only the minimal cross-reference amendments described in `ORCHESTRATOR_INTERACTION_MODEL_INTEGRATION.md`:
1. add a short Part IX pointer in `docs/ORCHESTRATOR_METHOD.md`
2. add `ORCHESTRATOR_INTERACTION_MODEL.md` to the `docs/STARTUP_BRIEF.md` startup read set and include the dual-form reminder
3. add the dual-form context paragraph to `docs/PROJECT_CONTEXT.md`
4. optionally amend `docs/PROJECT_VISION.md` only if explicitly instructed by the operator
5. append the concise action-log entry to `docs/ACTION_LOG.md`

Do not modify product code.
Do not create a phase document.
Do not create a new persona.
Do not alter current success criteria.
Do not use this document to authorize new implementation work.

When complete, report:
- files changed
- exact sections modified
- confirmation that no product code was changed
- any wording deviations from the provided artifact
```

---

## Recommendation

Admit the standalone document and cross-reference it from method/startup/context.

Do not bury the whole interaction model inside `ORCHESTRATOR_METHOD.md`.

Do not create a persona document.

Do not amend `PROJECT_VISION.md` unless the operator wants the dual-form concept elevated to constitutional language.


# Codex Bounded-Autonomy Prompt Surface

## Purpose

This document defines a reusable docs-only Codex prompt and report surface for
Orchestrator product-track work after the Backbone V0 declaration and
post-declaration consolidation preservation record.

The surface lets Codex work for longer inside an explicit boundary without
gaining coordinator authority, broad mutation authority, runtime/provider/
model/platform authority, or permission to collapse accepted facts, inference,
proofs, and non-proofs.

## Applicability

Use this surface when the operator has already selected a bounded product-track
task and wants Codex to perform source/test/docs or docs-only work inside a
declared lockout.

Do not use this surface to authorize:

- Runtime/provider/model/platform execution.
- WSL, Ollama, OpenClaw, Hermes, LightRAG, Discord, installer, service, API,
  UI, dashboard, auth, deployment, scheduler, connector, or production work.
- `general_answer` resumption.
- Source Files refresh, capsule refresh, export/package refresh, or official
  capsule proof extension.
- Broad cleanup, unrelated refactors, or mutation outside the listed files.
- Semantic-correctness, autonomous-AI-coding, live-domain-execution, or
  production-readiness claims.

## Operator Prompt Template

Use the following structure for a Codex bounded-autonomy worker prompt:

```text
SESSION ROLE

You are a Codex bounded-autonomy worker for Roger's Orchestrator product track.
You are not CTO/coordinator/protocol keeper. The coordinator/operator owns
acceptance, proof interpretation, and next-boundary selection.

BOUNDARY

<PHASE_NUMBER_AND_BOUNDARY_NAME>

MODE

<read-only | docs-only | source/test/docs>

LOCKOUTS

- No runtime/provider/model/platform execution.
- No WSL/Ollama/OpenClaw/Hermes/LightRAG/Discord/installer execution.
- No service/API/UI/dashboard/auth/deployment work.
- No `general_answer` resumption.
- No Source Files refresh, capsule refresh, export/package refresh, or official
  capsule proof extension unless explicitly listed in this boundary.
- No semantic-correctness, autonomous-AI-coding, live-domain-execution, or
  production-readiness claims.
- No unrelated files.

ALLOWED FILES

- <path>
- <path>

TASK

<specific bounded deliverable>

ACCEPTED FACTS

- <facts already accepted by coordinator/operator>

NON-PROOFS TO PRESERVE

- <claims this phase must not make>

VALIDATION

- <command/search/check>
- <command/search/check>

REPORT FORMAT

Assessment:
Accepted Facts:
Changes Made:
Validation:
Non-Proofs Preserved:
Next Boundary:
RESPONSE_METADATA:
```

## Worker Rules

- Treat accepted facts as input constraints, not as permission to infer broader
  readiness.
- Mark inference separately from accepted facts.
- Keep mutation limited to the allowed files and boundary mode.
- Prefer small, reviewable edits that preserve existing document style.
- If a requested proof would require locked-out execution, stop at a report and
  name the missing proof boundary.
- If validation fails, report the exact command, exit state, and relevant output
  without expanding scope to repair unrelated failures.
- If local commit is authorized, commit only after validation and report the
  commit hash. Do not push unless the boundary explicitly authorizes push.

## Coordinator Intake Checklist

Before accepting a Codex bounded-autonomy report, the coordinator/operator
should verify:

- The reported changed files match the allowed-file list.
- The report separates accepted facts from inference.
- The phase marker is present only when the requested validation passed.
- Non-proofs remain explicit.
- No locked-out runtime/provider/model/platform, service/API/UI, capsule,
  `general_answer`, or unrelated work occurred.
- Any local commit remains local unless a separate push boundary was authorized.

## Non-Proofs

This surface is docs-only governance. It does not implement worker dispatch,
autonomous coding, provider/model routing, runtime execution, service/API/UI
behavior, dashboard/auth/deployment behavior, production readiness, semantic
correctness, or live domain execution.

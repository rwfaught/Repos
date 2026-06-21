# Capability Registry

## Purpose

The capability registry defines capability names, classes, proof status,
permission burden, validation burden, and stop conditions for route admission.
It is a documentation-level maturity model, not a source-code implementation
registry.

- Capability labels are not implementation proof.
- Capability labels are not execution authority.
- Capability labels are not provider/model/substrate selection.
- Capability labels are not production readiness.
- A route may require a capability even when the capability is unavailable or
  unproven.
- Admission must preserve the difference between requested capability,
  available capability, implemented capability, and authorized execution.

## Capability Classes

| Capability class | Meaning | Allowed route use at current maturity | Required confirmation burden | Validation burden | Stop conditions | Explicit non-proofs |
| --- | --- | --- | --- | --- | --- | --- |
| `direct_answer` | Answer-only response without mutation, scheduling, retrieval, connector use, or platform execution. | Docs/control constrained; not productized as a general assistant lane. | Low unless facts are stale, high-stakes, missing, or boundary-sensitive. | State basis and preserve caveats when needed. | Missing facts, high risk, retrieval/web need, connector need, mutation request, or scheduling request. | Not a general assistant product, provider route, persistence policy, or production lane. |
| `coding_task` | Bounded code or docs mutation through an explicit worker packet. | Allowed only under declared boundary, file scope, validation, and report format. | Explicit operator authorization through a bounded packet. | Worker evidence plus coordinator review; local PASS is not acceptance. | Ambiguous scope, undeclared files, conflicting evidence, or mutation beyond packet. | Not route execution, autonomous writeback, production readiness, or proof of adjacent capabilities. |
| `file_operation` | Read, write, move, delete, archive, or package local files. | Allowed only when explicitly authorized and scoped. | Proportional to breadth and destructiveness; deletion/archive requires explicit clarity. | Path, scope, and effect evidence. | Unsafe paths, broad scope, missing backup/approval, or hidden cleanup. | Not general filesystem authority, autonomous writeback, or export/upload proof. |
| `local_document_lookup` | Search or retrieve from declared local document sources. | Deferred/unimplemented in the product track except manual docs/read-only inspection under a boundary. | Confirm source set when ambiguous or sensitive. | Source-grounded answer with inspectable evidence paths once implemented. | Missing source authority, stale-source risk, or requested mutation/execution. | Not RAG implementation, index freshness, grounding verifier, or production lookup. |
| `web_research` | Use web sources to answer or verify externally changing facts. | Boundary-dependent; not an implemented product route. | Confirm when web use changes scope, privacy, or operator expectation. | Current source evidence and caveats. | No web authority, high-stakes uncertainty, connector/login need, or requested execution. | Not live router, provider selection, connector access, or production research service. |
| `reminder_scheduler` | Persist or schedule reminders and operator-facing automations. | Deferred/unimplemented in the product track. | Explicit confirmation for time, recurrence, target, notification, and persistence. | Confirm parsed time, persistence semantics, and update/cancel behavior once implemented. | Ambiguous time, missing confirmation, unsupported persistence, or non-reminder work. | Not scheduler implementation, durable reminder service, or production automation. |
| `connector_access` | Use an external connector, account, API, or integration surface. | Requires explicit connector boundary and authority. | Explicit operator authorization appropriate to data sensitivity and write risk. | Connector result evidence, source identity, and permission boundaries. | Missing connector authority, login/account ambiguity, write risk, or external policy conflict. | Not platform execution, provider/model selection, or blanket external access. |
| `platform_runtime` | Execute or inspect platform/runtime substrates such as external packages or local services. | External track unless an explicit crossing boundary authorizes it. | Explicit crossing-boundary authorization. | Fresh runtime/platform evidence; historical proof is not current truth. | Boundary lacks crossing authority, runtime proof is missing, or product/platform authority conflicts. | Not product route correctness, provider readiness, or production execution. |
| `provider_model` | Use or select model/provider surfaces. | External/platform or future provider-routing track; not route correctness proof. | Explicit authority for provider/model use and any data exposure. | Provider contract, output evidence, and non-proof caveats. | Provider unavailable, selection unsupported, data sensitivity, or model output used as proof. | Not route admission, implementation proof, or production readiness. |
| `artifact_export_package` | Export, package, hash, or upload artifacts. | Only when explicitly authorized; not implied by local docs PASS. | Explicit artifact/export/upload boundary. | Hash/path/upload evidence appropriate to the artifact. | Missing export authority, upload ambiguity, stale artifact, or package scope conflict. | Not source proof, upload acceptance, or production readiness by itself. |
| `production_execution` | Run production task behavior or claim production readiness. | Not proven. | Future explicit production boundary and acceptance criteria required. | Future production-grade evidence, not local PASS by implication. | Any missing production authority, tests, runtime proof, safety gate, or acceptance evidence. | Not implied by local source/test/docs/runtime/artifact proof. |
| `unsupported_or_blocked` | Capability is unavailable, contradictory, outside authority, or requires clarification. | Used to block, reject, defer, or ask clarification. | Clarification or explicit new boundary required. | Explain missing authority, proof, connector, scope, or capability. | Required capability unavailable, unproven, unsafe, or externally owned. | Not failure of the whole product and not permission to execute adjacent work. |

## Capability Maturity Status

- `named_only`: the capability has a stable name but no durable doctrine or
  implementation proof.
- `docs_control_defined`: documentation/control doctrine exists for using the
  capability label during route admission.
- `source_contract_defined`: source-level contract or data shape exists.
- `source_test_proven`: source contract has targeted local test proof.
- `local_runtime_proven`: local runtime behavior has fresh, bounded proof.
- `artifact_proven`: exported, packaged, uploaded, or hashed artifact proof
  exists for the stated artifact boundary.
- `production_ready`: explicit future production proof and acceptance exist.
- `blocked_or_external`: capability depends on an external track, missing
  connector, unavailable substrate, or unresolved authority.

Lower statuses must not be collapsed into higher statuses. `production_ready`
requires explicit future proof and is not implied by any prior local pass.

## Capability Registry Entry Shape

A documentation-level registry entry may use this shape:

- `capability_id`
- `display_name`
- `capability_class`
- `maturity_status`
- `authority_docs`
- `implementation_refs`
- `allowed_route_types`
- `permission_burden`
- `validation_burden`
- `stop_conditions`
- `non_proofs`
- `owner_context`
- `external_track_dependency`

This shape does not require implementation in code.

## Current Capability Posture

| Capability class | Present posture |
| --- | --- |
| `direct_answer` | Docs/control constrained; not productized as a general assistant lane. |
| `coding_task` | Bounded coding spine exists, but integrated production workflow remains unproven. |
| `file_operation` | Mutation requires explicit boundary and declared scope. |
| `local_document_lookup` | Deferred/unimplemented in the product track. |
| `web_research` | Deferred and boundary-dependent. |
| `reminder_scheduler` | Deferred/unimplemented. |
| `connector_access` | Requires explicit connector boundary. |
| `platform_runtime` | External track unless a crossing boundary authorizes it. |
| `provider_model` | External/platform or future provider-routing track; not route correctness proof. |
| `artifact_export_package` | Only when explicitly authorized; not implied by local docs PASS. |
| `production_execution` | Not proven. |
| `unsupported_or_blocked` | Used to clarify, reject, defer, or block without downstream execution. |

## Route Admission Use

Route admission may use the registry to:

- identify missing capability proof
- block unsafe admission
- require clarification
- require operator confirmation
- emit a worker packet
- defer to an external/platform track
- preserve non-proofs

Registry lookup is not execution.

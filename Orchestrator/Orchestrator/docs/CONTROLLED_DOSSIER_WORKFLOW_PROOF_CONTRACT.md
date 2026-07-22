# Controlled Dossier Workflow Proof Contract

Boundary: `ORCHESTRATOR_REPEATABLE_FICTIONAL_CONTROLLED_DOSSIER_WORKFLOW_SOURCE_TEST_PROOF`

## Purpose

`orchestrator.controlled_dossier_workflow` joins one caller-supplied fictional
case packet with existing case-packet persistence, `NeutralEvidenceLink`, and
the narrow evidence-linked synthesis transformation. It returns one
deterministic reviewable result rather than requiring reconstruction from
separate records.

## Input and flow

The workflow input has a `case_packet` and `analytical_records`. The packet
uses existing explicit `source_materials` and `extracted_facts` entries. Each
identified source entry transfers its caller-supplied value into
`source_inventory`; each identified fact entry transfers its value into
`statement_register`. The adapter supplies those existing entry IDs as the
corresponding synthesis identities and rejects mismatched IDs. It does not
classify, match, extract, score, select, or otherwise judge records.

The workflow saves and reloads the existing case packet, builds synthesis input
from the reloaded state, validates caller-supplied evidence links through the
existing synthesis contract, produces its recommendation package, validates an
explicit human disposition, and returns the final controlled workflow result.

The disposition must separately state accepted items, not-authorized items, and
separate future decisions. A recommendation is therefore not authorization.

## Result and blocked posture

Success uses `controlled_dossier_workflow_completed`. Its final structure
surfaces the original bounded case, reloaded source/fact identities, evidence
links, synthesis result, human disposition, non-proofs, and next bounded
action. Structural, persistence, adapter, synthesis, and disposition failures
return the deterministic `controlled_dossier_workflow_blocked` classification
with diagnostic errors. The coordinator does not repair records.

## Non-proofs

This is one fictional, deterministic source/test proof only. It does not
establish source truth or quality, evidentiary sufficiency, recommendation
correctness, authorization for excluded actions, provider/model/runtime
behavior, privacy or security compliance, real-client usefulness, Phase 5
provenance, product-wedge suitability, or production readiness.

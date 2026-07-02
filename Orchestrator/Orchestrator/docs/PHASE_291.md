# Phase 291 - Packet To Patch Bridge Negative Edge Contract

## Boundary

`PHASE291_PACKET_TO_PATCH_BRIDGE_NEGATIVE_EDGE_CONTRACT_SOURCE_TEST_DOCS`

## Purpose

Phase 291 hardens negative and edge-case coverage across the packet-result to
patch-proposal bridge created in Phases 288-290.

This phase adds focused tests and docs/ledger registration. It does not add
new source behavior because the existing bridge modules already block the
covered edge cases.

## Files Changed

- `tests/test_phase_291_packet_to_patch_bridge_negative_edge_contract.py`
- `docs/PHASE_291.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`

## Validation Commands

- `python -m py_compile tests\test_phase_291_packet_to_patch_bridge_negative_edge_contract.py`
- `python -m unittest tests.test_phase_291_packet_to_patch_bridge_negative_edge_contract`
- `python -m unittest tests.test_phase_288_packet_result_to_patch_proposal_eligibility_contract`
- `python -m unittest tests.test_phase_289_packet_result_patch_proposal_candidate_artifact`
- `python -m unittest tests.test_phase_290_patch_proposal_candidate_operator_promotion_gate`
- Relevant packet/current-success and patch-spine regressions listed in the
  worker validation report.
- `git diff --check`
- Search proof marker:
  `PHASE291_PACKET_TO_PATCH_BRIDGE_NEGATIVE_EDGE_CONTRACT_SOURCE_TEST_DOCS_PROVEN=PASS`
- Changed-file allowlist audit.

## Proof Marker

`PHASE291_PACKET_TO_PATCH_BRIDGE_NEGATIVE_EDGE_CONTRACT_SOURCE_TEST_DOCS_PROVEN=PASS`

## Proof Scope

Phase 291 proves deterministic negative-edge readback coverage for missing
accepted decisions, rejected decisions, deferred/rejected candidates, latest
rejected decisions, mismatched task/artifact/verifier evidence, missing
current-success/eligibility/candidate/promotion records, path traversal, POSIX
absolute paths, Windows absolute paths, Windows separators, provider/model/
runtime/platform smuggling, semantic correctness smuggling, production
readiness smuggling, apply-authorization smuggling, attempt-to-apply blocking,
generated residue reporting, no cleanup/deletion/archive behavior, no apply
invocation, exact reason codes, and non-proof preservation.

## Non-Proofs

Phase 291 does not prove semantic correctness, live provider/model execution,
runtime/platform behavior, autonomous AI coding, model-backed generation,
production readiness, service/API/UI/dashboard/auth/deployment behavior,
scheduler/reminder behavior, connector behavior, `general_answer` resumption,
platform/OpenClaw/Hermes/LightRAG behavior, cleanup/delete/archive authority,
patch proposal creation, patch apply authorization from packet acceptance,
patch apply authorization from candidate creation, patch apply authorization
from candidate promotion, patch application, or integrated production patch
workflow readiness.

## Caveats

- Phase 291 is negative-edge source/test/docs coverage; it does not add a new
  user-facing command.
- The bridge remains candidate/promotion evidence only, not a production patch
  workflow.
- Source ZIP uploads may include generated `__pycache__` or `.pyc` entries
  depending on operator packaging; product capsule proof should come from the
  official product capsule refresh output, not source upload hash alone.

## Generated Artifact / Residue Posture

Phase 291 tests generated residue in temporary directories and verifies it is
reported without cleanup, deletion, archive, or apply behavior.

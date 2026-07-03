# Phase 360 - Product Task Packet Domain-General Intake Contract Readback

Boundary: `PHASE360_PRODUCT_TASK_PACKET_DOMAIN_GENERAL_INTAKE_CONTRACT_READBACK_SOURCE_TEST_DOCS`

## Purpose

Adds a pure deterministic source/test/docs domain-general intake contract
readback for product task packets. This defines intake eligibility and stop
doctrine only; it does not implement domain-general intake or perform live
domain work.

## Changed Files

- `orchestrator/product_task_packet_domain_general_intake_contract_readback.py`
- `tests/test_phase_360_product_task_packet_domain_general_intake_contract_readback.py`
- `docs/PHASE_360.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`

## Accepted Facts

Prior source basis is Phase 349 through Phase 359 for the product task packet
track. Current verified `origin/main`: `8e33ab2c50ca8722cac4e8e3ca22a15d6ba904da`.
Phase 335 remains the only accepted official clean capsule proof unless
explicitly superseded.

## Implementation Summary

Adds static intake input doctrine, intake output doctrine, intake stop gates,
invalid claims, stop conditions, false activity flags, report caveats, and
source/capsule/Git truth separation.

## Validation Checklist

- `python -m py_compile orchestrator/product_task_packet_domain_general_intake_contract_readback.py`
- `python -m unittest tests.test_phase_360_product_task_packet_domain_general_intake_contract_readback`
- marker search
- non-proof search
- `git diff --check`
- changed-file allowlist audit

## Marker

`PHASE360_PRODUCT_TASK_PACKET_DOMAIN_GENERAL_INTAKE_CONTRACT_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS`

## Recommended Next Boundary

`PHASE361_PRODUCT_TASK_PACKET_HANDOFF_CONTRACT_READBACK_SOURCE_TEST_DOCS`

## Non-Proofs

No runtime/provider/model/platform execution. No service/API/UI/dashboard/auth/deployment.
No general_answer. No Source Files refresh. No capsule/export/package refresh.
No domain-general intake implementation beyond static readback doctrine, no live
business-data access, no live Obsidian/PKMS access, no real domain execution,
no production task execution, no semantic correctness, no production readiness,
no autonomous AI coding, and no official capsule proof beyond Phase 335.

## Contract Doctrine

Readback is not execution. Eligibility is not implementation. Contract is not
runtime enforcement. Worker PASS is evidence, not coordinator ratification.
Test PASS is not semantic correctness. Pushed commit is not production readiness.
Git repo truth is distinct from Source Files handoff snapshots.

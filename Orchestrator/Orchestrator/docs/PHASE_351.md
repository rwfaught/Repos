# Phase 351 - Product Task Packet Negative-Edge Contract

Boundary:

`PHASE351_PRODUCT_TASK_PACKET_NEGATIVE_EDGE_CONTRACT_SOURCE_TEST_DOCS`

## Purpose

Phase 351 adds a narrow deterministic source/test/docs negative-edge contract
for product task packets, grounded in the Phase 349 operator report surface.

The contract makes explicit what product task packets must not claim, trigger,
imply, or authorize. It hardens the Phase 349 report surface without creating
product tasks, dispatching workers, applying patches, executing providers or
models, resuming `general_answer`, or crossing into service/API/UI/dashboard/
auth/deployment work.

## Changed Files

- `orchestrator/product_task_packet_negative_edge.py`
- `tests/test_phase_351_product_task_packet_negative_edge_contract.py`
- `docs/PHASE_351.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`

## Accepted Facts

- Phase 349 completed the deterministic source/test/docs product task packet
  operator report surface.
- Phase 349 marker:
  `PHASE349_PRODUCT_TASK_PACKET_OPERATOR_REPORT_SURFACE_SOURCE_TEST_DOCS_PROVEN=PASS`
- Current accepted `origin/main` at the start of this phase:
  `5b9767285c70b1009c980ca9fbe00b8b5cb2d064`
- Phase 335 remains the only accepted official clean capsule proof unless a
  later explicit boundary refreshes capsule/export/package proof.

## Implementation Summary

Phase 351 adds `read_product_task_packet_negative_edge_contract()` as a pure
deterministic source readback. It returns static data only and does not read
files, invoke Git, run subprocesses, access environment variables, call
networks, execute providers/models/adapters, create CLI behavior, create
service/API/UI/dashboard behavior, import or resume `general_answer`, execute
Codex or any worker agent, dispatch workers, apply patches, mutate files,
validate live tasks, or parse live packets.

The contract records disallowed packet claims, disallowed packet actions,
required stop conditions, required false flags, required report caveats,
source/capsule/Git truth separation, and next-safe-seam doctrine. It is not a
validator, parser, dispatcher, CLI, service, runner, live task harness, or live
enforcement mechanism.

## Validation Checklist

- `git status --short --branch`
- `python -m py_compile orchestrator/product_task_packet_negative_edge.py`
- `python -m unittest tests.test_phase_351_product_task_packet_negative_edge_contract`
- Marker search for
  `PHASE351_PRODUCT_TASK_PACKET_NEGATIVE_EDGE_CONTRACT_SOURCE_TEST_DOCS_PROVEN=PASS`
- Non-proof and lockout text search in source, test, and phase doc
- `git diff --check`
- changed-file allowlist audit
- `git status --short --branch`

## Marker

`PHASE351_PRODUCT_TASK_PACKET_NEGATIVE_EDGE_CONTRACT_SOURCE_TEST_DOCS_PROVEN=PASS`

## Non-Proofs

- No runtime/provider/model/platform execution occurred.
- No service/API/UI/dashboard/auth/deployment work occurred.
- No WSL, Ollama, OpenClaw, Hermes, LightRAG, Discord, installer, service,
  API, UI, dashboard, auth, deployment, scheduler, connector, or production
  behavior occurred.
- No general_answer work occurred.
- No `general_answer` work occurred.
- No capsule/export/package refresh occurred.
- No Source Files refresh, capsule refresh, export/package refresh, or official
  capsule proof extension occurred.
- No worker dispatch occurred.
- No Codex execution or worker dispatch occurred.
- No relay execution occurred.
- No patch application occurred.
- No live task execution occurred.
- No task creation or task mutation occurred.
- No parser, runner, dispatcher, CLI, service, API, UI, or live harness
  behavior occurred.
- No push occurred in this phase unless a later coordinator/operator boundary
  does it.
- No production-readiness claim is made.
- No semantic-correctness claim is made.
- No autonomous AI coding authority is implied.
- No live provider/model claim is implied.
- No live Obsidian/PKMS/business-data claim is implied.
- No live mutation, adapter execution, or real domain execution is implied.

## Source/Capsule/Git Truth Separation Caveat

Git repo truth remains separate from Source Files handoff snapshots, official
clean product capsule proofs, and full Git repo backups including `.git`.
Phase 351 adds a source/test/docs negative-edge contract only and does not
refresh or supersede the Phase 335 official clean capsule proof.

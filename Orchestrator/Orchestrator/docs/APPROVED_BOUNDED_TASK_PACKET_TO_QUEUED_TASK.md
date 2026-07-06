# Approved Bounded Task Packet To Queued Task

Boundary: `APPROVED_BOUNDED_TASK_PACKET_TO_QUEUED_TASK_SOURCE_TEST_DOCS`

## Purpose

This seam adds the next piece of the small Orchestrator MVP loop: after a bounded task packet is ready for Roger approval, explicit Roger approval can create one queued task record.

This is task creation only. It does not execute the task, dispatch a worker, invoke a model, mutate project files, or claim production readiness.

## What Went In

The seam consumes:

- a review-gate result from `orchestrator/bounded_task_packet_review_gate.py`,
- an explicit Roger approval record,
- a caller-supplied task store directory.

The caller-supplied directory is required so tests and future interfaces can prove persistence without silently writing into the live repo task store.

## What Orchestrator Does

`orchestrator/approved_bounded_task_packet_to_queued_task.py` checks:

- the review gate decision is `ready_for_roger_approval`,
- Roger's decision is `approve_next_boundary`,
- `roger_approved` is true,
- an approval note is present,
- a task store directory is explicitly supplied,
- the target queued task record does not already exist.

If those checks pass, it writes one JSON task record with:

- `status: queued`,
- `role: worker`,
- `execution_policy: report_only`,
- `execution_delegation_status: queued_waiting_for_explicit_execution_boundary`,
- `requires_causal_change: false`,
- no execution artifact.

## What Roger Can Judge

Roger can inspect whether:

- the approved task record still matches the bounded task packet,
- the task is queued rather than executed,
- the file/scope surface is explicit,
- the approval note is preserved,
- the next step still requires a separate execution authorization review.

## What Is Proven

This proves only deterministic source/test/docs behavior:

- explicit approval can be required before task creation,
- a ready review gate can become one queued task JSON record,
- missing approval blocks the write,
- missing task store directory blocks the write,
- clarification-needed packets do not become tasks,
- duplicate task records are not overwritten,
- execution flags remain false.

## What Is Not Proven

This does not prove:

- runtime/provider/model execution,
- live coordinator reasoning,
- autonomous task dispatch,
- worker execution,
- local model capability,
- frontier model escalation,
- semantic correctness,
- production readiness,
- file mutation execution,
- Phase 387 implementation,
- first product wedge selection.

## Current MVP Loop Shape

The project now has a deterministic spine:

1. Broad operator goal is preserved and structured.
2. Missing inputs and risk flags are surfaced.
3. Orchestrator asks clarification questions or emits one bounded task packet.
4. The bounded task packet is reviewed for Roger approval readiness.
5. Explicit Roger approval can create one queued task record in a caller-supplied task store.
6. The queued task can be reviewed for future execution-authorization readiness.
7. Execution remains locked until a future explicit execution authorization boundary.

## Recommended Next Boundary

`QUEUED_TASK_EXECUTION_AUTHORIZATION_REVIEW_SOURCE_TEST_DOCS`

The next review should inspect whether the queued task record is sufficient to support a future execution authorization boundary without smuggling in runtime, provider/model, mutation, or product-wedge claims.

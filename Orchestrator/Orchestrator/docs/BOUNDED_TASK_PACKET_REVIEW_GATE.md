# Bounded Task Packet Review Gate

Boundary: `BOUNDED_TASK_PACKET_REVIEW_GATE_SOURCE_TEST_DOCS`

## Purpose

This seam adds the next piece of the small Orchestrator MVP loop.

The prior slice can turn a broad operator goal into either clarification questions or one reviewable bounded task packet. This gate reviews that packet before any execution-like step. It answers:

- is the packet ready for Roger approval,
- does the packet need repair,
- or is the goal still blocked because clarification is required?

It does not dispatch a worker. It does not execute a model. It does not mutate files.

## What Went In

The gate consumes the deterministic output from `orchestrator/goal_intake_to_bounded_task_packet.py`.

For the dogwalking app example, the source packet includes one proposed bounded planning packet.

For the PKMS reorganization example, the source packet has no task packet because the request needs clarification around path, schema, backup/dry-run posture, and mutation scope.

## What Orchestrator Does

`orchestrator/bounded_task_packet_review_gate.py` checks whether the proposed bounded task packet includes:

- packet id,
- title,
- purpose,
- preserved operator goal,
- file/scope surface,
- allowed operations,
- excluded operations,
- success criteria,
- explicit operator approval requirement,
- dispatch authorization remaining false.

If those checks pass, the gate returns `ready_for_roger_approval`. That means Roger can review the packet. It does not mean execution is authorized.

If required fields are missing, the gate returns `needs_packet_repair`.

If the source intake still needs clarification, the gate returns `blocked_for_operator_clarification`.

## Roger Approval Surface

The gate exposes the next human decision as a small set of allowed answers:

- `approve_next_boundary`
- `request_packet_repair`
- `answer_clarification_questions`
- `stop_or_reframe_goal`

This is the practical control point between planning and doing.

## What Is Proven

This proves only deterministic source/test/docs behavior:

- a proposed bounded task packet can be structurally reviewed,
- clarification-needed intake remains blocked,
- missing packet fields trigger repair,
- dispatch authority cannot be smuggled into the packet,
- missing file/scope surface triggers repair,
- Roger approval remains required before dispatch,
- false execution flags remain false,
- non-proofs remain visible.

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
- file mutation safety,
- Phase 387 implementation,
- first product wedge selection.

## Current MVP Loop Shape

The project now has a small deterministic spine:

1. Broad operator goal is preserved and structured.
2. Missing inputs and risk flags are surfaced.
3. Orchestrator either asks clarification questions or emits one bounded task packet.
4. The bounded task packet is reviewed for Roger approval readiness.
5. Explicit Roger approval can create one queued task record.
6. Execution remains locked until a future explicit authorization boundary.

## Recommended Next Boundary

`BOUNDED_TASK_PACKET_REVIEW_GATE_REVIEW_READONLY`

The next review should decide whether this gate is the right approval checkpoint before adding task persistence or any live worker execution path.

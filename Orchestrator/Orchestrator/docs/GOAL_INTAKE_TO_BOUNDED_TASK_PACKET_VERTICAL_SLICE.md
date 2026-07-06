# Goal Intake To Bounded Task Packet Vertical Slice

Boundary: `GOAL_INTAKE_TO_BOUNDED_TASK_PACKET_VERTICAL_SLICE_SOURCE_TEST_DOCS`

## Purpose

This slice records the smallest honest version of Roger's intended Orchestrator loop:

- Roger gives a broad goal.
- Orchestrator preserves the goal as input.
- Orchestrator identifies missing information and risk.
- Orchestrator chooses a non-executing route posture.
- Orchestrator either asks clarifying questions or produces one reviewable bounded task packet.
- Roger remains the approval point before mutation, dispatch, provider/model use, or production work.

This is not yet the full autonomous coordinator. It is a deterministic source/test/docs proof that the repo can represent the product loop in a Roger-legible way.

## What Went In

The source seam includes two deterministic example requests:

- A simple local dogwalking gig-work app idea.
- A PKMS/front matter reorganization request that would involve broad local document inspection and possible bulk mutation.

The dogwalking example is intentionally simple. Its purpose is to prove the loop shape, not to select a real product wedge.

## What Orchestrator Does

`orchestrator/goal_intake_to_bounded_task_packet.py` builds a plain dictionary with:

- the preserved operator goal,
- known context,
- missing inputs,
- risk flags,
- intake status,
- clarification questions,
- local-first and frontier-escalation posture,
- a next bounded task packet when the request is safe enough to reduce,
- explicit non-proofs and false activity flags.

The PKMS example stops at clarification because the request lacks path, schema, backup/dry-run posture, and mutation authority.

## What Came Out

For the dogwalking example, the seam produces a reviewable first task packet:

- draft a compact product brief,
- identify user roles,
- name the smallest useful workflow,
- list missing decisions,
- preserve an explicit no-mutation file/scope surface,
- recommend a next implementation boundary for Roger review.

The packet does not authorize dispatch. It does not write app code. It does not select a product wedge.

For the PKMS example, the seam produces clarification questions and no task packet.

## What Roger Can Judge

Roger can inspect whether:

- the original goal was preserved,
- the missing inputs are practical and real,
- the proposed first task is small enough,
- local-first routing makes sense for the first bounded task,
- frontier coordinator review should be authorized later,
- risky or underspecified work stops before mutation.

## What Is Proven

This proves only deterministic source/test/docs behavior:

- a broad goal can be represented as structured intake,
- the code can stop for clarification,
- the code can produce a bounded first task packet when enough information exists,
- route posture can distinguish local-first worker posture from later frontier escalation posture,
- false flags remain false,
- non-proofs remain visible.

## What Is Not Proven

This does not prove:

- runtime/provider/model execution,
- live coordinator reasoning,
- autonomous task dispatch,
- local model capability,
- frontier model escalation,
- semantic correctness,
- production readiness,
- file mutation safety,
- Phase 387 implementation,
- first product wedge selection.

## Recommended Next Boundary

`GOAL_INTAKE_TO_BOUNDED_TASK_PACKET_VERTICAL_SLICE_REVIEW_READONLY`

The next review should judge whether this is the correct minimal spine for the real Orchestrator MVP before adding runtime model calls or worker dispatch.

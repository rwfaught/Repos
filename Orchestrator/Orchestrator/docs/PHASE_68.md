# PHASE_68.md

## Title

Authorized Case-Packet Persistence Write Gate

## Purpose

Phase 68 defines the product-side persistence write gate after Phase 67 operator authorization.

Phase 65 admits a proceed handoff.

Phase 66 reviews the case-packet seed candidate.

Phase 67 records explicit operator authorization for a later persistence boundary.

Phase 68 defines the boundary where that authorization may become a persisted case packet.

This phase is the line between authorization and durable state.

## Problem Statement

Authorization is not persistence.

Phase 67 can say a reviewed seed is authorized for a later case-packet persistence boundary, but that still does not mean a case packet has been written.

Without a separate persistence write gate, the product could blur these distinct states:

- reviewed seed
- operator authorization
- persisted case packet
- task creation
- planner routing
- execution

That blur would turn consent into a conveyor belt.

Phase 68 exists to prevent that.

## Phase Boundary

This phase defines persistence semantics only.

This definition boundary does not itself create a case packet.

A later implementation boundary may add a deterministic persistence command if explicitly authorized.

This phase does not authorize:

- task creation
- planner output
- execution runs
- verifier runs
- reviewer runs
- runtime calls
- model calls
- platform integration
- OpenClaw integration
- bridge behavior
- adapter behavior

## Intended Behavior

A future implementation of this phase should accept a Phase 67 creation authorization result and classify whether a case packet may be persisted.

A persistence implementation should require:

- Phase 67 authorization result
- `creation_authorization=creation_authorized`
- `case_packet_creation_authorized=true`
- `case_packet_created=false`
- `case_packet_persisted=false`
- `task_created=false`
- `planner_invoked=false`
- `mutation_performed=false`
- `execution_performed=false`
- seed summary with objective text
- seed summary with provided artifacts
- seed summary with source intake linkage
- seed summary with candidate-only status
- seed summary with non-created creation status
- explicit operator persistence authorization for this boundary

The persistence result should preserve a clear artifact identity for the new case packet if persistence occurs.

## Persistence Requirements

A case packet may only be persisted if all of the following are true:

1. The input derives from a Phase 67 creation authorization result.

2. The Phase 67 result is `creation_authorized`.

3. The result confirms no prior persistence or mutation occurred.

4. The seed summary is complete enough to create a minimal case packet.

5. The operator explicitly authorizes persistence in this boundary.

6. The write target is the product case-packet store only.

7. The output records:

   - case packet id
   - case packet path
   - source intake linkage
   - Phase 65 admission status if available
   - Phase 66 seed-review summary
   - Phase 67 authorization summary
   - objective text
   - provided artifacts
   - created timestamp
   - persistence status

8. No task, planner output, runtime execution, model execution, or platform behavior is created as part of the persistence write.

## Needs-Decision Conditions

The persistence gate should classify the result as `needs_operator_decision` if:

- Phase 67 authorization is valid but no explicit persistence decision is provided
- the operator decision is ambiguous
- the operator asks to inspect the case packet preview before persistence
- the case-packet id or naming policy needs clarification
- the operator requests a different persistence boundary

## Blocked Conditions

The persistence gate should classify the result as `blocked` if:

- the Phase 67 authorization result is not `creation_authorized`
- the input implies a case packet already exists
- the input implies task creation
- the input implies planner invocation
- the input implies runtime/model/platform execution
- the seed summary lacks objective text
- the seed summary lacks source intake linkage
- the persistence target is outside the product case-packet store
- the operator request tries to bundle persistence with planner/task/runtime/model/platform behavior
- the operator request expands into OpenClaw, bridge, adapter, installer, WSL, Discord, A18CF, vendoring, cleanup, delete, archive, or Codex behavior

## Operator Control Principle

Phase 68 is the first phase in this intake chain that may eventually write durable case-packet state.

That power must remain narrow.

Persistence should mean:

"Create the case packet record only."

It must not mean:

- create tasks
- invoke a planner
- execute anything
- call models
- call platform integrations
- start OpenClaw/Discord/bridge/adapter behavior

The case packet is a ledger entry, not a launch button.

## Expected Implementation Surface

A later implementation boundary may add one or more of:

- a pure validation function for Phase 67 authorization persistence readiness
- a deterministic case-packet persistence function
- a read-only preview mode before persistence
- a CLI command that persists only if explicitly bounded
- regression tests proving the write is narrow
- regression tests proving no task, planner, runtime, model, platform, OpenClaw, Discord, bridge, adapter, installer, or WSL behavior occurs

That later implementation boundary must identify exact target files before mutation.

## Acceptance Criteria

A successful implementation of this phase should prove:

1. A valid Phase 67 creation authorization plus explicit persistence approval can persist one case packet.
2. The persisted case packet includes objective text, provided artifacts, source intake linkage, and prior gate summaries.
3. The persistence result includes case packet id and path.
4. A valid Phase 67 authorization without explicit persistence approval is classified as `needs_operator_decision`.
5. A non-authorized Phase 67 result is classified as `blocked`.
6. Any input implying prior case-packet creation or persistence is classified as `blocked`.
7. Any input implying task creation or planner invocation is classified as `blocked`.
8. Any input implying runtime, model, platform, Discord, OpenClaw, bridge, adapter, installer, or WSL behavior is classified as `blocked`.
9. The persistence path is confined to the product case-packet store.
10. The persistence write does not create tasks.
11. The persistence write does not invoke planner behavior.
12. The persistence write does not execute runtime or model behavior.
13. The persistence write is deterministic and operator-legible.

## Boundary Discipline

This phase does not authorize:

- task creation
- planner output
- platform repo mutation
- installer execution
- WSL execution
- model pull
- model run
- Discord execution
- OpenClaw integration
- bridge execution
- adapter execution
- A18CF
- vendoring
- cleanup/delete/archive
- Codex

## Expected Next Boundary

After this phase is defined and ratified, the next likely boundary is product implementation of the authorized case-packet persistence write gate.

That implementation boundary must decide whether to implement preview-only first or allow a narrowly scoped persistence command.

If persistence is allowed, it must be explicitly bounded to one case-packet write and must include proof that no task, planner, runtime, model, or platform behavior was created.

## Implementation Status

Phase 68 implementation target:

- deterministic authorized case-packet persistence function
- CLI command: `case-packet-persist-authorized`
- persisted / needs_operator_decision / blocked outcomes
- explicit operator persistence authorization requirement
- one-case-packet-only write semantics
- persisted packet includes objective text, provided artifacts, source intake linkage, Phase 66 seed-review summary, and Phase 67 authorization summary
- regression tests proving no task, planner, runtime, model, platform, Discord, OpenClaw, bridge, adapter, installer, or WSL behavior is created
- regression tests keep persistence writes confined to a temporary patched case-packet store during test execution

Implementation marker:

PHASE_68_IMPLEMENTED_AUTHORIZED_CASE_PACKET_PERSISTENCE_WRITE_GATE
## Implementation Repair Note

Initial Phase 68 implementation output was not ratified because the native unittest gate failed in 	est_h_existing_case_packet_is_not_overwritten.

The repair boundary preserved the test expectation and patched the blocked-persistence helper so blocked existing-case results can carry the attempted case-packet path without raising TypeError.

Repair marker:

PHASE_68_REPAIRED_BLOCKED_PATH_ARGUMENT_AND_NATIVE_TEST_GUARD
## Upload Verification and Ledger Closure

The repaired Phase 68 product artifact was uploaded and coordinator-inspected after the native PowerShell repair boundary.

Verified repaired implementation artifact:

- SHA256: de86e8d51da286733c6b8507ab347d8dd240d0cf095a321232718254819cd4f7
- Size: 658,084 bytes
- Entry count: 640

Verification result:

- `_blocked_persistence()` accepts `path: str = ""`.
- `_blocked_persistence()` forwards `path=path` to `_persistence_result()`.
- The existing-case blocked branch still passes `path=str(path)`.
- Generated workspace JSON count: 0.
- Test-log payload count: 0.
- pyc / pyo / `__pycache__` count: 0.
- Host metadata count: 0.
- Fixture JSON preserved count: 321.

Phase 68 is closed as implemented, locally tested after repair, exported, and uploaded verified.

PHASE_68_UPLOAD_VERIFIED_AND_LEDGER_CLOSED

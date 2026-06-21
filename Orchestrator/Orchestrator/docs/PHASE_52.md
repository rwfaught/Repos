# PHASE_52.md

## Phase 52: Core Orchestration Service Layer Beneath CLI

---

## Goal

Create a narrow service layer beneath the CLI so canonical orchestration operations can be called directly from Python without going through command-line parsing.

This phase is not about adding an API server.

It is about preventing the CLI from becoming the accidental internal API.

The system should gain a stable, importable orchestration service surface that:

- preserves existing behavior
- keeps command parsing in `main.py`
- moves core engine-facing operations below the CLI boundary
- allows future machine-facing interfaces to call the same core logic as the CLI

---

## Why This Phase Exists

The system is now mature enough that other software may eventually want to use it as an engine.

If that future arrives before the engine boundary is defined, two bad outcomes become likely:

1. the CLI becomes the de facto internal API
2. a future HTTP or RPC layer reimplements or shells into CLI behavior

Both would create a second control system.

This phase hardens the correct architecture early:

- orchestration semantics live in a service layer
- CLI remains a thin adapter
- future API surfaces can call the same canonical operations

---

## This Phase Is About

This phase is about extracting stable engine operations beneath the CLI.

It should create a service module that exposes a small set of Python-callable functions for existing orchestration behavior.

The first extraction surface should be limited to already-stable core operations such as:

- workspace initialization
- status inspection
- run creation
- next-task processing

Recommendation operations are explicitly deferred in this phase unless implementation reveals one or two truly trivial read-only seams that can be included without broadening the boundary. Default stance: defer them.

The extraction must preserve current CLI behavior.

---

## This Phase Is NOT About

This phase is NOT about:

- adding FastAPI, Flask, or any HTTP server
- adding sockets, RPC, or daemon behavior
- adding authentication or permissions
- adding concurrency control or locking redesign
- adding background workers
- redesigning task/run semantics
- broadly modularizing all CLI command families
- shelling out from one interface into another
- changing recommendation policy or workflow meaning
- turning this into a general service-framework refactor

This phase defines the engine boundary only.

Transport comes later.

---

## Files to Create

- `orchestrator/service.py`

---

## Files to Modify

- `main.py`
- `docs/ACTION_LOG.md`

Optional only if strictly necessary:

- existing orchestrator modules that must be touched to keep the service seam clean and minimal

Do not modify `orchestrator/recommendation_cli.py` unless doing so is strictly necessary to avoid duplication or keep imports coherent.

---

## Core Requirement

The system must gain a small importable service module whose functions perform canonical orchestration actions directly.

These service functions must call the existing orchestration logic rather than duplicating it.

The CLI must then delegate to those service functions.

The result should be:

- one control system
- two surfaces:
  - CLI surface
  - direct Python-callable service surface

---

## Service Layer Requirements

The new service module should expose explicit functions for stable core operations.

Minimum target operations:

### 1. `initialize_workspace_service()`

Purpose:
- perform workspace initialization

Behavior:
- call the same underlying initialization path used by the CLI
- return a structured result instead of only printing

Suggested result shape:
- `status`
- `message`

---

### 2. `get_status_service()`

Purpose:
- provide current system status

Behavior:
- return the same underlying information currently surfaced by the CLI status path
- do not require command-line parsing

Suggested result shape:
- `status`
- `message`
- optional small structured metadata if already naturally available

---

### 3. `create_run_service(request_text: str | None = None)`

Purpose:
- create a run directly from Python without CLI mediation

Behavior:
- perform the same run creation behavior as the current CLI path
- preserve existing defaults if request text is omitted

Suggested result shape:
- `status`
- `message`
- `run_id`
- `run_data`

---

### 4. `process_next_task_service(provider_name: str = "mock")`

Purpose:
- execute the next task through the existing engine path

Behavior:
- call the same bounded task-processing logic currently used by the CLI
- preserve provider selection semantics
- preserve final status behavior

Suggested result shape:
- `status`
- `message`
- `task_id`
- `artifact_id`
- `final_task_status`
- `provider`
- `execution_status`
- `verification_status`
- optional recommendation/reviewer ids only if already naturally available from existing behavior

Do NOT invent new semantic layers here.

---

## Recommendation Surface Rule

Recommendation read and mutation operations are not part of the intended extraction target for this phase.

Reason:
- they are currently more control-surface-shaped than engine-spine-shaped
- forcing them into Phase 52 would risk broadening the seam
- the primary objective here is to canonicalize the core orchestration spine first

Exception:
- if implementation reveals a trivially bounded read-only helper that clearly belongs below the CLI and can be included without widening the phase, it may be included
- mutation operations should remain deferred

Default outcome:
- recommendation operations remain outside the Phase 52 service boundary

---

## Result Shape Rules

Service functions must return structured Python dictionaries rather than relying on print-only behavior.

These results should be:

- small
- explicit
- deterministic
- machine-consumable
- consistent with existing system semantics

Do NOT introduce a large response framework.

Do NOT add Pydantic, Marshmallow, dataclass-based response hierarchies, or schema systems.

Keep result shapes simple dicts.

---

## CLI Integration Rules

`main.py` must remain the CLI entrypoint.

It must continue to own:

- command names
- argument parsing
- user-facing command dispatch

But after parsing, `main.py` should delegate relevant core operations to `orchestrator/service.py`.

The CLI should become thinner, not different.

Command semantics must remain unchanged.

---

## Design Rules

This phase must preserve the following architectural rules:

### 1. No second control system

The service layer must not become a parallel implementation of CLI behavior.

It must be the canonical execution surface beneath the CLI.

---

### 2. No transport leakage

Do not shape the service layer around HTTP concepts.

Avoid:
- route naming
- request/response objects
- status codes
- auth hooks
- server lifecycle concerns

This is an engine layer, not a web layer.

---

### 3. No semantic drift

Do not change:

- provider defaults
- status meanings
- run selection behavior
- task-processing rules
- recommendation meanings

This is extraction, not redesign.

---

### 4. Minimal seam only

Only extract operations that are already coherent enough to be canonical.

Do not use this phase to refactor unrelated command families.

---

## Validation Requirements

This phase must be validated with bounded checks showing that CLI behavior remains intact while service functions are usable directly.

Required validation:

### Test A: Compile validation

Run:

`python3 -m py_compile main.py orchestrator/service.py`

Expected:
- passes cleanly

---

### Test B: Existing CLI regression surface

Run the smallest existing regression set that proves core CLI behavior remains unchanged for:

- init
- status
- run creation
- next-task processing

Use existing tests if present.

If no direct tests exist for one of these surfaces, add only the minimum validation necessary to prove behavior preservation.

Do NOT broaden test infrastructure.

---

### Test C: Direct service call validation

Add or run bounded tests showing service functions can be called directly from Python and return structured results for:

- workspace initialization
- status
- run creation
- next-task processing

Expected:
- no CLI parsing required
- structured dict output returned
- semantics match current CLI behavior

---

### Test D: Provider passthrough preservation

Validate that service-layer task processing preserves explicit provider selection behavior.

Expected:
- `provider_name="mock"` works
- unsupported provider behavior remains controlled and unchanged

---

## Success Criteria

This phase is successful when:

- `orchestrator/service.py` exists
- core orchestration operations can be called directly from Python
- `main.py` delegates those operations through the service layer
- CLI behavior remains unchanged
- no transport/server concerns are introduced
- no second control system appears
- validation confirms preserved behavior and direct service usability
- recommendation operations are either deferred or included only in an obviously trivial read-only way without broadening the seam

---

## Implementation Notes

The safest implementation style is:

- thin service wrappers over existing orchestrator logic
- small structured return dicts
- CLI functions call service functions, then print existing user-facing output

Prefer reusing existing helpers and execution paths wherever possible.

Do NOT duplicate engine logic just to make the service module look “clean.”

A small truthful seam is better than a broad decorative abstraction.

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was implemented
   - which files were created or modified

2. Report:
   - which operations are now canonical service functions
   - how `main.py` delegates to the service layer
   - what validation was performed
   - whether recommendation operations were fully deferred or whether any trivial read-only seam was included

3. Append a concise entry to:
   - `docs/ACTION_LOG.md`

4. Do NOT proceed further

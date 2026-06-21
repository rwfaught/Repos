# PHASE_64.md

## Phase 64 — Intake Proceed Handoff Object

Status: Implemented / locally verified.

## Purpose

Define and implement the smallest product-side handoff seam between intake judgment and bounded internal casework.

Phase 57 exposed intake judgment through a local control surface.

Phases 58 through 62 created and made legible a minimal local case-packet substrate.

The remaining gap is the seam between those two surfaces:

when intake returns `proceed`, what exactly is handed off next?

This phase exists to make that seam explicit, inspectable, deterministic, and bounded.

## Required Outcome

After this phase, a `proceed` intake result must include a minimal `decomposition_handoff` object.

The handoff object must be operator-legible and must preserve enough information for later bounded casework without silently creating tasks, case packets, or decomposition plans.

The handoff object is authorization context only.

It is not decomposition.

It is not a task.

It is not a case packet.

It is not execution.

## Required Handoff Shape

For a `proceed` result, the output should include a `decomposition_handoff` object with fields equivalent to:

- `objective_text`
- `provided_artifacts`
- `confirmed_context`
- `handoff_status`
- `authorized_next_action`
- `operator_decision_required`
- `case_packet_seed_candidate`

The exact field names may be adjusted during implementation, but the shape must preserve these meanings.

## Required Semantics

For `proceed` outcomes:

- `outcome` remains `proceed`
- `decomposition_permitted` remains `true`
- `next_action` remains `begin_decomposition`
- `decomposition_handoff` must be present
- the handoff must be deterministic from the intake input
- the handoff must be inspectable in the CLI output
- the handoff must not mutate case-packet storage
- the handoff must not create orchestrator tasks
- the handoff must not run a planner
- the handoff must not perform decomposition

For `clarify` and `blocked` outcomes:

- `decomposition_handoff` must not authorize decomposition
- no case-packet seed candidate should be treated as ready
- the operator must still be able to understand what is missing or blocked

## Non-Goals

This phase must not implement:

- planner-generated decomposition
- automatic task creation
- automatic case-packet creation
- runtime execution
- model execution
- installer work
- WSL work
- Discord work
- OpenClaw integration
- bridge or adapter execution
- platform package mutation
- vendoring

## Platform / Installer Track Note

The installer exists and remains a real platform asset.

However, installer/model/runtime concerns are deferred from this product phase.

Known future platform concerns include:

- avoiding repeated model downloads during installer validation
- deciding when a reusable model cache is acceptable
- distinguishing smoke-test models from practical local default models
- avoiding unnecessary fresh-distro churn
- preserving reproducibility while preventing installer tests from becoming slow and wasteful

Those concerns require a separate platform strategy boundary.

They must not be solved inside Phase 64.

## Model Strategy Note

Tiny models may be acceptable for installer smoke tests or proof-of-command-path checks.

Tiny models should not be treated as proof of Discord-quality or real assistant behavior.

A practical local model tier may need to be around the 7B class for meaningful platform behavior checks.

Exact model choice is not decided in this phase.

No model pull, model run, runtime probe, WSL run, installer run, Discord test, bridge execution, adapter execution, or A18CF work is authorized by this document.

## Implementation Surface

Expected candidate files for the later implementation boundary:

- `orchestrator/intake.py`
- `main.py`
- `tests/test_phase_64_intake_handoff.py`

Implementation should be small and deterministic.

## Acceptance Criteria

A later implementation boundary should prove:

1. `intake-judge` with a valid proceed input emits `decomposition_handoff`.
2. The handoff includes the original objective text.
3. The handoff includes provided artifacts.
4. The handoff includes confirmed context.
5. The handoff contains a bounded case-packet seed candidate or equivalent operator-inspectable seed context.
6. The handoff does not create a case packet file.
7. The handoff does not create tasks.
8. Clarify and blocked outcomes do not authorize decomposition through the handoff.
9. Existing Phase 57 through Phase 62 tests remain valid.
10. The result remains operator-legible and deterministic.

## Boundary Discipline

This phase is product-side only.

It does not authorize:

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
- `oz`
- Codex

## Expected Next Boundary

After this phase is defined and ratified, the next likely boundary is an implementation boundary for the minimal `decomposition_handoff` object.

If platform testing concerns become urgent, create a separate platform strategy boundary instead of mixing them into the product phase.

## Implementation Result

Phase 64 is implemented locally.

The intake proceed path now emits a deterministic decomposition_handoff object.

The handoff is authorization context only. It does not create tasks, case packets, planner output, runtime execution, model execution, platform work, OpenClaw integration, bridge execution, adapter execution, installer work, WSL work, Discord work, vendoring, cleanup, oz, or Codex work.

Clarify and blocked outcomes do not include a decomposition_handoff.

Local validation for this boundary includes:

- Python compile check for orchestrator/intake.py and tests/test_phase_64_intake_handoff.py.
- Phase 57 through Phase 62 regression unit tests in an external validation copy.
- Phase 64 dedicated unit tests in an external validation copy.

## Validation Repair Result

A prior Phase 64 implementation attempt wrote code and docs but used a broken validation-copy command and did not check native command exit codes. Its compile/test pass markers are superseded and must not be treated as proof.

This repair boundary rewrote the Phase 64 intake implementation and dedicated Phase 64 test, scanned both files for paste artifacts, copied the product repo to an external validation directory with robocopy, verified the expected validation files existed, and accepted compile/unit-test results only after explicit native exit-code checks.

Repair validation passed for:

- Python compile check for orchestrator/intake.py and tests/test_phase_64_intake_handoff.py.
- Phase 57 through Phase 62 regression unit tests.
- Phase 64 dedicated intake handoff tests.

Phase 64 remains product-only. It does not authorize runtime execution, model execution, WSL, installer work, Discord, OpenClaw, bridge, adapter, A18CF, platform mutation, vendoring, cleanup, oz, or Codex.

## PHASE_64_FINAL_VALIDATION_SUPERSEDES_FALSE_REPAIR_MARKERS

A prior Phase 64 repair attempt entered the Python REPL and then resumed after operator exit, causing false validation markers and documentation claims to be emitted without valid compile/test proof.

This section supersedes those earlier false validation claims.

Current accepted validation is the final validation boundary:

VALIDATE_PHASE64_CURRENT_STATE_SUPERSEDE_FALSE_VALIDATION_MARKERS_AND_EXPORT_NO_REWRITE_NO_RUNTIME_NO_WSL_NO_INSTALLER_NO_MODEL_NO_DISCORD_NO_BRIDGE_NO_ADAPTER_NO_A18CF_NO_VENDOR_NO_CLEANUP_NO_OZ_NO_CODEX

Accepted proof requirements:

- Phase 64 implementation/test files contain required markers and no prompt paste artifacts.
- External validation copy contains the expected product files.
- python -m py_compile exits with code 0.
- Phase 57 through Phase 62 regression tests exit with code 0.
- Phase 64 dedicated intake handoff test exits with code 0.

Phase 64 remains product-only and does not authorize runtime execution, model execution, WSL, installer work, Discord, OpenClaw, bridge, adapter, A18CF, platform mutation, vendoring, cleanup, oz, or Codex.

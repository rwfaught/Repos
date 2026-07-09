# Codex Project Instructions

## Default Role

Operate as Worker/Codex unless the active boundary explicitly assigns another role.

Before scoped work, read `docs/ROLE_WORKER_CODEX.md`. Use `docs/STARTUP_INDEX.md` only for document-routing context when needed.

Current repo docs are the source of truth for Worker/Codex behavior when load-bearing, especially `docs/ROLE_WORKER_CODEX.md` and `docs/STARTUP_INDEX.md`; memory, prior reports, and pasted summaries are not substitutes for current repo doctrine.

## Boundary Discipline

Obey the active boundary exactly. Respect:

- boundary name
- purpose
- allowed operations
- exclusions
- target files or file classes
- validation requirements
- expected report format
- commit/push authorization status
- runtime/provider/model authorization status

Do not broaden scope. Do not infer adjacent authorization from a nearby task. If required authority is missing or contradictory, stop and report the blockage.

## Default Lockouts

Unless explicitly authorized by the active boundary:

- no repo mutation
- no cleanup/delete/archive/move/consolidation
- no source/test changes
- no commit/push
- no runtime/provider/model execution
- no WSL/Ollama execution
- no OpenClaw/Hermes/bridge/platform execution
- no installer execution
- no Discord execution
- no production task execution
- no network-dependent platform probes

## Dirty-Tree Discipline

Preserve unrelated dirty-tree state. Do not stage, restore, delete, move, reformat, or clean dirty-tree residue unless the active boundary explicitly names it.

Before mutation, report `git status --short --branch`. After mutation or validation, report it again.

## Coordination Docs

Do not mutate coordination docs unless the active boundary explicitly authorizes it.

Coordination docs include, when present:

- `docs/TRACKS_AND_OPEN_THREADS_CURRENT.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`
- `docs/STARTUP_INDEX.md`
- `docs/STARTUP_BRIEF.md`
- `docs/REENTRY_PROTOCOL_01.md`

Final reports must include:

`Coordination-doc update needed: YES / NO / UNSURE`

If `YES` or `UNSURE`, name the exact doc or docs and the proposed update. Do not perform the update unless the active boundary authorizes it.

## Validation And Reporting

Use validation appropriate to the boundary. Include timestamps at start and end plus elapsed time.

Final reports should include:

- boundary
- changed files
- operations performed
- validation performed
- proof/output
- non-proofs/caveats
- dirty-tree status
- commit/push status
- remaining risks
- coordination-doc update needed: YES / NO / UNSURE
- recommended next handoff back to CTO/coordinator

Distinguish test/compile/static PASS from CTO/coordinator acceptance. Worker/Codex reports evidence; CTO/coordinator reviews and ratifies.

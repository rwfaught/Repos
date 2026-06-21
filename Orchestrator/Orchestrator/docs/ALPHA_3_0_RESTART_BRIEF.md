# ALPHA_3_0_RESTART_BRIEF.md

## 1. Current state

Repo has a live local case-packet kernel with deterministic create/inspect/init surfaces and no authorized next implementation phase.

## 2. Closed recent phases

- Phase 58: minimal case-packet substrate
- Phase 59: read-only inspectability/readiness
- Phase 60: controlled seed-based initialization helper

## 3. Current Phase state

- Phase 60 is closed.
- No Phase 61 is authorized.
- Current Phase remains: `(none — awaiting next phase definition)`.

## 4. Live authority stack

Primary governance stack:
- `docs/ORCHESTRATOR_METHOD.md`
- `docs/ORCHESTRATOR_INTERACTION_MODEL.md`
- `docs/REENTRY_PROTOCOL_01.md`
- `docs/STARTUP_BRIEF.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`

Strategic/design constraints:
- `docs/PROJECT_VISION.md`
- `docs/CURRENT_SUCCESS_CRITERION.md`
- `docs/PRODUCT_STRATEGY_03.md`
- `docs/PRODUCT_DESIGN_02.md`
- `docs/INTAKE_TRIAGE_DESIGN_04.md`

## 5. Strategic posture

Consultant verdict: continue, but narrow.
Next session starts in re-entry/strategy mode, not implementation momentum.
Alpha 3.0 must re-establish repo truth before recommending any Phase 61.
Alpha 3.0 re-entry should use targeted archive access for canonical snapshots and avoid full extraction by default (see `docs/SNAPSHOT_ACCESS_PROTOCOL_01.md`).

## Bootstrap Workflow Posture

Alpha 3.0 is operating through a bootstrap relay: ChatGPT Orchestrator, human approval membrane, Codex bounded worker, and repo truth.
This relay is not a weakness; it is the current explicit control topology.
The long-term goal is to internalize appropriate parts of this workflow into the Orchestrator system.
Internalization must be phased and bounded.
This section does not authorize Phase 61 or implementation by itself.
The next ranking pass should consider whether a proposed packet strengthens migration from external workflow discipline to internal, inspectable system behavior while preserving the golden-path casework proof.

## 6. OpenClaw/channel-access posture

- OpenClaw/channel access is strategically live.
- OpenClaw/channel access is not implementation-authorized now.
- Discord/SMS/Slack/Telegram-style command surfaces are long-term intended access surfaces.
- Any future transport work must route through a command boundary.
- Orchestrator remains authority over authorization, state transitions, case truth, audit trail, and worker boundaries.

## 7. Owner-authored system principle

System remains "my system" first while preserving seams for adoption as "their system".
This is strategic constraint, not current build authorization for broad customization infrastructure.

## 8. Current product proof target

Likely next product proof: golden-path local dispute packet demo.

## 9. Known watchlist items

- Phase 55 unsupported / missing
- Phase 56 partially supported
- readiness output nesting awkwardness
- substrate inflation risk
- OpenClaw gravitational-center risk
- channel-access enthusiasm outrunning command-boundary design
- main.py command accumulation pressure
- runtime data versus fixture/state separation
- snapshot hygiene items (Zone.Identifier, __pycache__, accidental path artifacts)
- SNAPSHOT_HANDOFF_RELIABILITY:
  - confirm the canonical snapshot before treating archive contents as repo truth
  - prefer smaller handoffs when a full repo archive is unnecessary
  - treat full-folder snapshots as acceptable but noisy
  - watch for stale uploads, duplicate filenames, accidental nested path artifacts, `__pycache__`, `.pyc`, `Zone.Identifier`, and unnecessary runtime/test state under `data/`

## 10. Non-authorized work

- No Phase 61 admitted
- No OpenClaw integration
- No channel/transport integration implementation
- No runtime/gateway refactor
- No broad customization framework

## 11. First actions for Alpha 3.0

1. Perform docs-first orientation from live authority stack.
2. Reconfirm Current Phase and phase ledger truth.
3. Reconfirm closed-state posture for 58/59/60.
4. Re-rank from current strategic membrane before any phase drafting.
5. Only draft a new phase if ranking and explicit approval justify it.

## 12. Next decision membrane

Whether the next approved packet strengthens the golden-path casework proof while preserving bounded trust and command-boundary control, without displacement by channel/runtime enthusiasm.

## Operating notes

- Codex remains the main implementation worker.
- GPT/OpenAI API models remain in use for now.
- Other agents remain separate sessions/roles, not one monolithic agent.

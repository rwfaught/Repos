# Tracks And Open Threads Current

## Purpose

This file is the compact current-state startup summary for CTO/coordinator
orientation. It is a cockpit view of current tracks and open threads. It does
not replace the full historical ledger.

## Source Relationship

- Full historical ledger: `TRACKS_AND_OPEN_THREADS.md`
- Read this current summary by default for startup orientation.
- Read the full ledger only when named, when historical proof/open-thread
  archaeology is required, or when a boundary explicitly asks for it.

## Last Updated / Source Posture

- Current repo HEAD at edit time:
  `81db15d77eed41ab8e0556b9b9351b33be1b5ace`
- Generated/edited: `2026-07-08T20:37:31-05:00`
- Source state must be verified against live git, operator evidence, worker
  evidence, and current repo docs before being treated as current proof.

## Current Decision Membrane

The active decision membrane is founder/product-wedge control around the
neutral dossier/case abstraction.

Current safely inferable posture:

- No first product wedge is selected.
- Roger ratified Option 3: build the neutral dossier/case abstraction first,
  then choose the first product domain.
- Phase 387 remains parked unless Roger or CTO/coordinator explicitly
  authorizes it.
- The prior dry/report-only MVP milestone commit decision is resolved:
  `d40c6d4 Complete dry MVP milestone` is already in the
  pushed `main` ancestry before `969a13f`. The dry MVP successor/local-worker
  proof package is now committed and pushed in current `main` ancestry via
  `71be0c196e382c0aa8e2dead4a2b940a62a9fd18`. It preserves its narrow proof
  posture and does not authorize broader runtime, provider/model, product, or
  production-readiness conclusions.
- The session-record workflow protocol
  (`docs/session_records/SESSION_RECORDS_PROTOCOL.md`) is committed and pushed
  in current `main` ancestry via
  `9fab81c280a47f0626350f80033494103d38bd63`.
- The session-record pilot
  (`SESSION_RECORDS_PROTOCOL_PILOT_RECORD_DOCS_ONLY`) is completed, committed,
  pushed, and ratified in current `main` ancestry via
  `c6e00da Add session-record protocol pilot record`. `docs/session_records/`
  remains `READ_WHEN_NAMED`; its index now lists the pilot record as an
  evidence artifact.
- AGENTS source-authority hardening is completed, committed, pushed, and
  ratified in current `main` ancestry via
  `616c8e2 Clarify Worker source authority in AGENTS`.
  `AGENTS_SOURCE_AUTHORITY_DOCTRINE_HARDENING_COMMIT_PUSH_VERIFY=RATIFIED`
- `DOSSIER_CASE_TASK_READINESS_OPERATOR_REVIEW_DOCS_ONLY` is completed,
  committed, pushed, and ratified in current `main` ancestry via
  `81db15d Add dossier case task-readiness operator review`.
  `DOSSIER_CASE_TASK_READINESS_OPERATOR_REVIEW_COMMIT_PUSH_VERIFY=RATIFIED`

If a later handoff claims a different active membrane, treat this summary as
stale and verify against live docs and evidence.

## Current Success Anchor

`CURRENT_SUCCESS_CRITERION.md` records a bounded coding-task success bar:
operator-facing bounded coding-task proof through a stable control surface or
repeatable boundary packet.

The anchor remains narrow. It does not prove semantic correctness, live
provider/model behavior, autonomous coding, production readiness,
`general_answer` resumption, OpenClaw/Hermes/Obsidian/LightRAG integration, or
product-wedge selection.

## Active Tracks

| Track | Status | Current posture |
| --- | --- | --- |
| Founder/product-wedge control | ACTIVE | Option 3 is ratified: neutral dossier/case abstraction first, then product-domain choice. No first product wedge selected. |
| Dry MVP bounded-task loop | WATCH | Dry source/test/docs milestone closeout and deterministic local-worker stub proof package are already committed and pushed in current `main` ancestry. The stub proof proves only that a worker-shaped local stub ran under explicit boundary and produced persisted reviewable evidence. |
| Current success / coding-task anchor | WATCH | Current bar remains bounded coding-task proof. Use it for Question 0 and NBM ranking; do not treat it as whole-product proof. |
| Governance / startup / open-thread discipline | ACTIVE | Startup should use this compact current summary and triage visible open threads before ranking NBMs. Session-record protocol, pilot record, and AGENTS source-authority hardening are completed, committed, pushed, and ratified. `docs/session_records/` remains `READ_WHEN_NAMED`; use `docs/session_records/INDEX.md` only when the boundary names session records or evidence archaeology. |
| Local-first model/router/provider | WATCH | Evidence exists for specific smoke/metadata/proof registrations, but live execution and production readiness remain separate future boundaries. |
| General answer lightweight lane | DEFERRED | Report-only structured local lane is paused pending explicit coordinator ranking. |
| Dossier/case mapping and task-readiness seams | WATCH | Source/test/docs seams and docs-only reviews support the neutral abstraction. The task-readiness operator review is completed, committed, pushed, and ratified; it does not select a product wedge or prove runtime/provider/model behavior. |
| Founder-native Human Override / Causal Court material | WATCH | Useful founder-legible calibration/demo material; not current product direction or selected wedge. |
| Platform/OpenClaw/Hermes/RAG/installer integration | DEFERRED | External or future integration tracks only unless an explicit integration boundary authorizes them. |
| Historical artifact/export proof | HISTORICAL | Preserve as proof history. Do not treat older export/upload hashes or packaged artifacts as current source authority without fresh verification. |

## Active Open Threads

| Thread | Status | Current proof posture | Next likely boundary | History pointer |
| --- | --- | --- | --- | --- |
| Neutral dossier/case abstraction before wedge selection | ACTIVE | Docs/source/test seams, founder ratification records, and the ratified task-readiness operator review support abstraction-first posture; no final wedge selected. | `DOSSIER_CASE_NEUTRAL_TASK_PACKET_PLAN_DOCS_ONLY` unless Roger/CTO chooses wedge selection, Source Files refresh/export, or Phase 387 resume decision first. | `TRACKS_AND_OPEN_THREADS.md` |
| Dry MVP skeleton commit decision | RETIRED_OR_RESOLVED | The dry MVP milestone commit is already present in pushed `main` ancestry. This is no longer an active commit/push decision. | None for commit/push. Reopen only if evidence shows the milestone commit is missing or needs targeted repair. | `TRACKS_AND_OPEN_THREADS.md` |
| Dry MVP successor / local-worker proof question | RETIRED_OR_RESOLVED | `DRY_MVP_LOCAL_WORKER_STUB_PROOF_REVIEW_READONLY=PASS`: deterministic local-worker stub proof is committed and pushed in current `main` ancestry via `71be0c196e382c0aa8e2dead4a2b940a62a9fd18` and proves only that a worker-shaped local stub ran under explicit boundary and produced persisted reviewable evidence. It does not prove provider/model execution, subprocess worker execution, Codex handoff execution, file mutation execution, semantic correctness, production readiness, Phase 387, or product-wedge selection. | None for commit/push. Reopen only if targeted repair is found or a future boundary asks for a higher proof bar. | `TRACKS_AND_OPEN_THREADS.md` |
| Current success re-entry / Question 0 | WATCH | Current success anchor is bounded and coding-task focused; dry MVP work may inform the next bar but does not broaden it automatically. | Re-rank against `CURRENT_SUCCESS_CRITERION.md` before new implementation. | `TRACKS_AND_OPEN_THREADS.md` |
| Local provider/runtime execution | WATCH | Specific prior operator proofs are narrow and time-bound; live execution requires explicit future authorization and fresh evidence. | `UNKNOWN_REQUIRES_ROGER_REVIEW` unless a provider/runtime boundary is named. | `TRACKS_AND_OPEN_THREADS.md` |
| General answer productized surfacing | DEFERRED | Report-only contracts exist; no semantic answer quality, service/API/UI, live generation, or production readiness proof. | Explicit coordinator ranking before resumption. | `TRACKS_AND_OPEN_THREADS.md` |
| Platform/OpenClaw/Hermes/RAG integration | DEFERRED | Not product-repo current authority; requires separate integration boundary and fresh operator evidence. | Explicit integration boundary only. | `TRACKS_AND_OPEN_THREADS.md` |

## Current Non-Proofs / Caveats

- Product wedge is not selected unless current docs and Roger review prove
  otherwise.
- Current posture remains no first product wedge selected.
- Phase 387 remains parked unless Roger or CTO/coordinator explicitly
  authorizes it under a future boundary.
- Worker PASS is not CTO/coordinator ratification.
- Old prompts, memory, archives, ZIPs, and prior worker reports are not current
  authority without live repo/source/evidence checks.
- Platform/runtime/model smoke proof is not product readiness.
- Runtime/provider/model work remains unproven and requires an explicit future
  boundary before execution or proof claims.
- Deterministic local-worker stub proof is committed and pushed in current
  `main` ancestry, but proves only that a worker-shaped local stub ran under
  explicit boundary and produced persisted reviewable evidence. It is not
  provider/model execution, local model execution, runtime/platform execution,
  subprocess worker proof, Codex handoff proof, file mutation execution proof,
  semantic correctness proof, production readiness proof, Phase 387
  implementation, or product-wedge selection.
- Session records are `READ_WHEN_NAMED` evidence artifacts. The pilot record is
  listed in `docs/session_records/INDEX.md`, and the workflow is ratified for
  that completed pilot; future session-record edits still require explicit
  boundary authorization.
- No Source Files refresh, export, or capsule proof is implied by this summary.
- The current git tree at edit time includes unrelated dirty-tree residue:
  deleted `../Orchestrator_product_repo_latest.zip`, untracked `outputs/`, and
  untracked files under `../../Source Files/`. Preserve that residue unless a
  later boundary explicitly authorizes touching it.

## Recommended Next Ranked Candidates

1. `DOSSIER_CASE_NEUTRAL_TASK_PACKET_PLAN_DOCS_ONLY`
2. `FIRST_PRODUCT_WEDGE_SELECTION_RECORD_DOCS_ONLY`
3. `SOURCE_FILES_REFRESH_EXPORT_AFTER_TASK_READINESS`
4. `PHASE_387_RESUME_DECISION_DOCS_ONLY`

## Update Discipline

- Keep this file concise.
- Do not append long chronological history here.
- Put historical detail in `TRACKS_AND_OPEN_THREADS.md`.
- Update this file when current active track/open-thread state changes.
- If this file and the full ledger conflict, preserve the conflict and verify
  against live repo, operator, and worker evidence.

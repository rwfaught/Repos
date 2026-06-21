# CODEX EXECUTION PROMPTS (PHASED)
These are the prompts you are to follow. You should find everything you need here. Once you have ingested this file please acknowledge that you understand the contents and will follow protocols as best you can. You are permitted to speak freely, it is not necessary to talk to me as if I am a boss, we are together in this and we are collaborators so never assume I would be upset if you disagreed with me, but lets talk things out when there are disagreements please. Let's have fun!
---

## PHASE 01 — FOUNDATION

Read only:

- docs/SYSTEM_OVERVIEW.md
- docs/BUILD_RULES.md
- docs/PROJECT_CONTEXT.md
- docs/ARCHITECTURE_PLAN.md
- docs/PHASE_INDEX.md
- docs/PHASE_01.md

Follow BUILD_RULES.md strictly.

Complete PHASE_01.md only.

Do NOT:
- implement future phases
- expand scope
- invent alternate directory structures
- create a src/ directory

At the end:
- STOP
- summarize what you created
- list files created or modified
- append a concise entry to docs/ACTION_LOG.md

---

## PHASE 02 — STATE + TASK SYSTEM

Read only:

- docs/SYSTEM_OVERVIEW.md
- docs/BUILD_RULES.md
- docs/PHASE_02.md

Follow BUILD_RULES.md strictly.

Complete PHASE_02.md only.

Do NOT:
- implement orchestrator loop
- implement providers
- implement verifiers
- implement planning logic
- expand beyond task/state system

At the end:
- STOP
- summarize what you did
- list files created or modified
- append to docs/ACTION_LOG.md

---

## PHASE 03 — ORCHESTRATOR LOOP

Read only:

- docs/SYSTEM_OVERVIEW.md
- docs/BUILD_RULES.md
- docs/PHASE_03.md

Follow BUILD_RULES.md strictly.

Complete PHASE_03.md only.

Do NOT:
- implement providers
- implement verifiers
- implement role logic
- add routing complexity
- expand beyond the minimal orchestrator loop

At the end:
- STOP
- summarize actions
- list files created or modified
- append to docs/ACTION_LOG.md

---

## PHASE 04 — VERIFIER FRAMEWORK

Read only:

- docs/SYSTEM_OVERVIEW.md
- docs/BUILD_RULES.md
- docs/PHASE_04.md

Follow BUILD_RULES.md strictly.

Complete PHASE_04.md only.

Do NOT:
- implement model-based review
- implement provider logic
- implement routing logic
- expand beyond the verifier framework

At the end:
- STOP
- summarize actions
- list files created or modified
- append to docs/ACTION_LOG.md

---

## PHASE 05 — PROVIDER ABSTRACTION

Read only:

- docs/SYSTEM_OVERVIEW.md
- docs/BUILD_RULES.md
- docs/PHASE_05.md

Follow BUILD_RULES.md strictly.

Complete PHASE_05.md only.

Do NOT:
- implement real Ollama calls
- implement real Codex calls
- redesign orchestrator flow
- expand beyond provider abstraction

At the end:
- STOP
- summarize actions
- list files created or modified
- append to docs/ACTION_LOG.md

---

## PHASE 06 — ROLE MODULES + PROMPT ASSETS

Read only:

- docs/SYSTEM_OVERVIEW.md
- docs/BUILD_RULES.md
- docs/PHASE_06.md

Follow BUILD_RULES.md strictly.

Complete PHASE_06.md only.

Do NOT:
- implement real AI behavior
- add complex prompt templating
- redesign provider system
- redesign task system
- expand beyond role modules and prompt assets

At the end:
- STOP
- summarize actions
- list files created or modified
- append to docs/ACTION_LOG.md

---

## OPTIONAL CONTROL COMMAND

If using conversational continuation:

User may say:
"continue"

Expected behavior:
- consult PHASE_INDEX.md
- move to next phase
- execute only that phase
- STOP after completion

---

## GLOBAL RULE (ALWAYS IN EFFECT)

- Do not expand scope
- Do not skip phases
- Do not anticipate future phases
- Do not redesign the system mid-phase
- Build only what the current phase requires
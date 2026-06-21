# PHASE_06.md

## Phase 06: Role Modules + Prompt Assets

---

## Goal

Implement the first explicit role layer and its prompt assets.

This phase should create clean, minimal structure for:
- planner role
- coder role
- reviewer role
- role-specific prompt files

The purpose of this phase is to establish how roles are represented in code and on disk.

This phase is about role separation and prompt asset structure, not real model behavior or advanced context assembly.

---

## Files to Create

- agents/planner.py
- agents/coder.py
- agents/reviewer.py
- agents/prompts/planner.md
- agents/prompts/coder.md
- agents/prompts/reviewer.md

---

## Files to Modify (if needed)

- orchestrator/dispatcher.py
- docs/ACTION_LOG.md

---

## Core Behavior

The system must gain an explicit role layer.

Each role module should:
- represent one role clearly
- expose a minimal role identity or helper interface
- optionally load or reference its associated prompt asset
- remain small and readable

Prompt files should:
- live on disk as editable assets
- define the responsibility of that role
- reinforce scope boundaries
- remain concise and practical

This phase does NOT require:
- real model calls
- real planning logic
- real coding intelligence
- real review intelligence
- dynamic prompt composition
- complex context assembly

---

## agents/planner.py (pseudocode)

Purpose:
- represent the planner as a first-class role module

Possible contents:
- role name constant
- helper function to load planner prompt text
- optional helper to prepare a planner payload

Behavior:
- minimal
- explicit
- no real model behavior yet

---

## agents/coder.py (pseudocode)

Purpose:
- represent the coder as a first-class role module

Possible contents:
- role name constant
- helper function to load coder prompt text
- optional helper to prepare a coder payload

Behavior:
- minimal
- explicit
- no real model behavior yet

---

## agents/reviewer.py (pseudocode)

Purpose:
- represent the reviewer as a first-class role module

Possible contents:
- role name constant
- helper function to load reviewer prompt text
- optional helper to prepare a reviewer payload

Behavior:
- minimal
- explicit
- no real model behavior yet

---

## Prompt Asset Requirements

### agents/prompts/planner.md

Must explain that:
- planner decomposes high-level requests into bounded task cards
- planner defines dependencies and success criteria
- planner must not write the whole project directly
- planner does not execute implementation work

### agents/prompts/coder.md

Must explain that:
- coder executes one bounded task at a time
- coder must obey file scope and constraints
- coder must not expand into future tasks
- coder does not control workflow

### agents/prompts/reviewer.md

Must explain that:
- reviewer critiques artifacts against explicit criteria
- reviewer identifies likely defects, inconsistencies, or omissions
- reviewer recommends next action
- reviewer should not rewrite everything unless explicitly assigned a repair task

Prompt files should be:
- concise
- role-specific
- editable on disk
- aligned with BUILD_RULES.md and ARCHITECTURE_PLAN.md

---

## orchestrator/dispatcher.py changes (pseudocode)

Only modify if helpful.

Possible minimal behavior:
- inspect task.role
- map role name to known role module
- optionally load role prompt through the role module
- continue using provider abstraction for execution

Keep this simple.
Do NOT implement full prompt composition yet.
Do NOT implement complex role routing yet.

---

## Constraints

- Keep role modules minimal
- Do NOT implement real AI behavior
- Do NOT add complex prompt templating
- Do NOT redesign provider system
- Do NOT redesign task schema
- Do NOT redesign orchestrator flow
- Keep role boundaries explicit and stable

---

## Expected Runtime Behavior

After this phase, the project should contain:
- dedicated Python modules for planner, coder, and reviewer
- dedicated prompt files for planner, coder, and reviewer
- a clearer mapping from task role to role asset

The dispatcher may remain mostly simple, but the role layer should now exist cleanly and coherently.

---

## Success Criteria

- planner/coder/reviewer modules exist
- planner/coder/reviewer prompt files exist
- role boundaries are clearly expressed
- dispatcher remains compatible with prior phases
- no deep future-phase functionality is implemented prematurely

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was implemented
   - which files were created or modified

2. Append a concise entry to:
   docs/ACTION_LOG.md

3. Do NOT proceed to the next phase
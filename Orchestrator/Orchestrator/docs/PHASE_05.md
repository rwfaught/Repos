# PHASE_05.md

## Phase 05: Provider Abstraction

---

## Goal

Implement the provider abstraction layer for the orchestration system.

This phase should establish the first clean interface between the orchestrator and execution backends.

The system should support:
- a base provider contract
- a mock provider implementation
- an Ollama provider stub
- a Codex provider stub

This phase is about interface design and clean separation, not real backend integration.

---

## Files to Create

- providers/base.py
- providers/mock_provider.py
- providers/ollama_provider.py
- providers/codex_provider.py

---

## Files to Modify (if needed)

- orchestrator/dispatcher.py
- main.py
- docs/ACTION_LOG.md

---

## Core Behavior

The provider layer must let the system execute bounded work through a common interface.

A provider should accept enough information to execute a task, such as:
- role name
- task object or task data
- optional context payload

A provider should return a structured result, such as:
- status
- output
- provider
- metadata
- error

This phase does NOT require:
- real Ollama calls
- real Codex integration
- model networking
- advanced config systems
- provider routing logic beyond a simple default

---

## providers/base.py (pseudocode)

Define a base provider interface or abstract class.

Expected method:

function execute(role, task, context=None)

Expected result structure:

- status
- output
- provider
- metadata
- error

Keep the contract:
- small
- explicit
- easy to implement in later providers

Do NOT overbuild.

---

## providers/mock_provider.py (pseudocode)

Implement a working mock provider.

Behavior:
- accept role/task/context
- return deterministic structured success result
- include task id, title, or role in output when helpful

This provider should be usable immediately by the dispatcher.

It is the default provider for local testing at this stage.

---

## providers/ollama_provider.py (pseudocode)

Create a stub provider.

Behavior for now:
- define provider class
- implement same execute signature
- return a controlled "not implemented" result or raise a controlled, readable error

Do NOT implement real Ollama calls yet.

---

## providers/codex_provider.py (pseudocode)

Create a stub provider.

Behavior for now:
- define provider class
- implement same execute signature
- return a controlled "not implemented" result or raise a controlled, readable error

Do NOT implement real Codex calls yet.

---

## orchestrator/dispatcher.py changes (pseudocode)

Update dispatcher to use provider abstraction.

Possible minimal behavior:
- choose provider name from a simple default
- instantiate provider
- call provider.execute(role, task, context)

For this phase:
- default to mock provider
- keep provider selection simple
- keep code explicit and readable

Do NOT implement advanced provider selection or dynamic configuration.

---

## main.py changes (pseudocode)

Only modify if needed.

Possible minimal additions:
- simple provider selection placeholder
- or no CLI change at all if dispatcher defaults to mock

Do NOT add a large configuration layer.

---

## Constraints

- Keep the abstraction minimal
- Do NOT implement real Ollama calls
- Do NOT implement real Codex calls
- Do NOT redesign orchestrator flow
- Do NOT redesign task schema
- Do NOT add complex config systems
- Keep the mock provider working cleanly
- Keep provider result structures consistent

---

## Expected Runtime Behavior

After this phase:
- dispatcher should be able to execute via mock provider
- mock provider should return structured output
- Ollama and Codex stubs should exist cleanly
- future real backend integration should be possible without redesigning the orchestrator

---

## Success Criteria

- provider modules exist and are coherent
- base provider contract is clear
- mock provider works
- dispatcher can call the mock provider
- Ollama and Codex stubs exist cleanly
- no real backend integration is attempted prematurely
- no unrelated systems are expanded

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
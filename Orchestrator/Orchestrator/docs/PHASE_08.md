# PHASE_08.md

## Phase 08: Real Provider Integration (Ollama)

---

## Goal

Integrate a real Ollama-backed provider into the system while preserving the existing provider contract and execution flow.

This phase enables bounded task execution through a real local model while maintaining:
- deterministic orchestration
- explicit control
- inspectable outputs

The system must:
- keep the mock provider intact
- add a real Ollama provider implementation
- support explicit provider selection
- preserve the existing dispatcher/provider contract
- keep all execution bounded and predictable

---

## Files to Modify

- providers/ollama_provider.py
- orchestrator/dispatcher.py
- main.py (to support explicit provider selection)
- docs/ACTION_LOG.md

---

## Files to Keep Unchanged Unless Strictly Necessary

- providers/base.py
- providers/mock_provider.py
- orchestrator/engine.py
- verifiers/*
- task schema
- role modules
- prompt assets

Do NOT redesign stable layers unless required.

---

## Core Behavior

The Ollama provider must:

1. Accept:
   - role
   - task
   - optional context

2. Receive role prompt content via existing dispatcher flow.

3. Build a bounded prompt using:
   - role prompt
   - task title
   - task role
   - success criteria (brief, human-readable)
   - files in scope (as a short list)

4. Call Ollama locally.

5. Return a normalized `ProviderResult`.

---

## Provider Result Contract

All providers must return:

- `status`:
  - `"success"` for valid execution
  - `"error"` for execution failure

- `output`:
  - model response (string or structured content)

- `provider`:
  - provider name (e.g., `"ollama"`)

- `metadata`:
  - small structured context (e.g., task_id, role)

- `error`:
  - `None` if success
  - string message if failure

This structure must remain consistent across providers.

---

## Provider Selection (Explicit)

Provider selection must be explicit and controlled.

Required behavior:

- CLI must support:

    python main.py next --provider ollama

- If no provider is specified:
    default = "mock"

- Dispatcher must:
    - read provider selection
    - instantiate the correct provider
    - NOT silently fall back for unknown providers

If an unknown provider is requested:
- return a controlled error
- do NOT silently substitute another provider

---

## providers/ollama_provider.py (pseudocode)

Implement `OllamaProvider(BaseProvider)`:

function execute(role, task, context=None):

    try:
        prompt = build_prompt(role, task, context)

        response = call_ollama(prompt)

        return {
            "status": "success",
            "output": response,
            "provider": "ollama",
            "metadata": {...},
            "error": None
        }

    except Exception as e:
        return {
            "status": "error",
            "output": None,
            "provider": "ollama",
            "metadata": {...},
            "error": str(e)
        }

---

## Prompt Assembly Rules (Strict)

Prompt must be:

- short
- human-readable
- structured in sections

Must include:

- role instructions (from prompt file)
- task title
- task role
- success criteria (brief)
- files in scope (brief list)

Must NOT:

- dump full task JSON
- include unrelated system documents
- include large context blobs
- exceed reasonable size for a single task

Prompt assembly must be explicit in code.

---

## orchestrator/dispatcher.py Changes

- Accept provider name from caller
- Load role prompt as before
- Pass role prompt into context
- Instantiate provider based on explicit selection
- Call provider.execute(...)

Do NOT:
- move logic into dispatcher
- introduce routing systems
- add fallback behavior

---

## main.py Changes

Add support for:

    python main.py next --provider ollama

Behavior:

- parse `--provider` argument
- pass provider name into dispatcher/engine path
- default to `"mock"` if not specified

Do NOT:
- introduce CLI frameworks
- introduce complex argument parsing

Keep parsing minimal and explicit.

---

## Validation Expectations

You must test with bounded tasks only.

Required tests:

1. Mock provider still works
2. Ollama provider returns structured result
3. Artifact is created
4. Verification still runs
5. Task status updates correctly
6. Provider failure produces:
   - status = "error"
   - meaningful error message

Do NOT test with:
- large multi-file generation tasks
- open-ended prompts

---

## Constraints

- Preserve provider abstraction
- Preserve orchestrator flow
- Preserve verification integration
- Keep prompt assembly bounded
- Do NOT introduce retries
- Do NOT introduce planner logic
- Do NOT introduce reviewer loops
- Do NOT introduce streaming
- Do NOT introduce hidden fallback behavior

---

## Expected Runtime Behavior

System should now support:

- mock execution (default)
- real Ollama execution (explicit)

Execution flow remains:

1. select task
2. dispatch via provider
3. create artifact
4. run verification
5. update task status

Only difference:
execution may now be real.

---

## Success Criteria

- Ollama provider implemented
- Provider contract respected
- Explicit provider selection works
- Mock provider remains intact
- Real execution produces structured output
- Verification continues to function
- Errors are surfaced cleanly
- No architectural drift introduced

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was implemented
   - which files were modified

2. Report:
   - how provider selection works
   - how prompt assembly works
   - what validation was performed

3. Append a concise entry to:
   docs/ACTION_LOG.md

4. Do NOT proceed further
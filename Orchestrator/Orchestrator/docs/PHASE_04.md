# PHASE_04.md

## Phase 04: Verifier Framework

---

## Goal

Implement the first deterministic verification layer for the orchestration system.

This phase should add a small verifier framework that can:
- run named checks
- return structured results
- support file existence checks
- support directory existence checks
- support Python syntax checks
- be called independently from the CLI

This phase creates the verification subsystem cleanly so later phases can connect it to orchestration and routing.

---

## Files to Create

- verifiers/base.py
- verifiers/file_checks.py
- verifiers/python_checks.py
- verifiers/registry.py

---

## Files to Modify (if needed)

- main.py
- docs/ACTION_LOG.md

---

## Core Behavior

The verifier framework must support deterministic checks such as:

- file_exists
- directory_exists
- python_syntax

Each check must return structured output.

The framework must be usable independently from the CLI.

This phase does NOT require:
- test execution
- JavaScript linting
- HTML/CSS inspection
- model-based review
- routing decisions
- orchestration integration beyond simple CLI access

---

## verifiers/base.py (pseudocode)

Define structured result helpers.

Possible approach:
- VerificationCheckResult
- VerificationResult

Each check result should contain at least:
- name
- passed
- message
- evidence

Overall result should contain at least:
- overall_passed
- checks
- messages

All structures must be JSON-serializable.

Keep this simple and explicit.

---

## verifiers/file_checks.py (pseudocode)

Implement:

function check_file_exists(path)
function check_directory_exists(path)

Behavior:
- return structured pass/fail results
- do not raise uncaught exceptions for normal missing-path cases
- include path in evidence

Messages should be readable and concise.

---

## verifiers/python_checks.py (pseudocode)

Implement:

function check_python_syntax(path)

Behavior:
- verify target exists
- verify target is a file
- attempt to parse or compile the Python source
- return structured pass/fail result
- include syntax error details in evidence if parsing fails

Keep implementation minimal and robust.

---

## verifiers/registry.py (pseudocode)

Implement a lightweight registry for named verifier steps.

Behavior:
- map string names to check functions
- allow a check to be run by name with a target path

Supported names:
- "file_exists"
- "directory_exists"
- "python_syntax"

Possible helper:
function run_check(check_name, target_path)

Optional helper:
function list_checks()

Keep this interface small and easy to extend later.

---

## main.py changes (pseudocode)

Add a CLI command:

if command == "verify":
    parse:
        verify <check_name> <target_path>

    run verifier via registry
    print readable structured output

Keep CLI changes minimal.
Do NOT introduce a framework-heavy command system.

---

## Constraints

- Keep verifier framework minimal and explicit
- Do NOT implement model-based review
- Do NOT implement test runners yet
- Do NOT implement complex routing or orchestrator changes
- Prefer readable JSON-serializable structures
- Keep outputs understandable to a human
- Do NOT expand beyond the named checks listed above

---

## Expected Runtime Behavior

After this phase, commands like these should work:

python main.py verify file_exists orchestrator/engine.py
python main.py verify directory_exists data/tasks
python main.py verify python_syntax main.py

Each should return:
- pass/fail
- concise message
- relevant evidence

---

## Success Criteria

- verifier modules exist and are coherent
- file existence checks work
- directory existence checks work
- Python syntax checks work
- `python main.py verify ...` runs without crashing
- outputs are structured and readable
- no future-phase systems are implemented prematurely

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
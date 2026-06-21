# PHASE_26.md

## Phase 26: Scope Clarification — Software-First, Not Software-Only

---

## Goal

Clarify in the governing and context documents that the project is currently implemented around software-oriented workflows, but is not constitutionally limited to software-only use.

This phase should ensure that future implementation work preserves the possibility of broader bounded-work applicability where appropriate.

This is a docs-only clarification phase.

It is NOT about:
- redesigning the system into a fully domain-general framework
- weakening the current software-first implementation
- changing code behavior
- adding features
- renaming core concepts broadly
- introducing abstract architectural manifestos

---

## Problems This Phase Must Solve

### Problem 1: Current Implementation Bias Could Quietly Become Constitutional Narrowing

The system has been built primarily around software-oriented workflows.
That is reasonable and expected.

But if the governing documents do not clearly distinguish:
- current implementation focus
from
- longer-term architectural scope

then future work may drift into unnecessary software-only assumptions.

---

### Problem 2: Future Workers Need an Explicit Constraint Against Unnecessary Narrowing

The project should remain free to support broader bounded, inspectable, code-mediated workflows in the future.

That does not mean pretending the current system is already domain-general in practice.

It means making the intended scope explicit enough that future local decisions do not quietly harden the framework into a code-only system by default.

---

## Files to Modify

Modify only the minimum docs needed.

Likely candidates:
- `docs/SYSTEM_OVERVIEW.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/ARCHITECTURE_PLAN.md`
- repository README surface if appropriate
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

Do NOT modify implementation code.

---

## Required Clarification

The updated docs should make the following points explicit:

1. The current build is software-first in implementation emphasis.
2. The underlying orchestration architecture is intended to remain applicable to broader bounded workflows where possible.
3. Future phases should avoid unnecessary software-only narrowing in:
   - role semantics
   - artifact concepts
   - task semantics
   - verification assumptions
   unless the current phase explicitly requires it.
4. This clarification does NOT claim that the current system is already fully domain-general in practical capability.

The wording should be:
- concrete
- restrained
- realistic
- aligned with the project’s existing style

---

## Constraints

- Keep this phase tightly scoped
- Do NOT overstate current generality
- Do NOT weaken the current software-oriented implementation truth
- Do NOT add architectural sprawl
- Do NOT create new subsystems
- Do NOT modify code

This is a constitutional clarification, not a redesign.

---

## Validation Requirements

Validate at least these cases:

### Test A: Current Implementation Reality Preserved

Expected:
- docs still accurately reflect that the current system is strongest in software-oriented workflows

### Test B: Future Scope Clarified

Expected:
- docs now explicitly protect against unnecessary software-only narrowing

### Test C: No Overclaiming

Expected:
- docs do not pretend the current system is already a general all-domain executor

---

## Success Criteria

- governing/context docs clearly distinguish software-first implementation from software-only constitutional scope
- future workers gain an explicit constraint against unnecessary narrowing
- no code changes are introduced
- no architectural drift is introduced

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was clarified
   - which files were modified

2. Append a concise entry to:
   `docs/ACTION_LOG.md`

3. Update:
   `docs/PHASE_INDEX.md`

4. Do NOT proceed further

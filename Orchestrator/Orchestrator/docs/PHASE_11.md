# PHASE_11.md

## Phase 11: Reviewer Execution + Recommendation Recording

---

## Goal

Make reviewer tasks operationally meaningful by giving reviewer output a constrained, system-readable landing point.

This phase should allow the system to:

- execute reviewer tasks
- validate reviewer output structurally
- persist a small recommendation record
- mark reviewer tasks as completed only when that recommendation record is valid

This phase is about making reviewer judgment inspectable and machine-usable.

It is NOT yet about:
- automatic repair
- retry loops
- writeback
- recursive reviewer routing
- autonomous task creation from reviewer output

---

## Problems This Phase Must Solve

### Problem 1: Reviewer Tasks Can Run but Their Output Has No Disciplined Landing Point

The current system can now:

- detect inadequate ordinary-task output
- route that task into `needs_review`
- create a queued reviewer task
- run reviewer tasks

But reviewer output is still just output text unless the system can interpret it into a constrained record.

This means reviewer tasks exist operationally, but not yet semantically.

---

### Problem 2: Reviewer Judgment Must Not Become Immediate Action

Reviewer output should inform the system without silently turning the reviewer into:

- a planner
- a repair engine
- a routing engine

This phase must preserve inspectability and control by storing reviewer judgment as a bounded recommendation record only.

The system should stop after recording that recommendation.

---

## Files to Create

- orchestrator/reviewer_output.py

---

## Files to Modify

- orchestrator/engine.py
- docs/ACTION_LOG.md
- docs/PHASE_INDEX.md

---

## Directories to Create (if missing)

- data/reviewer_recommendations/

Created at runtime if needed.

---

## Core Behavior

This phase applies only to reviewer-role tasks.

For a reviewer task, after:

1. provider execution
2. artifact creation
3. verification success

the system must attempt to validate reviewer output into a constrained recommendation record.

If reviewer output is structurally valid:
- persist the recommendation record
- mark the reviewer task as `completed`

If reviewer output is structurally invalid:
- do NOT persist an accepted recommendation record
- mark the reviewer task as `verification_failed`

Do NOT introduce a new reviewer-specific failure status in this phase.

Keep status handling minimal.

---

## Reviewer Recommendation Record

A reviewer recommendation record must contain exactly these required fields:

- `recommendation_type`
- `reason`
- `source_task_id`
- `source_artifact_id`

Optional fields should be avoided unless strictly necessary.

The system must not depend on additional freeform fields in this phase.

---

## Allowed Recommendation Types

The allowed `recommendation_type` values must be a closed set:

- `accept`
- `manual_followup`
- `repair_candidate`

No other values are allowed in this phase.

Do NOT introduce:
- arbitrary action names
- freeform routing instructions
- nested recommendation payloads
- planning structures

Keep this closed and deterministic.

---

## Reviewer Output Validation Rules

Reviewer output validation must be deterministic and explicit.

A reviewer output is structurally valid only if all of the following are true:

1. reviewer output is present
   - not `None`
   - not empty
   - not whitespace only

2. reviewer output is valid JSON object text

3. reviewer output can be parsed into the required recommendation fields

4. `recommendation_type` is one of:
   - `accept`
   - `manual_followup`
   - `repair_candidate`

5. `reason` is present and non-empty

6. `source_task_id` is present and non-empty

7. `source_artifact_id` is present and non-empty

If any required field is missing or invalid:
- reviewer output is structurally invalid

Keep validation conservative and explicit.

---

## Required Output Shape

Reviewer output must be JSON only.

Expected format:

```json
{
  "recommendation_type": "manual_followup",
  "reason": "The original output was too weak to satisfy the requested bounded implementation task.",
  "source_task_id": "task_123",
  "source_artifact_id": "artifact_456"
}
```

This phase should validate exactly this general object shape.

Do NOT support multiple formats.

Do NOT support prose-only reviewer output.

Do NOT add fallback parsing for loosely structured text.

---

## Reviewer Task Outcome Rules

Reviewer task outcome resolution must follow this order:

### Rule 1: Execution Failure Wins

If provider result has:

- `status == "error"`

Then:
- reviewer task status = `execution_failed`

Do NOT attempt recommendation validation after execution failure.

---

### Rule 2: Verification Failure Still Wins Before Recommendation Validation

If provider execution succeeds, but normal verification fails, then:
- reviewer task status = `verification_failed`

Do NOT attempt recommendation validation if verification already failed.

---

### Rule 3: Recommendation Validation Runs Only After Successful Execution and Successful Verification

Only if:
- execution status = `success`
- verification passed

Then:
- validate reviewer output structure

If valid:
- save recommendation record
- reviewer task status = `completed`

If invalid:
- reviewer task status = `verification_failed`

---

## Recommendation Persistence

When reviewer output is valid, save a recommendation record to:

- `data/reviewer_recommendations/<task_id>_<timestamp>.json`

Each saved record should include at least:

- reviewer task ID
- run ID
- recommendation record
- timestamp

You may also include:
- provider name

Only if that is helpful and does not complicate the schema unnecessarily.

Keep persisted records JSON and inspectable.

---

## Scope Rules

This phase applies reviewer recommendation handling only to reviewer-role tasks.

Do NOT apply reviewer recommendation parsing to:
- planner tasks
- coder tasks
- ordinary non-review execution
- tasks merely in a review-adjacent status

This is a targeted extension, not a generalized output-parsing system.

---

## orchestrator/reviewer_output.py (pseudocode)

This module may include:

function parse_reviewer_recommendation(output_text):
    parse JSON object only
    return parsed dict or controlled failure result

function validate_reviewer_recommendation(data):
    check required fields
    check allowed recommendation_type values
    return validation result

function build_recommendation_record(task, parsed_data):
    return normalized persisted recommendation record

Keep this module:
- small
- explicit
- deterministic

Do NOT add scoring, ranking, or semantic inference systems.

---

## orchestrator/engine.py Changes

Update the execution flow so that:

- ordinary tasks continue behaving exactly as they do now
- reviewer-role tasks gain one extra step after successful execution and verification:
  - reviewer output validation
  - recommendation persistence if valid

Expected reviewer-task flow:

1. select reviewer task
2. mark `in_progress`
3. dispatch via provider
4. create artifact
5. run verification
6. if execution failed → `execution_failed`
7. else if verification failed → `verification_failed`
8. else validate reviewer output
9. if valid:
   - persist recommendation record
   - mark `completed`
10. else:
   - mark `verification_failed`

Summary output should clearly show:
- provider
- execution status
- verification status
- reviewer recommendation validation result
- final task status
- recommendation record path or ID if created

---

## Implementation Guidance

Keep recommendation parsing and validation inside `orchestrator/reviewer_output.py`.

Do NOT turn `run_manager.py` into a general persistence bucket for this phase unless a concrete implementation need forces a minimal helper.

If no helper is truly needed, persist recommendation records through a narrow explicit path in the engine or reviewer-output layer.

Preserve the smallest possible modification surface.

---

## Constraints

- Keep this phase tightly scoped
- Do NOT implement automatic repair-task creation
- Do NOT implement retry loops
- Do NOT implement writeback/application logic
- Do NOT implement recursive reviewer routing
- Do NOT implement planner-generated tasks
- Do NOT introduce fuzzy scoring or confidence systems
- Do NOT expand reviewer output into a general planning language
- Do NOT redesign stable prior-phase components unless strictly necessary
- Do NOT modify `task_schema.py` unless implementation proves it is necessary

This phase is about recommendation recording, not recommendation execution.

---

## Validation Requirements

This phase must be validated with at least these cases:

### Test A: Valid Reviewer Recommendation

Use a reviewer task whose provider output is valid JSON reviewer output.

Expected:
- execution success
- verification pass
- recommendation validation pass
- recommendation record persisted
- final task status = `completed`

---

### Test B: Invalid Reviewer Recommendation Structure

Use a reviewer task whose output is missing required fields or uses an invalid `recommendation_type`.

Expected:
- execution success
- verification pass
- recommendation validation fail
- no accepted recommendation record persisted
- final task status = `verification_failed`

---

### Test C: Reviewer Execution Failure

Use unknown provider or forced provider error for a reviewer task.

Expected:
- final task status = `execution_failed`
- no recommendation validation attempted
- no recommendation record created

---

### Test D: Reviewer Verification Failure

Use a reviewer task with successful execution but failing normal verification.

Expected:
- final task status = `verification_failed`
- no recommendation validation attempted
- no recommendation record created

---

### Test E: Ordinary Task Behavior Unchanged

Run a non-reviewer task through the current flow.

Expected:
- ordinary adequacy routing still behaves as before
- no reviewer recommendation parsing is applied
- no regression in ordinary task handling

---

## Success Criteria

- reviewer output validation exists and is deterministic
- reviewer recommendation records can be persisted
- reviewer tasks become `completed` only when recommendation structure is valid
- invalid reviewer output is classified as `verification_failed`
- execution and verification precedence remain intact
- ordinary task behavior remains unchanged
- no automatic repair or routing behavior is introduced
- no architectural drift is introduced

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was implemented
   - which files were created or modified

2. Report:
   - how reviewer recommendation validation works
   - how recommendation persistence works
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further

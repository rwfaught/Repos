# PHASE_13.md

## Phase 13: Recommendation Visibility + Status Surfacing

---

## Goal

Make persisted reviewer recommendation records visible as part of the system’s explicit operator-facing control surface.

This phase should allow the system to:

- discover persisted reviewer recommendation records
- display concise recommendation summaries
- surface recommendation state through the CLI in a bounded, inspectable way
- preserve the separation between recommendation visibility and recommendation execution

This phase is about making reviewer outcomes visible and legible.

It is NOT yet about:
- acting on reviewer recommendations
- automatic repair task creation
- retry loops
- writeback/application logic
- recommendation-driven routing
- planner-generated follow-up work

---

## Problems This Phase Must Solve

### Problem 1: Recommendation Records Exist but Are Not Part of the Visible Workflow Surface

Phase 11 introduced persisted reviewer recommendation records.

Phase 12 added regression tests for that behavior.

But recommendation records currently live only as JSON files on disk.
They are not yet surfaced through the normal operator-facing system interface.

This means the system can store reviewer judgment but cannot cleanly show it.

---

### Problem 2: The System Needs Awareness Before Action

The next future capability may involve bounded interpretation or routing based on reviewer recommendations.

But before the system can safely act on recommendations, it must first make them clearly visible.

This phase must improve awareness without introducing hidden behavior.

---

## Files to Create

Create only the minimum new file(s) needed.

Recommended:
- orchestrator/recommendation_store.py

If implementation proves this helper is unnecessary, keep the logic minimal and explicit elsewhere.

---

## Files to Modify

- main.py
- docs/ACTION_LOG.md
- docs/PHASE_INDEX.md

If strictly needed:
- orchestrator/run_manager.py (minimal read-only helper only)
- orchestrator/engine.py (only if a tiny summary hook is necessary)

Do NOT modify reviewer recommendation semantics.

---

## Core Behavior

The system must gain a minimal way to inspect persisted reviewer recommendation records.

Recommended CLI behavior:

`python main.py recommendations`

Optional bounded variant:

`python main.py recommendations --run <run_id>`

If no run filter is provided:
- show recent or all persisted recommendation records in a simple readable list

If a run filter is provided:
- show only recommendation records for that run

Keep this behavior:
- explicit
- read-only
- human-readable
- deterministic

---

## Recommendation Visibility Requirements

For each surfaced recommendation record, show at least:

- reviewer task ID
- run ID
- recommendation_type
- reason
- source_task_id
- source_artifact_id
- timestamp

Optional:
- provider

Only if it is already stored and easy to show without extra complexity.

Do NOT infer or invent additional meaning.

---

## Required CLI Behavior

### Command: recommendations

The command must:

1. Read persisted recommendation records from:
   - `data/reviewer_recommendations/`

2. Parse records safely

3. Print a concise readable summary for each record

4. Handle empty state cleanly:
   - if no recommendation records exist, print a clear message

5. Remain read-only

Do NOT:
- mutate tasks
- create tasks
- apply recommendations
- alter workflow state

---

## Filtering Rules

If `--run <run_id>` is implemented:

- filter recommendations by `run_id`
- do not add broader filtering yet

Do NOT add:
- task-role filters
- recommendation-type filters
- sorting frameworks
- search systems

Keep filtering minimal.

---

## Recommendation Store Helper (Optional)

If `orchestrator/recommendation_store.py` is created, it may include:

- function load_recommendation_records()
- function load_recommendation_records_for_run(run_id)
- function format_recommendation_summary(record)

Keep it:
- small
- read-only
- explicit

Do NOT turn this into a routing layer.

---

## Output Rules

CLI output must be:

- concise
- readable
- explicit about empty results
- stable in structure

Example shape:

- Recommendation record count
- One readable block per recommendation:
  - reviewer task ID
  - run ID
  - recommendation type
  - reason
  - source task
  - source artifact
  - timestamp

Do NOT emit raw JSON unless that is the only minimal path and no readable formatter is feasible.

---

## Constraints

- Keep this phase tightly scoped
- Do NOT introduce recommendation execution
- Do NOT create repair tasks
- Do NOT add retries
- Do NOT add writeback
- Do NOT redesign persistence
- Do NOT broaden CLI into a large query interface
- Do NOT introduce hidden routing behavior
- Do NOT alter existing reviewer recommendation records

This phase is visibility only.

---

## Validation Requirements

This phase must be validated with at least these cases:

### Test A: Recommendation Records Exist

Given one or more persisted recommendation records,
running:

`python main.py recommendations`

Expected:
- records are loaded
- readable summaries are printed
- required fields are visible

---

### Test B: Empty Recommendation Directory

Given no persisted recommendation records,
running:

`python main.py recommendations`

Expected:
- clear no-records message
- no crash

---

### Test C: Run Filter Works (Only If Implemented)

Given recommendation records from multiple runs,
running:

`python main.py recommendations --run <run_id>`

Expected:
- only matching run records are shown

---

### Test D: Read-Only Guarantee

Running the recommendations command must not:
- modify tasks
- create artifacts
- alter state
- create new recommendation records

---

## Success Criteria

- reviewer recommendation records are visible through a bounded CLI surface
- output is readable and deterministic
- empty-state handling is clear
- recommendation visibility remains read-only
- no routing or execution behavior is introduced
- no architectural drift is introduced

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was implemented
   - which files were created or modified

2. Report:
   - how recommendation records are loaded
   - how the CLI command works
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further

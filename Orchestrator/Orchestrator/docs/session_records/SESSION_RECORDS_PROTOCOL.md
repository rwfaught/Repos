# Session Records Protocol

## Purpose

Session records are compact repo-backed evidence records for bounded
Orchestrator sessions. They preserve what a session claims it inspected, did,
validated, did not prove, and recommends reporting back to CTO/coordinator.

Session records support continuity and evidence archaeology. They do not
replace current repo docs, startup docs, role docs, CTO/coordinator review, or
Roger/CTO ratification.

## Authority Status

Session records are evidence artifacts only unless CTO/coordinator ratifies
them. A saved record is not:

- a CTO handoff
- startup authority
- project ratification
- an accepted fact by itself
- authorization for mutation, runtime execution, cleanup, commit, or push
- permission to route the next session
- proof that adjacent capability exists

Only CTO/coordinator may create official CTO handoffs or initialize
CTO/coordinator continuity. Relay, Worker/Codex, Platform/Substrate, and
Specialist sessions may create closeout records only when assigned by an
explicit boundary. Non-CTO records must not label themselves as CTO handoffs,
use CTO/coordinator response metadata, route the next session, or create or
re-create CTO/coordinator continuity unless CTO/coordinator explicitly assigns
a handoff-drafting task for review.

## Load Discipline

`docs/session_records/` is `READ_WHEN_NAMED`. Do not load session records by
default during startup.

Read records only when:

- the user or boundary names a specific record
- the boundary requires the session-record folder
- evidence archaeology requires a targeted record lookup
- CTO/coordinator asks to review or ratify a saved record

Use `docs/session_records/INDEX.md` first for discovery. After the index
narrows the target, read only the specific records needed.

## Mutation Discipline

Writing, updating, moving, deleting, archiving, or reclassifying session
records is repo mutation. It requires an explicit boundary naming the target
record or file class.

A boundary to write a record should name:

- the role allowed to write
- the source session or closeout being recorded
- the target file or file class under `docs/session_records/`
- whether `INDEX.md` may be updated
- whether commit/push is authorized

Do not create session records opportunistically. Do not clean, archive, or
consolidate old records without a separate explicit cleanup or retention
boundary.

## Naming Convention

Use one Markdown file per saved session record.

Preferred filename pattern:

`YYYY-MM-DD_role_boundary-slug.md`

Examples:

- `2026-07-08_cto-coordinator_boundary-slug.md`
- `2026-07-08_relay_boundary-slug.md`
- `2026-07-08_worker-codex_boundary-slug.md`
- `2026-07-08_platform-substrate_boundary-slug.md`
- `2026-07-08_specialist_boundary-slug.md`

Use lowercase role slugs, ASCII letters and digits, hyphens, and underscores.
Keep the boundary slug short enough for scanning.

## Required Fields

Each saved session record should include:

- title
- record type
- role
- boundary
- date or timestamp
- source session or source closeout, when known
- repo/path context, when applicable
- HEAD or source state, when relevant and observed
- files, docs, systems, or evidence inspected
- operations performed
- validation or proof observed
- non-proofs and caveats
- authority status
- coordination-doc implications, if any
- recommended report-back to CTO/coordinator

Record only what was actually observed or reported. If a field is unknown,
state `Unknown` or `Not inspected` rather than inventing continuity.

## Compact Template

```markdown
# Session Record: <role> / <boundary>

Record type: <CTO handoff | Relay closeout | Worker/Codex report | Platform/Substrate report | Specialist memo | Capsule for CTO review>
Role: <role>
Boundary: <boundary>
Date/time: <timestamp or date>
Source session/closeout: <identifier, link, or Unknown>
Repo/path context: <path or Not applicable>
HEAD/source state: <hash/status or Not inspected>

## Evidence Inspected

- <files, docs, command output, logs, or supplied evidence>

## Operations Performed

- <what the session did>

## Validation Or Proof

- <observed checks, outputs, or proof>

## Non-Proofs And Caveats

- <what this record does not prove>

## Authority Status

This record is an evidence artifact only unless CTO/coordinator ratifies it.
It is not startup authority and not a CTO handoff unless the record type is
`CTO handoff` and CTO/coordinator authored or ratified it as such.

## Coordination-Doc Implications

Coordination-doc update needed: <YES / NO / UNSURE>
Details: <doc names and proposed update, or None>

## Recommended Report-Back To CTO/Coordinator

- <concise recommendation or next review item>
```

## Role-Specific Rules

### CTO/Coordinator

CTO/coordinator may create official CTO handoffs, ratify records, and decide
whether a saved record affects accepted facts, current-state docs, startup
routing, or open-thread continuity.

A CTO/coordinator record may carry authority only when it explicitly states
that CTO/coordinator is ratifying the content and names the evidence basis.

### Relay

Relay may save a closeout record only when the active boundary authorizes
repo-backed record writing. A Relay record may describe command/script
construction, assumptions, failure modes avoided, and validation expectations.
It must not claim commands executed unless supplied proof shows that execution.

### Worker/Codex

Worker/Codex may save a report record only inside explicit file scope. A
Worker/Codex record may report inspected files, changed files, validation, git
status, non-proofs, and coordination-doc implications. It must not rank NBMs,
ratify completion, or route the next session.

### Platform/Substrate

Platform/Substrate may save a record only when the boundary authorizes the
record file or class. Its record may report runtime/substrate findings,
commands run or not run, safety notes, and product-proof caveats. It must not
convert runtime facts into product authority.

### Specialist

Specialist may save a memo only when the boundary authorizes record writing.
Its record may preserve expert judgment, assumptions, risks, and advisory
recommendations. It must not authorize mutation, claim proof, or route project
work unless CTO/coordinator explicitly asked for advisory routing
recommendations.

## Index Discipline

`docs/session_records/INDEX.md` is a lightweight discovery aid. It should list
records compactly without importing the full record content.

The index should not become a second startup ledger. Keep entries concise and
link to records by filename. Do not use the index to ratify records, resolve
open threads, or replace current coordination docs.

## Cleanup And Retention Caution

Session records may become stale. Stale does not mean disposable.

Do not delete, archive, consolidate, rename, or bulk-edit records without an
explicit cleanup/retention boundary. If a record is stale or superseded, prefer
adding a concise index note under an authorized boundary instead of rewriting
the record itself.

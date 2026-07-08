# Session Records

## Purpose

This folder may hold lightweight saved closeout records from bounded
Orchestrator role sessions when an explicit boundary authorizes writing a
record into the repo.

Session records are evidence artifacts, not authority artifacts. A saved Relay
closeout report, Worker/Codex report, Platform/Substrate report, Specialist
memo, or capsule for CTO review does not become a CTO handoff, accepted fact,
project ratification, startup authority, or route for the next session unless
CTO/coordinator ratifies it.

## Record Convention

Use one Markdown file per saved record. Prefer filenames that include the date,
role, and boundary, for example:

`2026-07-08_worker-codex_boundary-name.md`

Each record should state:

- role
- boundary
- timestamp or date
- files or systems inspected
- operations performed
- validation or proof observed
- non-proofs and caveats
- recommended report-back to CTO/coordinator

Non-CTO records may include a capsule for CTO review, but must not label it as
a CTO handoff, use CTO/coordinator response metadata, route the next session,
or create/re-create CTO/coordinator continuity unless CTO/coordinator
explicitly assigned a handoff-drafting task for review.

## Load Discipline

Do not load this folder by default during startup. Read session records only
when named, when a boundary requires a specific record, or when evidence
archaeology is required.

Directly writing records into this folder is repo mutation. It requires an
explicit boundary that names this folder or the intended record file.

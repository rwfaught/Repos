# Project Continuity Evidence Protocol

## Purpose

This protocol defines a portable evidence shape for project continuity,
re-entry, command batches, run artifacts, evidence capsules, and handoffs.

It exists to keep future Orchestrator, Obsidian/LightRAG/Hermes, Blender,
OpenClaw, and other project work anchored to live source truth, durable command
evidence, explicit artifact locations, and honest proof vocabulary.

This is governance documentation only. It does not implement a wrapper script,
run commands, refresh capsules, probe runtimes, or transfer project-specific
facts across boundaries.

## Scope

Use this protocol when a coordinator, relay, operator, or worker needs to:

- re-enter a project after a handoff, capsule upload, source export, or thread
  restart
- run command batches whose output will be used as evidence
- preserve command output as a durable artifact rather than chat-only text
- distinguish live repo proof from source capsule, uploaded-source, operator
  terminal, worker-report, or non-proof evidence
- hand off accepted facts, caveats, open threads, source state, and command
  requirements to another actor or session

Each project keeps its own source-of-truth rules. This protocol provides a
shared evidence grammar; it does not override project-specific phase ledgers,
capsules, manifests, or runtime authority documents.

## Project-Neutral Evidence Vocabulary

- Repo proof: direct observation from the live repository or its VCS metadata.
- Source capsule proof: direct observation of a packaged source capsule, ZIP,
  tarball, or export artifact.
- Uploaded-source proof: direct observation that a capsule was uploaded and
  verified in the receiving context.
- Operator terminal proof: command output captured from the operator's
  terminal, including command text, timestamps, exit codes, and logs.
- Worker report: a bounded worker's written report of actions and validation.
- Role closeout record: a saved Relay closeout report, Worker/Codex report,
  Platform/Substrate report, Specialist memo, or capsule for CTO review.
- Non-proof: memory, chat summary, stale capsule text, unverified handoff
  prose, unexecuted plan text, or in-repo claims about a later artifact.
- Accepted fact: a claim accepted by the governing project authority with its
  evidence basis stated.
- Open thread: unresolved risk, question, or obligation that must remain
  visible until a later boundary resolves it.

## Source Authority Classes

Classify source claims before using them:

- Live repo authority: current files and VCS metadata read from the active repo.
- Fresh capsule authority: a newly created and verified source capsule.
- Stale capsule authority: a capsule that may lag live repo state and requires
  freshness checks before it can support current claims.
- Uploaded-source authority: a source artifact verified in the upload or
  receiving environment.
- External package authority: platform, runtime, installer, or sibling-package
  docs that govern their own track but do not override product repo truth.
- Conversational memory: useful orientation only; not proof without
  reconciliation.

When authority classes conflict, prefer fresh live repo evidence for repo
state, fresh operator terminal proof for command execution, and the relevant
project's own accepted authority for project-specific claims.

## Command Batch Evidence Requirements

Every evidence-bearing command batch should record:

- target project and target path
- command shell and platform, such as PowerShell or Bash
- start timestamp
- finish timestamp
- elapsed time
- exact command text or batch identifier
- exit code
- stdout and stderr, either visible live to Roger/operator or captured in a
  durable log
- artifact paths created by the batch
- explicit non-proofs and caveats

Command output should be visible to Roger/operator and captured to logs. Pasted
chat output alone is not durable command evidence.

## Run Artifact Location Rules

Evidence-bearing run artifacts should live outside the git worktree unless a
boundary explicitly intends them as source artifacts.

Recommended artifact roots include temp directories, dedicated evidence
folders, or project-external run folders named with the project, phase or
boundary, and timestamp.

Do not silently place logs, generated reports, command transcripts, exported
capsules, or proof bundles under the repo root. If an artifact must enter the
worktree, its source role must be explicit and it must be tracked by the
project's normal source authority.

Directly writing session output, closeout reports, memos, capsules, or records
into the repo or GitHub is repo mutation. It requires an explicit boundary
naming the target file or file class. Saved records are evidence artifacts,
not authority artifacts, unless CTO/coordinator ratifies them.

## Re-Entry Proof Checklist

Before relying on re-entry state, prove or classify:

- live repo root and nested product path
- source capsule identity, if a capsule is present
- `HEAD`, upstream, and origin alignment where VCS exists
- clean or dirty working status
- current phase markers and ledger pointers
- relevant open threads and their triage status
- capsule freshness relative to live repo state
- uploaded-source identity, if upload proof is part of the handoff
- stale locks or stale state files that could affect normal tools
- path normalization differences between workspace folder, product repo, and
  actual git root

If a source capsule may lag the live repo, say so and freshness-check it before
treating it as current proof.

## Evidence Capsule Rules

Evidence capsules should separate:

- repo proof
- source capsule proof
- uploaded-source proof
- operator terminal proof
- worker report
- accepted facts
- open threads
- explicit non-proofs

Capsules must state what they prove and what they do not prove. They must not
turn worker PASS, model output, stale memory, or source text into broader
runtime, product, or artifact proof.

## Handoff Requirements

Project handoffs should include:

- accepted facts and evidence basis
- open threads and triage status
- non-proofs and caveats
- next boundary or stop condition
- live repo state and capsule state
- source/capsule freshness notes
- required command/logging shape for the next actor
- run artifact location requirements
- redaction/exclusion requirements
- whether the next actor may mutate files, run scripts, probe runtimes, export,
  package, commit, or push

Official CTO handoffs are the only handoffs that may initialize a new
CTO/coordinator session. A non-CTO role may prepare a capsule for CTO review,
but it must not label that capsule as a CTO handoff, use CTO/coordinator
response metadata, route the next session, or create/re-create CTO continuity
unless CTO/coordinator explicitly assigned a handoff-drafting task for review.

## Redaction And Secret Exclusions

Evidence capsules and logs must redact or exclude:

- tokens, API keys, auth cookies, private keys, passwords, and credentials
- private configs that grant access
- unrelated personal data
- secrets embedded in environment dumps, shell history, or config files

Prefer targeted command output over broad environment or filesystem dumps.
When secret risk is uncertain, capture the minimum evidence needed and record
the omission as an explicit redaction caveat.

## PowerShell And Bash Parity

PowerShell and Bash batches should follow the same evidence shape:

- start timestamp
- finish timestamp
- elapsed time
- exit code
- visible output
- durable log path
- artifact paths
- explicit target repo/path
- explicit shell/platform

Syntax may differ, but the proof fields should not.

## Path Normalization Cautions

Do not infer authority from the prompt path. A workspace folder may contain a
nested product repo, a sibling platform package, backups, capsules, or export
artifacts.

Command batches should declare target paths explicitly and normalize:

- workspace/container folder
- actual git root
- product repo root
- sibling platform repo root
- export/capsule location
- artifact/log location

If a tool reports from the wrong path, preserve the evidence and correct the
target path before making source-state claims.

## Lock And Stale-State Cautions

Re-entry should check for stale state that can distort commands:

- stale `.git/index.lock`
- old generated run artifacts inside the repo root
- stale source capsules
- stale uploaded-source claims
- partially written logs
- interrupted command batches
- prior temp directories being reused as if fresh

Finding a lock or stale artifact is not itself proof of source corruption. It
is a caution that must be handled under the project's own safe operating rules.

## Non-Proofs

The following are not proof by themselves:

- chat memory
- worker report without supporting evidence
- a PASS marker copied without its command/log context
- a source capsule whose freshness is unknown
- in-repo text claiming the hash of a later export
- model output
- route validation
- authorization text
- a command batch with no timestamps, elapsed time, exit code, or durable log
- project-specific runtime facts imported from another project

## Adoption Path For Other Projects

To adopt this protocol in another project:

1. Identify that project's source-of-truth docs, live repo root, capsule shape,
   and evidence ledgers.
2. Map this protocol's neutral vocabulary onto the project's own authority
   classes.
3. Add command-batch logging requirements appropriate to its shell and host.
4. Define where run artifacts live outside its worktree.
5. Define redaction/exclusion rules for that project's secrets.
6. Preserve project-specific non-proofs and open threads.
7. Add tooling only in a later explicit implementation boundary.

## Runtime Fact Transfer Rule

Project-specific runtime facts do not transfer across project boundaries
without an explicit integration boundary.

An Ollama, Hermes, OpenClaw, Blender, LightRAG, or other runtime fact accepted
inside one project can orient another project, but it cannot prove current
availability, behavior, performance, correctness, or production readiness for
the other project until that other project runs its own authorized proof or
accepts the fact through its own integration boundary.

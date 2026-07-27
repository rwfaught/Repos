# Operator Workbench V1 Guide

## What it is

Operator Workbench V1 is a local, single-operator control surface for one
bounded coding task at a time. It creates a packet, shows it before execution,
requires a separate deliberate authorization action, launches the canonical
Orchestrator coding-task CLI, and displays its persisted evidence.

It supports only paths below `workbench_fixtures/`, one declared output, one
named worker selection, and the existing `trusted_local_unsandboxed` posture.
It is not a general chat interface, planner, arbitrary repository editor,
shell console, task queue, sandbox, production service, or provider router.

## Launch

From `Orchestrator/Orchestrator` run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start_orchestrator_workbench.ps1
```

The launcher opens `http://127.0.0.1:8766/workbench`, prints start/end times,
and remains active until `Ctrl+C`. The Founder Cockpit has a link to this
separate surface; the Cockpit itself remains read-only.

## Use

Enter title, objective, a `workbench_fixtures/` path, exact expected output,
validation text, explicit worker, timeout, and optional commit/push intent.
Preview first. Preview creates no task and does not authorize a worker.
`Authorize and run` is the only execution action and preserves the canonical
authorization record. The browser never accepts a shell command or a free-form
provider command.

While executing, the page reports a plain-language result, whether it is ready
for a recorded decision, declared changed paths, and frozen elapsed time once
the worker stops. The technical lifecycle records remain available only in an
optional disclosure. The Workbench shows decision buttons only when the
canonical lifecycle can record them; otherwise it says not to accept yet.

The Codex selection uses the fixed, native Windows Codex CLI distributed at
`C:\Users\accou\.codex\packages\standalone\releases\0.145.0-x86_64-pc-windows-msvc\bin\codex.exe`.
Its protocol adapter receives only the canonical worker JSON, runs Codex in the
isolated worker workspace with workspace-write permissions, and returns the
canonical worker-result envelope after the ordinary changed-path audit. The
adapter removes only the native CLI's known ephemeral top-level `.agents` and
`.git` residues from the fresh worker workspace; this cleanup is recorded in
the worker-result envelope. All other undeclared workspace changes still fail
the canonical audit. The browser cannot provide a command, model, or sandbox
option. `fixture` is
deterministic and exists only for tests and the isolated proof task.

## Recovery, limits, and security

Canonical records remain under `.operator_workbench_data`; refresh or server
restart does not erase them. A restarted Workbench can inspect those records,
but does not claim it can reattach to a prior in-memory launcher process.

The server binds only to `127.0.0.1`, accepts only allowlisted GET/POST routes,
checks a local action token/origin for writes, rejects unsupported methods,
HTML-escapes display content, caps browser-visible captured output, and rejects
traversal and all paths outside the dedicated fixture prefix. The canonical
worker's `trusted_local_unsandboxed` caveat remains material: it is not an OS
sandbox and it does not comprehensively observe effects outside the controlled
workspace.

## Exact proof task

Use `workbench_fixtures/proof.txt`, expected output `Expected Workbench proof line.\n`, and
the deterministic validation description `Exact expected output.` The fixture
worker proves the deterministic control-surface flow. A separately executed
Codex proof uses the same constrained task and records the native CLI
invocation, artifact, audit, verifier, and human disposition. Neither proof
establishes generalized Codex competence, semantic correctness, concurrency
safety, or production readiness.

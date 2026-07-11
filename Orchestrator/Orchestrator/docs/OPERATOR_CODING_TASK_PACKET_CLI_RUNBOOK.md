# Canonical Alpha Operator Coding Task Packet CLI Runbook

## Purpose and authority

The authoritative canonical-alpha operator route is:

~~~text
python -m orchestrator.operator_coding_task_packet_cli
~~~

This is an execution surface, not a read-only smoke command. Use it only when an
operator has deliberately selected a data root, a trusted local worker command,
and a bounded packet for an authorized execution.

**main.py** remains a legacy 49-command surface. It is not the canonical-alpha
entry point. Implicit **local_file** execution is retired from the canonical
packet path: a canonical execution requires an explicit **subprocess_worker**
and an explicit worker command.

The canonical lifecycle is:

~~~text
bounded structured packet
→ validation
→ explicit persisted execution authorization
→ task/run persistence
→ BaseProvider dispatch
→ trusted worker execution
→ structured result and artifact persistence
→ deterministic verification
→ human semantic disposition
→ persisted acceptance or rejection
→ read-only lifecycle reconciliation
~~~

This runbook does not select a provider or model.

## Command forms

The canonical execution command is:

~~~text
python -m orchestrator.operator_coding_task_packet_cli --packet-json <packet-path> --data-root <data-root> --trusted-worker-posture trusted_local_unsandboxed --worker-command <trusted-worker-command> <worker-argument>...
~~~

The **--worker-command** flag consumes the command and all remaining arguments,
so it must be last. The CLI does not shell-parse that value: it launches the
supplied argument list directly. Quote paths and arguments according to the
shell that constructs the list. The command receives one JSON object on standard
input and runs with the controlled per-run workspace as its current directory.

The only canonical read-only command form is:

~~~text
python -m orchestrator.operator_coding_task_packet_cli --reconcile --data-root <data-root>
~~~

It reads lifecycle records and prints reconciliation JSON; it does not launch a
worker. **--residue-guard** is a legacy repository-residue inspection surface,
not a canonical-alpha lifecycle command.

## Deliberate data-root selection

**--data-root** is required for canonical execution and reconciliation. Select a
dedicated, operator-controlled path for each isolated lifecycle or evidence set.
Do not assume repository-local persistence: the canonical path redirects its
durable stores to the supplied data root.

For an execution, the data root can contain these record areas:

- **state/**
- **runs/**
- **tasks/**
- **artifacts/**
- **verifier_results/**
- **execution_authorizations/**
- **worker_workspaces/**
- **acceptance_records/**
- **packet_operator_decision_records/**

Records written by the canonical path are schema-versioned JSON and are written
atomically. The selected data root must be suitable for this persistent state;
the worker safeguard rejects an existing data root that is a symlink or Windows
reparse point. A new data root is created as records and workspaces are written.
This isolation prevents canonical persistence from silently using the
repository's normal data location; it does not make the trusted worker an
OS-sandboxed process.

### Non-executing preparation and inspection

These examples prepare values and inspect an already selected data root; they
do not start a worker:

~~~powershell
$DataRoot = Join-Path $env:TEMP 'orchestrator-canonical-alpha-example-data'
$PacketPath = Join-Path $env:TEMP 'orchestrator-canonical-alpha-example-packet.json'
python -m orchestrator.operator_coding_task_packet_cli --reconcile --data-root $DataRoot
~~~

Reconciliation of an unused data root is a valid read-only inspection and may
report a healthy empty lifecycle. A healthy result means the records it found
are internally consistent; it is not semantic, security, or execution proof.

## Bounded packet and persisted authorization

The packet is a JSON object. It supplies the packet, run, and task identifiers;
title; declared output paths; success criteria; expected output; provider name;
and execution policy. For canonical execution, the material fields include:

~~~json
{
  "packet_id": "packet_example_001",
  "run_id": "run_example_001",
  "task_id": "task_example_001",
  "title": "Bounded canonical-alpha example",
  "files_in_scope": ["outputs/example.txt"],
  "success_criteria": ["Write the declared target."],
  "expected_output": "example output\n",
  "execution_policy": "filesystem_mutation",
  "provider_name": "subprocess_worker",
  "worker_trust_posture": "trusted_local_unsandboxed",
  "authorization_decision": "authorize_execution",
  "authorization_provenance": "operator-selected-example"
}
~~~

This JSON is a preparation example, not a command to execute. Identifiers and
declared paths must be valid; declared paths use relative forward-slash form.
The execution policy is **filesystem_mutation**. Do not add provider, model,
runtime, or platform request fields: the packet validator rejects them.

Validation and packet construction are not authorization. Before workspace
creation or worker launch, the runtime persists an execution-authorization
record under **execution_authorizations/**. It authorizes only when the packet
contains **authorization_decision: "authorize_execution"** and non-empty
**authorization_provenance**; the record binds the task ID, declared scope,
operator provenance, trust posture, timestamp, and constraints. A denied,
missing, or contradictory authorization blocks execution. The operator remains
the execution decision membrane.

## Trusted worker contract and controlled workspace

The only supported posture is:

~~~text
trusted_local_unsandboxed
~~~

The operator deliberately selects the local worker command. The canonical
provider seam is:

~~~text
providers.base.BaseProvider.execute(role, task, context)
~~~

The CLI constructs **SubprocessWorkerProvider** from **--worker-command**, which
implements that seam with provider name **subprocess_worker**. The provider
receives authorization, worker-security metadata, declared safe target paths,
and task context. It invokes the selected command with the controlled workspace
as its working directory and passes a JSON payload on standard input.

For each task/run pair, the runtime creates a unique workspace beneath:

~~~text
<data-root>/worker_workspaces/<run-id>__<task-id>/
~~~

Declared outputs are mapped below that workspace. The runtime rejects absolute,
backslash-form, ambiguous, or parent-traversal declared paths; checks workspace
and existing parent chains for symlink/reparse risks; checks expected parents
again immediately before launch; and inventories/audits workspace effects
afterward. A timeout attempts bounded descendant cleanup and records whether
cleanup was confirmed. The workspace audit detects effects within this controlled
workspace, including undeclared workspace mutation.

These are defense-in-depth controls for a trusted local worker. They are not OS
sandboxing. Effects outside the controlled workspace are not comprehensively
prevented or observed, and untrusted-worker execution is unsupported.

## Worker result contract and persisted records

After receiving the JSON payload, a successful worker must emit one JSON object
on standard output with at least:

~~~json
{
  "task_id": "task_example_001",
  "run_id": "run_example_001",
  "status": "success",
  "output": "example output\n",
  "target_path": "<the first allowed_paths value from the input payload>"
}
~~~

**target_path** must exactly equal the first safe allowed path supplied in the
input payload. Non-JSON output, a non-zero exit, a timeout, missing or
mismatched result fields, or an out-of-scope reported target fails the worker
result contract.

On the canonical path, task and run records are persisted before dispatch.
Execution produces an execution artifact; deterministic verification produces a
verifier result; and the records carry identifiers that link task, run,
authorization, artifact, verifier, worker-security metadata, and later human
disposition. Inspect the CLI JSON for **execution_provider**,
**final_task_status**, **execution_artifact_id**, **authorization**, and
**current_success_review**.

## Operator execution example — do not run as documentation validation

This is the source-accurate command shape for a separately authorized real
execution. It deliberately uses placeholders rather than selecting a provider,
model, or worker implementation. Do not run it merely to validate this runbook.

~~~powershell
python -m orchestrator.operator_coding_task_packet_cli --packet-json $PacketPath --data-root $DataRoot --trusted-worker-posture trusted_local_unsandboxed --worker-command <trusted-worker-command> <worker-argument-1> <worker-argument-2>
~~~

The CLI requires the packet's **worker_trust_posture**, if present, to match the
CLI posture. It also requires the packet's **provider_name** to be
**subprocess_worker**; an implicit or requested **local_file** path is not a
canonical execution.

## Deterministic verification and human semantic disposition

Deterministic verification occurs after worker execution and is persisted as a
verifier result. It is a bounded tripwire: it can check declared conditions
represented by the runtime, but does not prove semantic correctness,
architectural quality, task adequacy, provider competence, autonomous coding, or
production readiness.

Human semantic judgment is separate from deterministic verification. A packet
may include a **human_review** object, which the runtime processes only after it
has completed execution and current-success review:

~~~json
{
  "human_review": {
    "accepted": true,
    "operator_note": "Accepted after bounded human review.",
    "verification_caveat_acknowledged": true,
    "provider_caveat_acknowledged": true
  }
}
~~~

For an acceptance record, **accepted** must be true, the operator note and both
caveat acknowledgements are required, and the completed result must have passed
the deterministic review gate. The persisted acceptance links the task, run,
artifact, authorization, and verifier result. An execution-level CLI result with
**accepted: true** means the task execution completed; it is not by itself human
acceptance.

To persist a rejection for a completed reviewable result, include a
non-accepting review with an operator note:

~~~json
{
  "human_review": {
    "accepted": false,
    "operator_note": "Rejected after semantic inspection."
  }
}
~~~

The runtime records a rejected operator-decision record; rejection preserves the
decision and reason and does not automatically turn the task into product
failure. A later result-review operation outside this CLI does not make legacy
**main.py** the canonical lifecycle route.

## Read-only lifecycle reconciliation

Run reconciliation against the same data root after a lifecycle has produced
records:

~~~powershell
python -m orchestrator.operator_coding_task_packet_cli --reconcile --data-root $DataRoot
~~~

The reconciliation result contains **alpha_reconciliation**, **data_root**,
**findings**, and **healthy**. It reads task, run, authorization, artifact,
verifier, acceptance, and operator-decision records; checks JSON and schema
versions; detects incomplete in-progress work; validates task/run/artifact/
verifier/disposition identity linkage; checks authorization scope and identity
linkage; and checks persisted worker posture, workspace identity, audit, and
cleanup metadata. It is read-only.

An empty **findings** list (**healthy: true**) means the records examined are
structurally consistent. It does not prove semantic correctness, OS sandboxing,
safe execution of an untrusted worker, provider/model quality, or production
readiness.

## End-to-end operator sequence

1. Select a deliberate isolated **--data-root**; do not reuse one whose prior
   task IDs or workspace identities would collide.
2. Prepare a bounded packet with relative declared paths,
   **provider_name: "subprocess_worker"**, the required trust posture, and an
   explicit authorization decision and provenance.
3. Select a trusted local worker command that understands the JSON
   standard-input and structured-standard-output contract. Treat that selection
   as an operator decision, not a provider/model recommendation from runtime.
4. Under a separately authorized execution boundary, invoke the canonical CLI
   with **--packet-json**, **--data-root**,
   **--trusted-worker-posture trusted_local_unsandboxed**, and a final
   **--worker-command** argument list.
5. Inspect the structured result and persisted task, run, authorization,
   artifact, and verifier records under the selected data root.
6. Apply human semantic judgment. Include a valid **human_review** when an
   immediate acceptance or rejection record is intended; otherwise do not
   mistake execution completion for a persisted human disposition.
7. Run the read-only reconciliation command against that data root and inspect
   every finding before relying on the linked lifecycle state.

## Failure and stop conditions

Stop and inspect the structured CLI result rather than retrying blindly when
any of these occurs:

- packet file unreadable, malformed, or not a JSON object;
- unsupported CLI arguments, or missing **--data-root**, trust posture, or
  worker command;
- missing packet fields, invalid identifiers, unsafe declared paths, unsupported
  execution policy, **local_file**, or provider/model/runtime/platform request
  fields;
- missing, denied, or contradictory persisted authorization;
- unsupported or mismatched trust posture, provider identity, task identity, or
  authorized scope;
- unavailable, reused, unsafe, or changed workspace/output-parent state,
  including symlink or reparse risk;
- worker launch failure, timeout, unconfirmed descendant cleanup, non-zero exit,
  malformed result, target mismatch, or undeclared workspace effect;
- execution failure, failed deterministic verification, or human review that
  does not meet its acceptance/rejection prerequisites; or
- reconciliation findings such as invalid records, missing links, mismatched
  identifiers, incomplete cleanup metadata, or a completed task lacking human
  disposition.

Do not infer recovery behavior beyond the reported records and error codes.

## Explicit non-proofs

Canonical alpha does not prove:

- OS-level sandboxing;
- safe execution of untrusted workers;
- semantic correctness or architectural quality;
- autonomous coding competence;
- provider or model quality;
- concurrency safety;
- multi-user safety;
- production readiness;
- first-product-wedge selection; or
- product-market fit.

It also does not select a provider, model, or product wedge. This runbook does
not authorize a worker launch, provider/model/runtime execution, or production
workload; its real-execution example is descriptive only.

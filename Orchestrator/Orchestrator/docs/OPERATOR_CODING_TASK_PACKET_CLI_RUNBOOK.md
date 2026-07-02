# Operator Coding Task Packet CLI Runbook

## Purpose

This runbook gives an operator-facing command path for the Phase 275 packet
CLI:

`python -m orchestrator.operator_coding_task_packet_cli --packet-json <path>`

The packet CLI is an execution and persistence surface. A successful invocation
runs deterministic `local_file` behavior and may create repo-local durable
task, artifact, verifier, and output records. It is not a read-only repo smoke.
Run it only under an explicit persistence or mutation boundary where generated
repo-local files are expected, inspected, accepted, or cleaned under a later
explicit boundary.

## Command Syntax

```powershell
python -m orchestrator.operator_coding_task_packet_cli --packet-json <path>
```

The CLI accepts only `--packet-json <path>`.

Operator-pasted command batches for this runbook must not use `exit`,
especially not `exit 1`. For expected boundary failures, prefer accumulated
PASS/FAIL lines and natural script completion instead of `throw`.

## Minimal Packet

```json
{
  "execution_policy": "filesystem_mutation",
  "expected_output": "PHASE277 packet CLI golden smoke proof\n",
  "files_in_scope": [
    "outputs/phase277_golden_smoke.txt"
  ],
  "packet_id": "packet_phase277_golden_smoke",
  "provider_name": "local_file",
  "run_id": "run_phase277_golden_smoke",
  "success_criteria": [
    "Write the deterministic Phase 277 golden-smoke output.",
    "Return parseable JSON with local_file execution evidence and non-proofs."
  ],
  "task_id": "task_phase277_golden_smoke",
  "title": "Phase 277 packet CLI golden smoke"
}
```

## Persistence Posture

A successful packet CLI execution may persist repo-local generated files under:

- `outputs/`
- `data/tasks/`
- `data/artifacts/`
- `data/verifier_results/`

Deterministic `local_file` behavior is local filesystem behavior. It is not
model-backed coding, live provider generation, autonomous AI coding, or semantic
task adequacy proof.

Deterministic `local_file` behavior is not model-backed coding and is not
semantic task adequacy proof.

Because the packet writes files, a successful run can leave `git status` dirty.
Do not frame this command as a repo-read-only smoke. The operator should inspect
the generated paths and then accept them, leave them for a follow-up boundary,
or clean them only under a later explicit cleanup/delete boundary.

## PowerShell Execution And Persistence Pattern

From the product repo root, under an explicit persistence or mutation boundary:

```powershell
$StartedAt = Get-Date -Format o
$Stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
$Failures = New-Object System.Collections.Generic.List[string]
$RunStamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$RunDir = Join-Path $env:TEMP "orchestrator_phase277_packet_cli_$RunStamp"
$PacketPath = Join-Path $RunDir "packet.json"
$OutputPath = Join-Path $RunDir "cli-output.json"

New-Item -ItemType Directory -Force -Path $RunDir | Out-Null

@'
{
  "execution_policy": "filesystem_mutation",
  "expected_output": "PHASE277 packet CLI golden smoke proof\n",
  "files_in_scope": [
    "outputs/phase277_golden_smoke.txt"
  ],
  "packet_id": "packet_phase277_golden_smoke",
  "provider_name": "local_file",
  "run_id": "run_phase277_golden_smoke",
  "success_criteria": [
    "Write the deterministic Phase 277 golden-smoke output.",
    "Return parseable JSON with local_file execution evidence and non-proofs."
  ],
  "task_id": "task_phase277_golden_smoke",
  "title": "Phase 277 packet CLI golden smoke"
}
'@ | Set-Content -LiteralPath $PacketPath -Encoding UTF8

python -m orchestrator.operator_coding_task_packet_cli --packet-json $PacketPath |
  Tee-Object -FilePath $OutputPath

$CliExitCode = $LASTEXITCODE
if ($CliExitCode -ne 0) {
  $Failures.Add("CLI exit code was $CliExitCode")
}

try {
  $CliJson = Get-Content -LiteralPath $OutputPath -Raw | ConvertFrom-Json
  if ($CliJson.accepted -ne $true) { $Failures.Add("accepted was not true") }
  if ($CliJson.blocked -ne $false) { $Failures.Add("blocked was not false") }
  if ($CliJson.execution_provider -ne "local_file") {
    $Failures.Add("execution_provider was not local_file")
  }
  if ($CliJson.no_activity_flags.model_executed -ne $false) {
    $Failures.Add("model_executed was not false")
  }
  if ($CliJson.no_activity_flags.runtime_executed -ne $false) {
    $Failures.Add("runtime_executed was not false")
  }
  if ($CliJson.no_activity_flags.platform_invoked -ne $false) {
    $Failures.Add("platform_invoked was not false")
  }
} catch {
  $Failures.Add("CLI output was not parseable JSON: $($_.Exception.Message)")
}

$GeneratedRepoPaths = @(
  "outputs/phase277_golden_smoke.txt",
  "data/tasks/task_phase277_golden_smoke.json",
  "data/artifacts",
  "data/verifier_results"
)

$Stopwatch.Stop()
$FinishedAt = Get-Date -Format o

"StartedAt=$StartedAt"
"FinishedAt=$FinishedAt"
"ElapsedMs=$($Stopwatch.ElapsedMilliseconds)"
"CliExitCode=$CliExitCode"
"RunDir=$RunDir"
"PacketPath=$PacketPath"
"OutputPath=$OutputPath"
"GeneratedRepoPathsToInspect=$($GeneratedRepoPaths -join '; ')"

if ($Failures.Count -eq 0) {
  "PHASE277_PACKET_CLI_EXECUTION_PERSISTENCE_SMOKE=PASS"
} else {
  "PHASE277_PACKET_CLI_EXECUTION_PERSISTENCE_SMOKE=FAIL"
  $Failures | ForEach-Object { "Failure=$_" }
  "OperatorAction=inspect output JSON, generated repo-local files, and boundary authorization before retrying"
}
```

Keep the start timestamp, finish timestamp, elapsed time, CLI exit code,
visible CLI output, run directory path, and generated repo-local paths together
for any evidence-bearing script batch.

## Output Fields That Matter

For a successful local execution, inspect:

- `accepted`: should be `true`
- `blocked`: should be `false`
- `execution_provider`: should be `local_file`
- `final_task_status`: should be `completed`
- `execution_artifact_id`: should be non-empty
- `current_success_review`: should be present and reviewable
- `operator_response_surface`: should describe the response options
- `operator_next_action`: should list inspectable next actions
- `no_activity_flags`: should keep model, runtime, platform, provider, WSL,
  Ollama, OpenClaw, Hermes, Discord, installer, autonomous-coding, semantic,
  and production-readiness activity false
- `non_proofs`: should include the current non-proof caveats

## Operator Decision Record

After inspecting a completed packet CLI result and its current-success review,
an operator can record an explicit bounded decision with:

```text
python main.py packet-result-operator-decide <decision_input_json_path>
```

The input JSON must include `operator_decision` as `accepted` or `rejected`, a
valid `task_id`, and an `operator_note` or `reason`. `packet_id` may be supplied
when known. The command persists a local decision record and does not execute,
mutate, verify, call a provider, call a model, invoke a runtime, or claim
production readiness.

Acceptance records only the operator decision under stated caveats. It does not
prove semantic correctness, autonomous AI coding, model-backed generation, live
provider/model execution, runtime/platform behavior, or production readiness.
Rejection preserves the operator decision and reason without automatically
mutating the task into product failure.

The latest decision is surfaced in current-success readback under
`operator_decision_summary`.

## Expected Success Shape

The successful shape is deterministic parseable JSON with:

- `accepted=true`
- `blocked=false`
- `blocked_conditions=[]`
- `missing_requirements=[]`
- `execution_provider=local_file`
- `final_task_status=completed`
- a non-empty `execution_artifact_id`
- `no_activity_flags.model_executed=false`
- `no_activity_flags.runtime_executed=false`
- `no_activity_flags.platform_invoked=false`
- `no_activity_flags.live_provider_invoked=false`
- `non_proofs` containing `no_semantic_correctness_proof`,
  `no_live_provider_model_proof`, `no_runtime_platform_proof`,
  `no_autonomous_ai_coding_proof`, and `no_production_readiness_proof`

## Expected Blocked Or Error Shape

Blocked/error output is also deterministic parseable JSON. It should contain:

- `accepted=false`
- `blocked=true`
- one or more `blocked_conditions`
- optional `missing_requirements`
- `detail` when the CLI can safely explain the issue
- `no_activity_flags` preserving false activity flags
- `non_proofs` preserving the current caveats

Typical blocked/error causes include missing CLI arguments, unreadable packet
files, malformed JSON, JSON that is not an object, missing required packet
fields, unsupported provider names, requested model/runtime/platform fields,
unsafe declared file paths, or unsupported execution policy.

## Current Lockouts

This runbook does not authorize provider/model execution, runtime/platform
execution, WSL, Ollama, OpenClaw, Hermes, Discord, installer behavior,
service/API/UI work, scheduler/connector behavior, `general_answer` mutation,
cleanup/delete/archive behavior, or production-readiness claims.

## Non-Proofs

This runbook proves only a source/test/docs-backed description of the packet CLI
as an execution and persistence surface with deterministic `local_file`
behavior.

It does not prove semantic correctness, live provider/model execution,
runtime/platform behavior, autonomous AI coding, production readiness, service
or API or UI behavior, scheduler/reminder behavior, connector behavior,
`general_answer` resumption, or the full production patch workflow.

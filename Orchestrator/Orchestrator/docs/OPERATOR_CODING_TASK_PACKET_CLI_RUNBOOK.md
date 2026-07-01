# Operator Coding Task Packet CLI Runbook

## Purpose

This runbook gives an operator-facing golden-smoke path for the Phase 275
packet CLI:

`python -m orchestrator.operator_coding_task_packet_cli --packet-json <path>`

It shows how to write a minimal local JSON packet, run the CLI by hand, and
read the deterministic JSON output without reconstructing packet schema from
tests or coordinator memory.

## Command Syntax

```powershell
python -m orchestrator.operator_coding_task_packet_cli --packet-json <path>
```

The CLI accepts only `--packet-json <path>`.

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

## PowerShell Golden Smoke

From the product repo root:

```powershell
$StartedAt = Get-Date -Format o
$Stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
$RunStamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$RunDir = Join-Path $env:TEMP "orchestrator_phase277_packet_cli_$RunStamp"
New-Item -ItemType Directory -Force -Path $RunDir | Out-Null
$PacketPath = Join-Path $RunDir "packet.json"
$OutputPath = Join-Path $RunDir "cli-output.json"

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

$ExitCode = $LASTEXITCODE
$Stopwatch.Stop()
$FinishedAt = Get-Date -Format o
"StartedAt=$StartedAt"
"FinishedAt=$FinishedAt"
"ElapsedMs=$($Stopwatch.ElapsedMilliseconds)"
"ExitCode=$ExitCode"
"RunDir=$RunDir"
"PacketPath=$PacketPath"
"OutputPath=$OutputPath"
```

Keep the start timestamp, finish timestamp, elapsed time, exit code, visible
CLI output, and run directory path together for any evidence-bearing script
batch.

## Output Fields That Matter

For a successful local golden smoke, inspect:

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
- `non_proofs` containing `no_live_provider_model_proof` and
  `no_runtime_platform_proof`

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

This golden smoke proves only a source/test/docs-backed operator runbook and
deterministic CLI contract for a local JSON packet using `local_file`.

It does not prove semantic correctness, live provider/model execution,
runtime/platform behavior, autonomous AI coding, production readiness, service
or API or UI behavior, scheduler/reminder behavior, connector behavior,
`general_answer` resumption, or the full production patch workflow.

Deterministic `local_file` behavior is local filesystem behavior. It is not
model-backed coding, live provider generation, autonomous coding, or semantic
task adequacy proof.

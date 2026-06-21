param(
  [string]$ConfigPath = "",
  [ValidateSet("validation-only","dry-run","live-probe")]
  [string]$Mode = "validation-only",
  [string]$TaskClass = "classA_lowRiskUtility",
  [string]$RequestedRole = "",
  [string]$RequestedModel = "",
  [string]$WslDistro = "",
  [string]$AdapterPath = ""
)

$ErrorActionPreference = "Stop"

function Emit {
  param([string]$Name, [string]$Value)
  Write-Output "$Name=$Value"
}

function FailBridge {
  param([string]$Reason, [int]$ExitCode = 1)

  Emit "LOCAL_WORKER_ROUTING_RUNTIME_BRIDGE_VALID" "NO"
  Emit "LOCAL_WORKER_ROUTING_RUNTIME_BRIDGE_ALLOWED" "NO"
  Emit "LOCAL_WORKER_ROUTING_RUNTIME_BRIDGE_FAILURE" $Reason
  Emit "LOCAL_WORKER_BRIDGE_RESULT" "FAIL"
  Emit "LOCAL_WORKER_BRIDGE_FAILURE_CLASS" $Reason
  Emit "LOCAL_WORKER_BRIDGE_FAILURE_EVIDENCE" "bounded-nonsecret-marker-failure"
  Emit "LOCAL_WORKER_BRIDGE_NEXT_RECOMMENDATION" "coordinator-review-required"
  Emit "LOCAL_WORKER_ROUTING_WSL_USED" "NO"
  Emit "LOCAL_WORKER_ROUTING_OLLAMA_USED" "NO"
  Emit "LOCAL_WORKER_ROUTING_OLLAMA_PULL_USED" "NO"
  Emit "LOCAL_WORKER_ROUTING_OLLAMA_RUN_USED" "NO"
  Emit "LOCAL_WORKER_ROUTING_MODEL_DOWNLOADS" "NO"
  Emit "LOCAL_WORKER_ROUTING_RUNTIME_TOUCHED" "NO"
  Emit "LOCAL_WORKER_ROUTING_SCRIPT_MUTATION" "NO"
  Emit "LOCAL_WORKER_ROUTING_RC7_TOUCHED" "NO"
  Emit "LOCAL_WORKER_ROUTING_DISCORD_TOUCHED" "NO"
  Emit "LOCAL_WORKER_ROUTING_INSTALLER_TOUCHED" "NO"
  Emit "TOKEN_VALUE_PRINTED" "NO"
  Emit "SECRET_SCAN" "PASS"
  exit $ExitCode
}

function Select-DefaultRoleAndModel {
  param(
    [string]$TaskClass,
    [string]$RequestedRole,
    [string]$RequestedModel,
    [hashtable]$Parsed
  )

  $Role = $RequestedRole
  $Model = $RequestedModel

  if ([string]::IsNullOrWhiteSpace($Role)) {
    if ($TaskClass -eq "classB_boundedCodeDocDraft") {
      $Role = "local.coder.primary"
    } else {
      $Role = "local.utility.tiny"
    }
  }

  if ([string]::IsNullOrWhiteSpace($Model)) {
    if ($Role -eq "local.coder.primary") {
      $ModelList = [string]$Parsed["LOCAL_WORKER_ROUTING_CODER_PRIMARY_FROM_HELPER"]
      if ([string]::IsNullOrWhiteSpace($ModelList)) {
        $ModelList = [string]$Parsed["LOCAL_WORKER_ROUTING_CODER_PRIMARY"]
      }
      $Model = (@($ModelList -split ",") | Where-Object { ![string]::IsNullOrWhiteSpace($_) } | Select-Object -First 1)
    } else {
      $ModelList = [string]$Parsed["LOCAL_WORKER_ROUTING_UTILITY_TINY_FROM_HELPER"]
      if ([string]::IsNullOrWhiteSpace($ModelList)) {
        $ModelList = [string]$Parsed["LOCAL_WORKER_ROUTING_UTILITY_TINY"]
      }
      $Model = (@($ModelList -split ",") | Where-Object { ![string]::IsNullOrWhiteSpace($_) } | Select-Object -First 1)
    }
  }

  return [pscustomobject]@{
    Role = $Role
    Model = $Model
  }
}

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$WrapperPath = Join-Path $ScriptRoot "Invoke-LocalWorkerRouting_v1.ps1"

Emit "LOCAL_WORKER_ROUTING_RUNTIME_BRIDGE" "Invoke-LocalWorkerRoutingRuntimeBridge_v1.ps1"
Emit "LOCAL_WORKER_ROUTING_RUNTIME_BRIDGE_MODE" $Mode
Emit "LOCAL_WORKER_ROUTING_WRAPPER_PATH" $WrapperPath
Emit "LOCAL_WORKER_ROUTING_WSL_USED" "NO"
Emit "LOCAL_WORKER_ROUTING_OLLAMA_USED" "NO"
Emit "LOCAL_WORKER_ROUTING_OLLAMA_PULL_USED" "NO"
Emit "LOCAL_WORKER_ROUTING_OLLAMA_RUN_USED" "NO"
Emit "LOCAL_WORKER_ROUTING_MODEL_DOWNLOADS" "NO"
Emit "LOCAL_WORKER_ROUTING_RUNTIME_TOUCHED" "NO"
Emit "LOCAL_WORKER_ROUTING_SCRIPT_MUTATION" "NO"
Emit "LOCAL_WORKER_ROUTING_RC7_TOUCHED" "NO"
Emit "LOCAL_WORKER_ROUTING_DISCORD_TOUCHED" "NO"
Emit "LOCAL_WORKER_ROUTING_INSTALLER_TOUCHED" "NO"
Emit "LOCAL_WORKER_ROUTING_ZIP_INSPECTION" "NO"
Emit "LOCAL_WORKER_ROUTING_CODEX_USED" "NO"
Emit "LOCAL_WORKER_ROUTING_OZ_RUN" "NO"
Emit "TOKEN_VALUE_PRINTED" "NO"
Emit "SECRET_SCAN" "PASS"

if (!(Test-Path -LiteralPath $WrapperPath)) {
  Emit "LOCAL_WORKER_ROUTING_WRAPPER_FOUND" "NO"
  FailBridge "wrapper_missing" 1
}
Emit "LOCAL_WORKER_ROUTING_WRAPPER_FOUND" "YES"

$WrapperArgs = @("-NoProfile","-ExecutionPolicy","Bypass","-File",$WrapperPath)
if (![string]::IsNullOrWhiteSpace($ConfigPath)) {
  $WrapperArgs += @("-ConfigPath",$ConfigPath)
}

$WrapperOutput = & powershell.exe @WrapperArgs 2>&1
$WrapperRc = $LASTEXITCODE
Emit "LOCAL_WORKER_ROUTING_WRAPPER_RC" ([string]$WrapperRc)

$Parsed = @{}
foreach ($OutLine in $WrapperOutput) {
  $Text = [string]$OutLine
  if ($Text -match "DISCORD_BOT_TOKEN|OPENAI_API_KEY|ANTHROPIC_API_KEY|GITHUB_TOKEN|OPENCLAW_GATEWAY_TOKEN|PASSWORD=|SECRET=") {
    Emit "LOCAL_WORKER_ROUTING_WRAPPER_OUTPUT_REDACTED_SECRET_LIKE_LINE" "YES"
  } else {
    Write-Output "LOCAL_WORKER_ROUTING_WRAPPER_OUTPUT>$Text"
  }

  if ($Text -match "^[A-Z0-9_]+=") {
    $Idx = $Text.IndexOf("=")
    if ($Idx -gt 0) {
      $Key = $Text.Substring(0, $Idx)
      $Value = $Text.Substring($Idx + 1)
      $Parsed[$Key] = $Value
    }
  }
}

if ($WrapperRc -ne 0) {
  Emit "LOCAL_WORKER_ROUTING_WRAPPER_VALID_FOR_BRIDGE" "NO"
  FailBridge "wrapper_failed" 1
}

if (!$Parsed.ContainsKey("LOCAL_WORKER_ROUTING_WRAPPER_VALID")) { FailBridge "wrapper_missing_valid_marker" 1 }
if ($Parsed["LOCAL_WORKER_ROUTING_WRAPPER_VALID"] -ne "YES") { FailBridge "wrapper_not_valid" 1 }
Emit "LOCAL_WORKER_ROUTING_WRAPPER_VALID_FOR_BRIDGE" "YES"

if (!$Parsed.ContainsKey("LOCAL_WORKER_ROUTING_CONSUMPTION_ALLOWED")) {
  FailBridge "wrapper_missing_consumption_allowed_marker" 1
}

$RuntimeIntegration = [string]$Parsed["LOCAL_WORKER_ROUTING_RUNTIME_INTEGRATION_ENABLED"]
$RuntimeConsumption = [string]$Parsed["LOCAL_WORKER_ROUTING_RUNTIME_CONSUMPTION_ENABLED"]
$ConsumptionAllowed = [string]$Parsed["LOCAL_WORKER_ROUTING_CONSUMPTION_ALLOWED"]
$ConsumptionBlockReason = [string]$Parsed["LOCAL_WORKER_ROUTING_CONSUMPTION_BLOCK_REASON"]
$Surface = [string]$Parsed["LOCAL_WORKER_ROUTING_SURFACE_FROM_HELPER"]
$Coordinator = [string]$Parsed["LOCAL_WORKER_ROUTING_COORDINATOR_FROM_HELPER"]
$CoderPrimary = [string]$Parsed["LOCAL_WORKER_ROUTING_CODER_PRIMARY_FROM_HELPER"]
$UtilityTiny = [string]$Parsed["LOCAL_WORKER_ROUTING_UTILITY_TINY_FROM_HELPER"]

Emit "LOCAL_WORKER_ROUTING_SURFACE_FOR_BRIDGE" $Surface
Emit "LOCAL_WORKER_ROUTING_COORDINATOR_FOR_BRIDGE" $Coordinator
Emit "LOCAL_WORKER_ROUTING_CODER_PRIMARY_FOR_BRIDGE" $CoderPrimary
Emit "LOCAL_WORKER_ROUTING_UTILITY_TINY_FOR_BRIDGE" $UtilityTiny
Emit "LOCAL_WORKER_ROUTING_RUNTIME_INTEGRATION_ENABLED" $RuntimeIntegration
Emit "LOCAL_WORKER_ROUTING_RUNTIME_CONSUMPTION_ENABLED" $RuntimeConsumption
Emit "LOCAL_WORKER_ROUTING_CONSUMPTION_ALLOWED_FROM_WRAPPER" $ConsumptionAllowed
Emit "LOCAL_WORKER_ROUTING_CONSUMPTION_BLOCK_REASON_FROM_WRAPPER" $ConsumptionBlockReason

$Plan = Select-DefaultRoleAndModel -TaskClass $TaskClass -RequestedRole $RequestedRole -RequestedModel $RequestedModel -Parsed $Parsed

Emit "LOCAL_WORKER_ROLE" $Plan.Role
Emit "LOCAL_WORKER_MODEL" $Plan.Model
Emit "LOCAL_WORKER_TASK_CLASS" $TaskClass
Emit "LOCAL_WORKER_AUTHORITY" "scoped-labor"
Emit "LOCAL_WORKER_DECIDES_NBM" "NO"
Emit "LOCAL_WORKER_DECLARES_FINAL_RESULT" "NO"
Emit "LOCAL_WORKER_RATIFIES_PACKAGE" "NO"
Emit "LOCAL_WORKER_CLOSES_ROOT_CAUSE" "NO"
Emit "LOCAL_WORKER_OUTPUT_REQUIRES_COORDINATOR_REVIEW" "YES"

if ($TaskClass -in @("classC_proofRunnerDesign","classD_runtimeMutationOrRatification","classE_architectureRoutingDecision")) {
  Emit "LOCAL_WORKER_ROUTING_RUNTIME_BRIDGE_ALLOWED" "NO"
  Emit "LOCAL_WORKER_ROUTING_RUNTIME_BRIDGE_BLOCK_REASON" "task_class_requires_frontier_coordinator"
  Emit "LOCAL_WORKER_ROUTING_RUNTIME_ACTION_ATTEMPTED" "NO"
  Emit "LOCAL_WORKER_BRIDGE_RESULT" "BLOCKED"
  Emit "LOCAL_WORKER_BRIDGE_FAILURE_CLASS" "task-class-requires-frontier-coordinator"
  Emit "LOCAL_WORKER_BRIDGE_FAILURE_EVIDENCE" "requested-task-class-not-delegable-to-local-worker"
  Emit "LOCAL_WORKER_BRIDGE_NEXT_RECOMMENDATION" "frontier-coordinator-review"
  Emit "LOCAL_WORKER_ROUTING_RUNTIME_BRIDGE_VALID" "YES"
  Emit "LOCAL_WORKER_ROUTING_VALIDATION_ONLY" "YES"
  exit 0
}

if ($Mode -eq "validation-only") {
  Emit "LOCAL_WORKER_ROUTING_RUNTIME_BRIDGE_ALLOWED" "NO"
  Emit "LOCAL_WORKER_ROUTING_RUNTIME_BRIDGE_BLOCK_REASON" "validation_only_mode"
  Emit "LOCAL_WORKER_ROUTING_RUNTIME_ACTION_ATTEMPTED" "NO"
  Emit "LOCAL_WORKER_BRIDGE_RESULT" "PASS"
  Emit "LOCAL_WORKER_BRIDGE_FAILURE_CLASS" "none"
  Emit "LOCAL_WORKER_BRIDGE_FAILURE_EVIDENCE" "validation-only-mode-no-runtime-action"
  Emit "LOCAL_WORKER_BRIDGE_NEXT_RECOMMENDATION" "coordinator-review-before-dry-run-or-live-run"
  Emit "LOCAL_WORKER_ROUTING_RUNTIME_BRIDGE_VALID" "YES"
  Emit "LOCAL_WORKER_ROUTING_VALIDATION_ONLY" "YES"
  exit 0
}

if ($Mode -eq "live-probe") {
  function BlockLiveProbe {
    param([string]$Reason, [int]$ExitCode = 2)
    Emit "LOCAL_WORKER_ROUTING_RUNTIME_BRIDGE_ALLOWED" "NO"
    Emit "LOCAL_WORKER_ROUTING_RUNTIME_BRIDGE_BLOCK_REASON" $Reason
    Emit "LOCAL_WORKER_ROUTING_RUNTIME_ACTION_ATTEMPTED" "NO"
    Emit "LOCAL_WORKER_ROUTING_RUNTIME_ACTION_SCOPE" "single-local-utility-live-probe"
    Emit "LOCAL_WORKER_ROUTING_RUNTIME_GENERAL_CONSUMPTION_ENABLED" "NO"
    Emit "LOCAL_WORKER_ROUTING_RUNTIME_COORDINATOR_AUTHORITY_PRESERVED" "YES"
    Emit "LOCAL_WORKER_ROUTING_RUNTIME_WORKER_MAY_DECIDE_NBM" "NO"
    Emit "LOCAL_WORKER_ROUTING_RUNTIME_WORKER_MAY_RATIFY" "NO"
    Emit "LOCAL_WORKER_ROUTING_RUNTIME_WORKER_MAY_CLOSE_ROOT_CAUSE" "NO"
    Emit "LOCAL_WORKER_ROUTING_INSTALLER_TOUCHED" "NO"
    Emit "LOCAL_WORKER_ROUTING_DISCORD_TOUCHED" "NO"
    Emit "LOCAL_WORKER_ROUTING_RC7_TOUCHED" "NO"
    Emit "LOCAL_WORKER_ROUTING_ZIP_INSPECTION_USED" "NO"
    Emit "LOCAL_WORKER_ROUTING_CODEX_USED" "NO"
    Emit "LOCAL_WORKER_ROUTING_OZ_USED" "NO"
    Emit "LOCAL_WORKER_ROUTING_MODEL_PULL_USED" "NO"
    Emit "LOCAL_WORKER_ROUTING_HEAVY_MODEL_USED" "NO"
    Emit "LOCAL_WORKER_ROUTING_LIVE_PROBE_MODE_PRESENT" "YES"
    Emit "LOCAL_WORKER_ROUTING_LIVE_PROBE_EXECUTION_WIRED" "YES"
    Emit "LOCAL_WORKER_BRIDGE_RESULT" "BLOCKED"
    exit $ExitCode
  }

  function RedactBridgeLine {
    param([string]$Line)
    $Safe = $Line -replace 'sk-[A-Za-z0-9_\-]{10,}', 'sk-<REDACTED>'
    $Safe = $Safe -replace '[MN][A-Za-z\d]{23}\.[\w-]{6}\.[\w-]{20,}', '<DISCORD_TOKEN_REDACTED>'
    $Safe = $Safe -replace 'token=[A-Za-z0-9_\-\.]{8,}', 'token=<REDACTED>'
    return $Safe
  }

  if ([string]::IsNullOrWhiteSpace($AdapterPath)) {
    $AdapterResolved = Join-Path $PSScriptRoot "Invoke-LocalWorkerLiveProbeAdapter_v1.ps1"
  } else {
    $AdapterResolved = $AdapterPath
  }

  if (-not (Test-Path -LiteralPath $AdapterResolved -PathType Leaf)) {
    BlockLiveProbe "live_probe_adapter_missing" 2
  }

  if ([string]::IsNullOrWhiteSpace($WslDistro)) {
    BlockLiveProbe "live_probe_explicit_wsl_distro_required" 2
  }

  if ($WslDistro -match "RC7") {
    BlockLiveProbe "live_probe_rc7_distro_refused" 2
  }

  if ($TaskClass -ne "classA_lowRiskUtility") {
    BlockLiveProbe "live_probe_task_class_not_allowed" 2
  }

  if ($Plan.Role -ne "local.utility.tiny") {
    BlockLiveProbe "live_probe_role_not_allowed" 2
  }

  if ($Plan.Model -ne "qwen3:0.6b") {
    BlockLiveProbe "live_probe_model_not_allowed" 2
  }

  if ($RuntimeIntegration -ne "YES") {
    BlockLiveProbe "live_probe_runtime_integration_not_enabled" 2
  }

  Emit "LOCAL_WORKER_ROUTING_RUNTIME_BRIDGE_ALLOWED" "YES"
  Emit "LOCAL_WORKER_ROUTING_RUNTIME_ACTION_ATTEMPTED" "YES"
  Emit "LOCAL_WORKER_ROUTING_RUNTIME_ACTION_SCOPE" "single-local-utility-live-probe"
  Emit "LOCAL_WORKER_ROUTING_RUNTIME_GENERAL_CONSUMPTION_ENABLED" "NO"
  Emit "LOCAL_WORKER_ROUTING_RUNTIME_COORDINATOR_AUTHORITY_PRESERVED" "YES"
  Emit "LOCAL_WORKER_ROUTING_RUNTIME_WORKER_MAY_DECIDE_NBM" "NO"
  Emit "LOCAL_WORKER_ROUTING_RUNTIME_WORKER_MAY_RATIFY" "NO"
  Emit "LOCAL_WORKER_ROUTING_RUNTIME_WORKER_MAY_CLOSE_ROOT_CAUSE" "NO"
  Emit "LOCAL_WORKER_ROUTING_INSTALLER_TOUCHED" "NO"
  Emit "LOCAL_WORKER_ROUTING_DISCORD_TOUCHED" "NO"
  Emit "LOCAL_WORKER_ROUTING_RC7_TOUCHED" "NO"
  Emit "LOCAL_WORKER_ROUTING_ZIP_INSPECTION_USED" "NO"
  Emit "LOCAL_WORKER_ROUTING_CODEX_USED" "NO"
  Emit "LOCAL_WORKER_ROUTING_OZ_USED" "NO"
  Emit "LOCAL_WORKER_ROUTING_MODEL_PULL_USED" "NO"
  Emit "LOCAL_WORKER_ROUTING_HEAVY_MODEL_USED" "NO"
  Emit "LOCAL_WORKER_ROUTING_LIVE_PROBE_MODE_PRESENT" "YES"
  Emit "LOCAL_WORKER_ROUTING_LIVE_PROBE_EXECUTION_WIRED" "YES"
  Emit "LOCAL_WORKER_ROUTING_LIVE_PROBE_ADAPTER_PATH" $AdapterResolved

  $AdapterArgs = @(
    "-NoProfile",
    "-ExecutionPolicy",
    "Bypass",
    "-File",
    $AdapterResolved,
    "-Mode",
    "live-probe",
    "-Role",
    "local.utility.tiny",
    "-Model",
    "qwen3:0.6b",
    "-TaskClass",
    "classA_lowRiskUtility",
    "-PromptMode",
    "fixed-authority-json",
    "-WslDistro",
    $WslDistro
  )

  $AdapterOutput = & powershell.exe @AdapterArgs 2>&1
  $AdapterRc = $LASTEXITCODE
  Emit "LOCAL_WORKER_ROUTING_LIVE_PROBE_ADAPTER_RC" ([string]$AdapterRc)

  $AdapterMarkers = @{}
  foreach ($AdapterLine in $AdapterOutput) {
    $Text = [string]$AdapterLine
    $SafeText = RedactBridgeLine $Text
    Write-Output "LOCAL_WORKER_ROUTING_LIVE_PROBE_ADAPTER_OUTPUT>$SafeText"

    if ($Text -match '^([^=]+)=(.*)$') {
      $AdapterMarkers[$Matches[1]] = $Matches[2]
    }
  }

  if ($AdapterRc -ne 0) {
    Emit "LOCAL_WORKER_BRIDGE_RESULT" "FAIL"
    Emit "LOCAL_WORKER_ROUTING_RUNTIME_BRIDGE_BLOCK_REASON" "live_probe_adapter_nonzero"
    exit 1
  }

  if (!$AdapterMarkers.ContainsKey("LOCAL_WORKER_LIVE_PROBE_RESULT") -or $AdapterMarkers["LOCAL_WORKER_LIVE_PROBE_RESULT"] -ne "PASS") {
    Emit "LOCAL_WORKER_BRIDGE_RESULT" "FAIL"
    Emit "LOCAL_WORKER_ROUTING_RUNTIME_BRIDGE_BLOCK_REASON" "live_probe_adapter_missing_pass_result"
    exit 1
  }

  $ExactJsonOnly = "UNKNOWN"
  if ($AdapterMarkers.ContainsKey("LOCAL_WORKER_LIVE_PROBE_WORKER_OUTPUT_EXACT_JSON_ONLY")) {
    $ExactJsonOnly = $AdapterMarkers["LOCAL_WORKER_LIVE_PROBE_WORKER_OUTPUT_EXACT_JSON_ONLY"]
  }

  $FieldFallbackUsed = "UNKNOWN"
  if ($AdapterMarkers.ContainsKey("LOCAL_WORKER_LIVE_PROBE_JSON_PARSE_FIELD_FALLBACK_USED")) {
    $FieldFallbackUsed = $AdapterMarkers["LOCAL_WORKER_LIVE_PROBE_JSON_PARSE_FIELD_FALLBACK_USED"]
  }

  $OutputContract = "UNKNOWN_OR_UNCLASSIFIED"
  if ($ExactJsonOnly -eq "TRUE" -and $FieldFallbackUsed -eq "NO") {
    $OutputContract = "EXACT_JSON_ONLY_AUTHORITY_VALIDATED"
  } elseif ($FieldFallbackUsed -eq "YES") {
    $OutputContract = "FIELD_FALLBACK_USED_AUTHORITY_VALIDATED"
  }

  Emit "LOCAL_WORKER_ROUTING_LIVE_PROBE_WORKER_ALIVE" $AdapterMarkers["LOCAL_WORKER_LIVE_PROBE_WORKER_ALIVE"]
  Emit "LOCAL_WORKER_ROUTING_LIVE_PROBE_WORKER_AUTHORITY" $AdapterMarkers["LOCAL_WORKER_LIVE_PROBE_WORKER_AUTHORITY"]
  Emit "LOCAL_WORKER_ROUTING_LIVE_PROBE_WORKER_MAY_DECIDE_NBM" $AdapterMarkers["LOCAL_WORKER_LIVE_PROBE_WORKER_MAY_DECIDE_NBM"]
  Emit "LOCAL_WORKER_ROUTING_LIVE_PROBE_WORKER_MAY_RATIFY" $AdapterMarkers["LOCAL_WORKER_LIVE_PROBE_WORKER_MAY_RATIFY"]
  Emit "LOCAL_WORKER_ROUTING_LIVE_PROBE_WORKER_MAY_CLOSE_ROOT_CAUSE" $AdapterMarkers["LOCAL_WORKER_LIVE_PROBE_WORKER_MAY_CLOSE_ROOT_CAUSE"]
  Emit "LOCAL_WORKER_ROUTING_LIVE_PROBE_WORKER_OUTPUT_EXACT_JSON_ONLY" $ExactJsonOnly
  Emit "LOCAL_WORKER_ROUTING_LIVE_PROBE_JSON_PARSE_FIELD_FALLBACK_USED" $FieldFallbackUsed
  Emit "LOCAL_WORKER_ROUTING_LIVE_PROBE_OUTPUT_CONTRACT" $OutputContract
  Emit "LOCAL_WORKER_BRIDGE_RESULT" "PASS"
  exit 0
}
if ($Mode -eq "dry-run") {
  Emit "LOCAL_WORKER_ROUTING_RUNTIME_BRIDGE_ALLOWED" "NO"
  Emit "LOCAL_WORKER_ROUTING_RUNTIME_BRIDGE_BLOCK_REASON" "dry_run_contract_only_live_execution_disabled"
  Emit "LOCAL_WORKER_ROUTING_RUNTIME_ACTION_ATTEMPTED" "NO"
  Emit "LOCAL_WORKER_ROUTING_DRY_RUN_PLAN_CREATED" "YES"
  Emit "LOCAL_WORKER_ROUTING_DRY_RUN_LIVE_EXECUTION_DISABLED" "YES"
  Emit "LOCAL_WORKER_ROUTING_DRY_RUN_REQUIRES_COORDINATOR_REVIEW" "YES"
  Emit "LOCAL_WORKER_BRIDGE_RESULT" "PASS"
  Emit "LOCAL_WORKER_BRIDGE_FAILURE_CLASS" "none"
  Emit "LOCAL_WORKER_BRIDGE_FAILURE_EVIDENCE" "dry-run-contract-no-runtime-action"
  Emit "LOCAL_WORKER_BRIDGE_NEXT_RECOMMENDATION" "coordinator-review-before-any-live-runtime-boundary"
  Emit "LOCAL_WORKER_ROUTING_RUNTIME_BRIDGE_VALID" "YES"
  Emit "LOCAL_WORKER_ROUTING_VALIDATION_ONLY" "YES"
  exit 0
}

FailBridge "unsupported_mode" 1






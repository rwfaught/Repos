param(
  [string]$ConfigPath = "",
  [ValidateSet("classA_lowRiskUtility","classB_boundedCodeDocDraft","classC_proofRunnerDesign","classD_runtimeMutationOrRatification","classE_architectureRoutingDecision")]
  [string]$TaskClass = "classA_lowRiskUtility"
)

$ErrorActionPreference = "Stop"

function Emit {
  param([string]$Name, [string]$Value)
  Write-Output "$Name=$Value"
}

function FailWrapper {
  param([string]$Reason, [int]$ExitCode = 1)
  Emit "LOCAL_WORKER_ROUTING_WRAPPER_VALID" "NO"
  Emit "LOCAL_WORKER_ROUTING_CONSUMPTION_ALLOWED" "NO"
  Emit "LOCAL_WORKER_ROUTING_WRAPPER_FAILURE" $Reason
  Emit "LOCAL_WORKER_ROUTING_WSL_USED" "NO"
  Emit "LOCAL_WORKER_ROUTING_OLLAMA_USED" "NO"
  Emit "LOCAL_WORKER_ROUTING_OLLAMA_PULL_USED" "NO"
  Emit "LOCAL_WORKER_ROUTING_OLLAMA_RUN_USED" "NO"
  Emit "LOCAL_WORKER_ROUTING_MODEL_DOWNLOADS" "NO"
  Emit "LOCAL_WORKER_ROUTING_RUNTIME_TOUCHED" "NO"
  Emit "LOCAL_WORKER_ROUTING_SCRIPT_MUTATION" "NO"
  Emit "LOCAL_WORKER_ROUTING_RC7_TOUCHED" "NO"
  exit $ExitCode
}

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$HelperPath = Join-Path $ScriptRoot "Get-LocalWorkerRoutingConfig_v1.ps1"

Emit "LOCAL_WORKER_ROUTING_WRAPPER" "Invoke-LocalWorkerRouting_v1.ps1"
Emit "LOCAL_WORKER_ROUTING_HELPER_PATH" $HelperPath
Emit "LOCAL_WORKER_ROUTING_TASK_CLASS" $TaskClass
Emit "LOCAL_WORKER_ROUTING_WSL_USED" "NO"
Emit "LOCAL_WORKER_ROUTING_OLLAMA_USED" "NO"
Emit "LOCAL_WORKER_ROUTING_OLLAMA_PULL_USED" "NO"
Emit "LOCAL_WORKER_ROUTING_OLLAMA_RUN_USED" "NO"
Emit "LOCAL_WORKER_ROUTING_MODEL_DOWNLOADS" "NO"
Emit "LOCAL_WORKER_ROUTING_RUNTIME_TOUCHED" "NO"
Emit "LOCAL_WORKER_ROUTING_SCRIPT_MUTATION" "NO"
Emit "LOCAL_WORKER_ROUTING_RC7_TOUCHED" "NO"

if (!(Test-Path -LiteralPath $HelperPath)) {
  Emit "LOCAL_WORKER_ROUTING_HELPER_FOUND" "NO"
  FailWrapper "helper_missing" 1
}
Emit "LOCAL_WORKER_ROUTING_HELPER_FOUND" "YES"

$HelperArgs = @("-NoProfile","-ExecutionPolicy","Bypass","-File",$HelperPath)
if (![string]::IsNullOrWhiteSpace($ConfigPath)) {
  $HelperArgs += @("-ConfigPath",$ConfigPath)
}

$HelperOutput = & powershell.exe @HelperArgs 2>&1
$HelperRc = $LASTEXITCODE
Emit "LOCAL_WORKER_ROUTING_HELPER_RC" ([string]$HelperRc)

$Parsed = @{}
foreach ($OutLine in $HelperOutput) {
  $Text = [string]$OutLine
  if ($Text -match "DISCORD_BOT_TOKEN|OPENAI_API_KEY|ANTHROPIC_API_KEY|GITHUB_TOKEN|PASSWORD=|SECRET=") {
    Emit "LOCAL_WORKER_ROUTING_HELPER_OUTPUT_REDACTED_SECRET_LIKE_LINE" "YES"
  } else {
    Write-Output "LOCAL_WORKER_ROUTING_HELPER_OUTPUT>$Text"
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

if ($HelperRc -ne 0) {
  Emit "LOCAL_WORKER_ROUTING_HELPER_VALID" "NO"
  FailWrapper "helper_failed" 1
}

if (!$Parsed.ContainsKey("LOCAL_WORKER_ROUTING_CONFIG_VALID")) { FailWrapper "helper_missing_config_valid_marker" 1 }
if ($Parsed["LOCAL_WORKER_ROUTING_CONFIG_VALID"] -ne "YES") { FailWrapper "helper_config_not_valid" 1 }
Emit "LOCAL_WORKER_ROUTING_HELPER_VALID" "YES"

$RuntimeIntegration = $Parsed["LOCAL_WORKER_ROUTING_RUNTIME_INTEGRATION_ENABLED"]
$RuntimeConsumption = $Parsed["LOCAL_WORKER_ROUTING_RUNTIME_CONSUMPTION_ENABLED"]
$Surface = $Parsed["LOCAL_WORKER_ROUTING_SURFACE"]
$Coordinator = $Parsed["LOCAL_WORKER_ROUTING_COORDINATOR"]
$CoderPrimary = $Parsed["LOCAL_WORKER_ROUTING_CODER_PRIMARY"]
$UtilityTiny = $Parsed["LOCAL_WORKER_ROUTING_UTILITY_TINY"]

$Decision = switch ($TaskClass) {
  "classA_lowRiskUtility" { $Parsed["LOCAL_WORKER_ROUTING_CLASS_A"] }
  "classB_boundedCodeDocDraft" { $Parsed["LOCAL_WORKER_ROUTING_CLASS_B"] }
  "classC_proofRunnerDesign" { $Parsed["LOCAL_WORKER_ROUTING_CLASS_C"] }
  "classD_runtimeMutationOrRatification" { $Parsed["LOCAL_WORKER_ROUTING_CLASS_D"] }
  "classE_architectureRoutingDecision" { $Parsed["LOCAL_WORKER_ROUTING_CLASS_E"] }
  default { FailWrapper "unsupported_task_class" 1 }
}

$SelectedAuthority = switch ($TaskClass) {
  "classA_lowRiskUtility" { "local.utility.tiny" }
  "classB_boundedCodeDocDraft" { "local.coder.primary" }
  "classC_proofRunnerDesign" { "frontier.coordinator" }
  "classD_runtimeMutationOrRatification" { "frontier.coordinator" }
  "classE_architectureRoutingDecision" { "frontier.coordinator" }
  default { "unknown" }
}

Emit "LOCAL_WORKER_ROUTING_SURFACE_FROM_HELPER" $Surface
Emit "LOCAL_WORKER_ROUTING_COORDINATOR_FROM_HELPER" $Coordinator
Emit "LOCAL_WORKER_ROUTING_CODER_PRIMARY_FROM_HELPER" $CoderPrimary
Emit "LOCAL_WORKER_ROUTING_UTILITY_TINY_FROM_HELPER" $UtilityTiny
Emit "LOCAL_WORKER_ROUTING_RUNTIME_INTEGRATION_ENABLED" $RuntimeIntegration
Emit "LOCAL_WORKER_ROUTING_RUNTIME_CONSUMPTION_ENABLED" $RuntimeConsumption
Emit "LOCAL_WORKER_ROUTING_STATIC_DECISION" $Decision
Emit "LOCAL_WORKER_ROUTING_SELECTED_AUTHORITY" $SelectedAuthority

if ($RuntimeIntegration -ne "YES" -or $RuntimeConsumption -ne "YES") {
  Emit "LOCAL_WORKER_ROUTING_CONSUMPTION_ALLOWED" "NO"
  Emit "LOCAL_WORKER_ROUTING_CONSUMPTION_BLOCK_REASON" "runtime_or_consumption_disabled"
  Emit "LOCAL_WORKER_ROUTING_WRAPPER_VALID" "YES"
  Emit "LOCAL_WORKER_ROUTING_VALIDATION_ONLY" "YES"
  exit 0
}

Emit "LOCAL_WORKER_ROUTING_CONSUMPTION_ALLOWED" "YES"
Emit "LOCAL_WORKER_ROUTING_CONSUMPTION_BLOCK_REASON" "none"
Emit "LOCAL_WORKER_ROUTING_WRAPPER_VALID" "YES"
Emit "LOCAL_WORKER_ROUTING_VALIDATION_ONLY" "YES"
exit 0

param([string]$ConfigPath = "")
$ErrorActionPreference = "Stop"

function Emit {
  param([string]$Name, [string]$Value)
  Write-Output "$Name=$Value"
}

function BoolText {
  param([object]$Value)
  if ($Value -eq $true) { return "YES" }
  return "NO"
}

function Fail {
  param([string]$Marker, [string]$Message)
  Emit "LOCAL_WORKER_ROUTING_CONFIG_VALID" "NO"
  Emit $Marker "NO"
  Emit "LOCAL_WORKER_ROUTING_FAILURE" $Message
  Emit "LOCAL_WORKER_ROUTING_WSL_USED" "NO"
  Emit "LOCAL_WORKER_ROUTING_OLLAMA_USED" "NO"
  Emit "LOCAL_WORKER_ROUTING_OLLAMA_PULL_USED" "NO"
  Emit "LOCAL_WORKER_ROUTING_OLLAMA_RUN_USED" "NO"
  Emit "LOCAL_WORKER_ROUTING_MODEL_DOWNLOADS" "NO"
  Emit "LOCAL_WORKER_ROUTING_RUNTIME_TOUCHED" "NO"
  Emit "LOCAL_WORKER_ROUTING_SCRIPT_MUTATION" "NO"
  Emit "LOCAL_WORKER_ROUTING_RC7_TOUCHED" "NO"
  exit 1
}

function Assert-Equal {
  param([string]$Marker, [object]$Actual, [object]$Expected, [string]$Reason)
  if ($Actual -ne $Expected) { Fail $Marker $Reason }
  Emit $Marker "YES"
}

function Assert-Bool {
  param([string]$Marker, [object]$Actual, [bool]$Expected, [string]$Reason)
  if ($Actual -ne $Expected) { Fail $Marker $Reason }
  Emit $Marker "YES"
}

function Assert-ContainsAll {
  param([string]$Marker, [object[]]$Actual, [string[]]$Required, [string]$ReasonPrefix)
  foreach ($Item in $Required) {
    if ($Actual -notcontains $Item) { Fail $Marker "$ReasonPrefix$Item" }
  }
  Emit $Marker "YES"
}

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
if ([string]::IsNullOrWhiteSpace($ConfigPath)) {
  $ConfigPath = Join-Path $ScriptRoot "local_worker_routing_v1.json"
}

Emit "LOCAL_WORKER_ROUTING_HELPER" "Get-LocalWorkerRoutingConfig_v1.ps1"
Emit "LOCAL_WORKER_ROUTING_CONFIG_PATH" $ConfigPath
Emit "LOCAL_WORKER_ROUTING_WSL_USED" "NO"
Emit "LOCAL_WORKER_ROUTING_OLLAMA_USED" "NO"
Emit "LOCAL_WORKER_ROUTING_OLLAMA_PULL_USED" "NO"
Emit "LOCAL_WORKER_ROUTING_OLLAMA_RUN_USED" "NO"
Emit "LOCAL_WORKER_ROUTING_MODEL_DOWNLOADS" "NO"
Emit "LOCAL_WORKER_ROUTING_RUNTIME_TOUCHED" "NO"
Emit "LOCAL_WORKER_ROUTING_SCRIPT_MUTATION" "NO"
Emit "LOCAL_WORKER_ROUTING_RC7_TOUCHED" "NO"

if (!(Test-Path -LiteralPath $ConfigPath)) {
  Emit "LOCAL_WORKER_ROUTING_CONFIG_FOUND" "NO"
  Fail "LOCAL_WORKER_ROUTING_CONFIG_FOUND" "config_missing"
}

Emit "LOCAL_WORKER_ROUTING_CONFIG_FOUND" "YES"
$ConfigHash = (Get-FileHash -LiteralPath $ConfigPath -Algorithm SHA256).Hash.ToLowerInvariant()
Emit "LOCAL_WORKER_ROUTING_CONFIG_SHA256" $ConfigHash

try {
  $ConfigText = Get-Content -LiteralPath $ConfigPath -Raw
  $Config = $ConfigText | ConvertFrom-Json
  Emit "LOCAL_WORKER_ROUTING_JSON_PARSE" "PASS"
} catch {
  Emit "LOCAL_WORKER_ROUTING_JSON_PARSE" "FAIL"
  Fail "LOCAL_WORKER_ROUTING_JSON_PARSE" "json_parse_failed"
}

Assert-Equal "LOCAL_WORKER_ROUTING_SCHEMA_ID_VALID" $Config.schema.id "openclaw.local_worker_routing.v1" "schema_id_mismatch"
Assert-Equal "LOCAL_WORKER_ROUTING_SCHEMA_VERSION_VALID" $Config.schema.version 1 "schema_version_mismatch"
Assert-Equal "LOCAL_WORKER_ROUTING_SHELL_DEFAULT_VALID" $Config.shellContract.defaultShell "powershell.exe" "default_shell_mismatch"
Assert-Equal "LOCAL_WORKER_ROUTING_SHELL_COMPAT_VALID" $Config.shellContract.compatibility "Windows PowerShell 5.1" "shell_compat_mismatch"
Assert-Bool "LOCAL_WORKER_ROUTING_SHELL_PWSH_BOUNDARY_VALID" $Config.shellContract.pwshAllowedOnlyWhenBoundaryDeclares $true "pwsh_boundary_gate_missing"

Assert-Equal "LOCAL_WORKER_ROUTING_SURFACE_VALID" $Config.localWorkerSurface.currentSurface "WSL Ollama" "local_surface_mismatch"
Assert-Bool "LOCAL_WORKER_ROUTING_WINDOWS_OLLAMA_ASSUMED_VALID" $Config.localWorkerSurface.windowsOllamaAssumedAvailable $false "windows_ollama_assumption_mismatch"

if ($Config.localWorkerSurface.runtimeIntegrationEnabled -eq $true) {
  Emit "LOCAL_WORKER_ROUTING_RUNTIME_INTEGRATION_DISABLED" "NO"
} elseif ($Config.localWorkerSurface.runtimeIntegrationEnabled -eq $false) {
  Emit "LOCAL_WORKER_ROUTING_RUNTIME_INTEGRATION_DISABLED" "YES"
} else {
  Fail "LOCAL_WORKER_ROUTING_RUNTIME_INTEGRATION_BOOLEAN_VALID" "runtime_integration_not_boolean"
}
Emit "LOCAL_WORKER_ROUTING_RUNTIME_INTEGRATION_BOOLEAN_VALID" "YES"

Assert-Bool "LOCAL_WORKER_ROUTING_RUNTIME_BOUNDARY_REQUIRED_VALID" $Config.localWorkerSurface.runtimeIntegrationBoundaryRequired $true "runtime_boundary_required_missing"
Assert-Bool "LOCAL_WORKER_ROUTING_RUNTIME_CONSUMPTION_DISABLED" $Config.futureIntegration.runtimeConsumptionEnabled $false "runtime_consumption_not_disabled"
Assert-Bool "LOCAL_WORKER_ROUTING_C31_CONFIG_ONLY_VALID" $Config.futureIntegration.c31CreatesConfigOnly $true "c31_config_only_missing"
Assert-Equal "LOCAL_WORKER_ROUTING_IMPLEMENTATION_BOUNDARY_VALID" $Config.futureIntegration.implementationBoundaryRequired "C32_or_later" "implementation_boundary_mismatch"
Assert-Bool "LOCAL_WORKER_ROUTING_SCRIPT_MUTATION_DISABLED_VALID" $Config.futureIntegration.routingScriptMutationAllowedHere $false "routing_script_mutation_not_disabled"

Assert-Equal "LOCAL_WORKER_ROUTING_COORDINATOR_VALID" $Config.coordinatorAuthority.primary "GPT-5.5 Thinking / high" "coordinator_mismatch"

$CoderCandidates = @($Config.localRoles.coderPrimary.candidates)
$UtilityCandidates = @($Config.localRoles.utilityTiny.candidates)
Assert-ContainsAll "LOCAL_WORKER_ROUTING_CODER_PRIMARY_VALID" $CoderCandidates @("qwen2.5-coder:32b") "missing_coder_candidate_"
Assert-ContainsAll "LOCAL_WORKER_ROUTING_UTILITY_TINY_VALID" $UtilityCandidates @("qwen3:0.6b","qwen3:0.6b-4k") "missing_utility_candidate_"

$Prohibitions = @($Config.localWorkerProhibitions)
Assert-ContainsAll "LOCAL_WORKER_ROUTING_PROHIBITIONS_VALID" $Prohibitions @(
  "must_not_decide_NBMs",
  "must_not_declare_final_PASS_FAIL_BLOCKED",
  "must_not_claim_package_ratification",
  "must_not_close_root_cause",
  "must_not_touch_RC7",
  "must_not_print_token_values",
  "must_not_perform_token_diagnosis_without_explicit_boundary",
  "must_not_run_destructive_WSL_operations",
  "must_not_run_ollama_pull_without_explicit_boundary",
  "must_not_run_ollama_run_without_explicit_boundary",
  "must_not_mutate_runtime_or_routing_without_explicit_boundary"
) "missing_prohibition_"

Assert-Equal "LOCAL_WORKER_ROUTING_CLASS_A_VALID" $Config.routingClasses.classA_lowRiskUtility "local.utility.tiny_allowed" "class_a_mismatch"
Assert-Equal "LOCAL_WORKER_ROUTING_CLASS_B_VALID" $Config.routingClasses.classB_boundedCodeDocDraft "local.coder.primary_draft_allowed" "class_b_mismatch"
Assert-Equal "LOCAL_WORKER_ROUTING_CLASS_C_VALID" $Config.routingClasses.classC_proofRunnerDesign "frontier.coordinator_final_review_required" "class_c_mismatch"
Assert-Equal "LOCAL_WORKER_ROUTING_CLASS_D_VALID" $Config.routingClasses.classD_runtimeMutationOrRatification "frontier.coordinator_required" "class_d_mismatch"
Assert-Equal "LOCAL_WORKER_ROUTING_CLASS_E_VALID" $Config.routingClasses.classE_architectureRoutingDecision "frontier.coordinator_required" "class_e_mismatch"

Assert-Bool "LOCAL_WORKER_ROUTING_GUARDRAIL_NO_WSL_VALID" $Config.guardrails.noWsl $true "noWsl_guardrail_missing"
Assert-Bool "LOCAL_WORKER_ROUTING_GUARDRAIL_NO_RUNTIME_VALID" $Config.guardrails.noRuntimeTouch $true "noRuntimeTouch_guardrail_missing"
Assert-Bool "LOCAL_WORKER_ROUTING_GUARDRAIL_NO_MODEL_DOWNLOADS_VALID" $Config.guardrails.noModelDownloads $true "noModelDownloads_guardrail_missing"
Assert-Bool "LOCAL_WORKER_ROUTING_GUARDRAIL_NO_OLLAMA_PULL_VALID" $Config.guardrails.noOllamaPull $true "noOllamaPull_guardrail_missing"
Assert-Bool "LOCAL_WORKER_ROUTING_GUARDRAIL_NO_OLLAMA_RUN_VALID" $Config.guardrails.noOllamaRun $true "noOllamaRun_guardrail_missing"
Assert-Bool "LOCAL_WORKER_ROUTING_GUARDRAIL_NO_ROUTING_MUTATION_VALID" $Config.guardrails.noRoutingScriptMutation $true "noRoutingScriptMutation_guardrail_missing"
Assert-Bool "LOCAL_WORKER_ROUTING_GUARDRAIL_NO_PACKAGE_REBUILD_VALID" $Config.guardrails.noPackageRebuild $true "noPackageRebuild_guardrail_missing"
Assert-Bool "LOCAL_WORKER_ROUTING_GUARDRAIL_NO_DISCORD_VALID" $Config.guardrails.noDiscordChecks $true "noDiscordChecks_guardrail_missing"
Assert-Bool "LOCAL_WORKER_ROUTING_GUARDRAIL_NO_TOKEN_DUMP_VALID" $Config.guardrails.noTokenEnvDump $true "noTokenEnvDump_guardrail_missing"
Assert-Bool "LOCAL_WORKER_ROUTING_GUARDRAIL_NO_RC7_VALID" $Config.guardrails.noRc7Touch $true "noRc7Touch_guardrail_missing"
Emit "LOCAL_WORKER_ROUTING_GUARDRAILS_VALID" "YES"

Emit "LOCAL_WORKER_ROUTING_CONFIG_VALID" "YES"
Emit "LOCAL_WORKER_ROUTING_SCHEMA_ID" $Config.schema.id
Emit "LOCAL_WORKER_ROUTING_SCHEMA_VERSION" ([string]$Config.schema.version)
Emit "LOCAL_WORKER_ROUTING_SURFACE" $Config.localWorkerSurface.currentSurface
Emit "LOCAL_WORKER_ROUTING_RUNTIME_INTEGRATION_ENABLED" (BoolText $Config.localWorkerSurface.runtimeIntegrationEnabled)
Emit "LOCAL_WORKER_ROUTING_RUNTIME_CONSUMPTION_ENABLED" (BoolText $Config.futureIntegration.runtimeConsumptionEnabled)
Emit "LOCAL_WORKER_ROUTING_COORDINATOR" $Config.coordinatorAuthority.primary
Emit "LOCAL_WORKER_ROUTING_CODER_PRIMARY" ($CoderCandidates -join ",")
Emit "LOCAL_WORKER_ROUTING_UTILITY_TINY" ($UtilityCandidates -join ",")
Emit "LOCAL_WORKER_ROUTING_CLASS_A" $Config.routingClasses.classA_lowRiskUtility
Emit "LOCAL_WORKER_ROUTING_CLASS_B" $Config.routingClasses.classB_boundedCodeDocDraft
Emit "LOCAL_WORKER_ROUTING_CLASS_C" $Config.routingClasses.classC_proofRunnerDesign
Emit "LOCAL_WORKER_ROUTING_CLASS_D" $Config.routingClasses.classD_runtimeMutationOrRatification
Emit "LOCAL_WORKER_ROUTING_CLASS_E" $Config.routingClasses.classE_architectureRoutingDecision
Emit "LOCAL_WORKER_ROUTING_VALIDATION_ONLY" "YES"
exit 0

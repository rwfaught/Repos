param(
  [ValidateSet("live-probe")]
  [string]$Mode = "live-probe",

  [ValidateSet("local.utility.tiny")]
  [string]$Role = "local.utility.tiny",

  [ValidateSet("qwen3:0.6b")]
  [string]$Model = "qwen3:0.6b",

  [ValidateSet("classA_lowRiskUtility")]
  [string]$TaskClass = "classA_lowRiskUtility",

  [ValidateSet("fixed-authority-json")]
  [string]$PromptMode = "fixed-authority-json",

  [Parameter(Mandatory=$true)]
  [string]$WslDistro
)

$ErrorActionPreference = "Stop"

function Emit {
  param([string]$Name, [string]$Value)
  Write-Output "$Name=$Value"
}

function FailAdapter {
  param([string]$Reason, [int]$ExitCode = 1)
  Emit "LOCAL_WORKER_LIVE_PROBE_ADAPTER_VALID" "NO"
  Emit "LOCAL_WORKER_LIVE_PROBE_ADAPTER_FAILURE" $Reason
  Emit "LOCAL_WORKER_LIVE_PROBE_RUNTIME_ACTION_ATTEMPTED" "NO"
  Emit "LOCAL_WORKER_LIVE_PROBE_MODEL_PULL_USED" "NO"
  Emit "LOCAL_WORKER_LIVE_PROBE_INSTALLER_TOUCHED" "NO"
  Emit "LOCAL_WORKER_LIVE_PROBE_DISCORD_TOUCHED" "NO"
  Emit "LOCAL_WORKER_LIVE_PROBE_RC7_TOUCHED" "NO"
  Emit "LOCAL_WORKER_LIVE_PROBE_ZIP_INSPECTION_USED" "NO"
  Emit "LOCAL_WORKER_LIVE_PROBE_CODEX_USED" "NO"
  Emit "LOCAL_WORKER_LIVE_PROBE_OZ_USED" "NO"
  Emit "LOCAL_WORKER_LIVE_PROBE_RESULT" "FAIL"
  exit $ExitCode
}

function RedactLine {
  param([string]$Line)
  $Safe = $Line -replace 'sk-[A-Za-z0-9_\-]{10,}', 'sk-<REDACTED>'
  $Safe = $Safe -replace '[MN][A-Za-z\d]{23}\.[\w-]{6}\.[\w-]{20,}', '<DISCORD_TOKEN_REDACTED>'
  $Safe = $Safe -replace 'token=[A-Za-z0-9_\-\.]{8,}', 'token=<REDACTED>'
  return $Safe
}

Emit "LOCAL_WORKER_LIVE_PROBE_ADAPTER" "Invoke-LocalWorkerLiveProbeAdapter_v1.ps1"
Emit "LOCAL_WORKER_LIVE_PROBE_MODE" $Mode
Emit "LOCAL_WORKER_LIVE_PROBE_ROLE" $Role
Emit "LOCAL_WORKER_LIVE_PROBE_MODEL" $Model
Emit "LOCAL_WORKER_LIVE_PROBE_TASK_CLASS" $TaskClass
Emit "LOCAL_WORKER_LIVE_PROBE_PROMPT_MODE" $PromptMode
Emit "LOCAL_WORKER_LIVE_PROBE_RUNTIME_GENERAL_CONSUMPTION_ENABLED" "NO"
Emit "LOCAL_WORKER_LIVE_PROBE_COORDINATOR_AUTHORITY_PRESERVED" "YES"
Emit "LOCAL_WORKER_LIVE_PROBE_WORKER_MAY_DECIDE_NBM" "NO"
Emit "LOCAL_WORKER_LIVE_PROBE_WORKER_MAY_RATIFY" "NO"
Emit "LOCAL_WORKER_LIVE_PROBE_WORKER_MAY_CLOSE_ROOT_CAUSE" "NO"
Emit "LOCAL_WORKER_LIVE_PROBE_MODEL_PULL_USED" "NO"
Emit "LOCAL_WORKER_LIVE_PROBE_INSTALLER_TOUCHED" "NO"
Emit "LOCAL_WORKER_LIVE_PROBE_DISCORD_TOUCHED" "NO"
Emit "LOCAL_WORKER_LIVE_PROBE_ZIP_INSPECTION_USED" "NO"
Emit "LOCAL_WORKER_LIVE_PROBE_CODEX_USED" "NO"
Emit "LOCAL_WORKER_LIVE_PROBE_OZ_USED" "NO"

if ([string]::IsNullOrWhiteSpace($WslDistro)) {
  FailAdapter "explicit_wsl_distro_required_no_default_wsl_allowed" 2
}

if ($WslDistro -match "RC7") {
  Emit "LOCAL_WORKER_LIVE_PROBE_RC7_TOUCHED" "NO"
  FailAdapter "rc7_distro_refused_by_adapter" 2
}

$WslCommand = Get-Command wsl.exe -ErrorAction SilentlyContinue
if ($null -eq $WslCommand) {
  FailAdapter "wsl_exe_not_found" 2
}

$ProbePrompt = '/no_think Return exactly one compact JSON object only. No markdown. No code fence. No explanation. No thinking text. JSON: {"worker_alive":true,"authority":"scoped-labor-only","may_decide_nbm":false,"may_ratify":false,"may_close_root_cause":false}'
$SafePromptForBash = $ProbePrompt.Replace("'", "'\''")
$BashCommand = "ollama run qwen3:0.6b '$SafePromptForBash'"

Emit "LOCAL_WORKER_LIVE_PROBE_ADAPTER_VALID" "YES"
Emit "LOCAL_WORKER_LIVE_PROBE_RUNTIME_ACTION_SCOPE" "single-local-utility-live-probe"
Emit "LOCAL_WORKER_LIVE_PROBE_RUNTIME_ACTION_ATTEMPTED" "YES"
Emit "LOCAL_WORKER_LIVE_PROBE_WSL_USED" "YES"
Emit "LOCAL_WORKER_LIVE_PROBE_OLLAMA_USED" "YES"
Emit "LOCAL_WORKER_LIVE_PROBE_OLLAMA_RUN_USED" "YES"
Emit "LOCAL_WORKER_LIVE_PROBE_MODEL_DOWNLOADS" "NO"
Emit "LOCAL_WORKER_LIVE_PROBE_WSL_DISTRO" $WslDistro

$WslArgs = @("-d", $WslDistro, "--", "bash", "-lc", $BashCommand)
$PreviousErrorActionPreference = $ErrorActionPreference
$ErrorActionPreference = "Continue"

try {
  $Output = & wsl.exe @WslArgs 2>&1
  $Rc = $LASTEXITCODE
} catch {
  $Output = @("LOCAL_WORKER_LIVE_PROBE_WSL_NATIVE_COMMAND_EXCEPTION=$($_.Exception.Message)")
  $Rc = 9001
} finally {
  $ErrorActionPreference = $PreviousErrorActionPreference
}

Emit "LOCAL_WORKER_LIVE_PROBE_WSL_RC" ([string]$Rc)

foreach ($Line in $Output) {
  $Text = [string]$Line
  $Safe = RedactLine $Text
  Write-Output "LOCAL_WORKER_LIVE_PROBE_WORKER_OUTPUT>$Safe"
}

if ($Rc -ne 0) {
  Emit "LOCAL_WORKER_LIVE_PROBE_RESULT" "FAIL"
  Emit "LOCAL_WORKER_LIVE_PROBE_FAILURE" "wsl_ollama_run_nonzero"
  exit 1
}

$Joined = ($Output | ForEach-Object { [string]$_ }) -join "`n"
$JsonMatches = [regex]::Matches($Joined, '\{[^{}]*\}')
$Obj = $null
$JsonCandidate = ""

for ($JsonIndex = $JsonMatches.Count - 1; $JsonIndex -ge 0; $JsonIndex--) {
  $Candidate = $JsonMatches[$JsonIndex].Value
  try {
    $CandidateObj = $Candidate | ConvertFrom-Json
    if ($null -ne $CandidateObj) {
      $Obj = $CandidateObj
      $JsonCandidate = $Candidate
      break
    }
  } catch {
    # Continue scanning earlier JSON-looking candidates.
  }
}

$FieldFallbackUsed = "NO"
$NormalizedJoined = $Joined -replace '\x1B\[[0-?]*[ -/]*[@-~]', ''
$NormalizedJoined = $NormalizedJoined -replace '[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', ''
$CompactJoined = $NormalizedJoined -replace '\s+', ''

$FallbackWorkerAliveRaw = [regex]::IsMatch($Joined, '"worker_alive"\s*:\s*true')
$FallbackAuthorityMatchRaw = [regex]::Match($Joined, '"authority"\s*:\s*"([^"]+)"')
$FallbackMayDecideFalseRaw = [regex]::IsMatch($Joined, '"may_decide_nbm"\s*:\s*false')
$FallbackMayRatifyFalseRaw = [regex]::IsMatch($Joined, '"may_ratify"\s*:\s*false')
$FallbackMayCloseFalseRaw = [regex]::IsMatch($Joined, '"may_close_root_cause"\s*:\s*false')

$FallbackWorkerAliveCompact = $CompactJoined.Contains('"worker_alive":true')
$FallbackAuthorityCompact = $CompactJoined.Contains('"authority":"scoped-labor-only"')
$FallbackMayDecideFalseCompact = $CompactJoined.Contains('"may_decide_nbm":false')
$FallbackMayRatifyFalseCompact = $CompactJoined.Contains('"may_ratify":false')
$FallbackMayCloseFalseCompact = $CompactJoined.Contains('"may_close_root_cause":false')

Emit "LOCAL_WORKER_LIVE_PROBE_JSON_MATCH_COUNT" ([string]$JsonMatches.Count)
Emit "LOCAL_WORKER_LIVE_PROBE_FALLBACK_RAW_WORKER_ALIVE" ([string]$FallbackWorkerAliveRaw).ToUpperInvariant()
Emit "LOCAL_WORKER_LIVE_PROBE_FALLBACK_RAW_AUTHORITY_MATCH" ([string]$FallbackAuthorityMatchRaw.Success).ToUpperInvariant()
if ($FallbackAuthorityMatchRaw.Success) { Emit "LOCAL_WORKER_LIVE_PROBE_FALLBACK_RAW_AUTHORITY_VALUE" $FallbackAuthorityMatchRaw.Groups[1].Value }
Emit "LOCAL_WORKER_LIVE_PROBE_FALLBACK_RAW_MAY_DECIDE_FALSE" ([string]$FallbackMayDecideFalseRaw).ToUpperInvariant()
Emit "LOCAL_WORKER_LIVE_PROBE_FALLBACK_RAW_MAY_RATIFY_FALSE" ([string]$FallbackMayRatifyFalseRaw).ToUpperInvariant()
Emit "LOCAL_WORKER_LIVE_PROBE_FALLBACK_RAW_MAY_CLOSE_FALSE" ([string]$FallbackMayCloseFalseRaw).ToUpperInvariant()
Emit "LOCAL_WORKER_LIVE_PROBE_FALLBACK_COMPACT_WORKER_ALIVE" ([string]$FallbackWorkerAliveCompact).ToUpperInvariant()
Emit "LOCAL_WORKER_LIVE_PROBE_FALLBACK_COMPACT_AUTHORITY" ([string]$FallbackAuthorityCompact).ToUpperInvariant()
Emit "LOCAL_WORKER_LIVE_PROBE_FALLBACK_COMPACT_MAY_DECIDE_FALSE" ([string]$FallbackMayDecideFalseCompact).ToUpperInvariant()
Emit "LOCAL_WORKER_LIVE_PROBE_FALLBACK_COMPACT_MAY_RATIFY_FALSE" ([string]$FallbackMayRatifyFalseCompact).ToUpperInvariant()
Emit "LOCAL_WORKER_LIVE_PROBE_FALLBACK_COMPACT_MAY_CLOSE_FALSE" ([string]$FallbackMayCloseFalseCompact).ToUpperInvariant()

if ($null -eq $Obj) {
  $RawFallbackPass = ($FallbackWorkerAliveRaw -and $FallbackAuthorityMatchRaw.Success -and $FallbackAuthorityMatchRaw.Groups[1].Value -eq "scoped-labor-only" -and $FallbackMayDecideFalseRaw -and $FallbackMayRatifyFalseRaw -and $FallbackMayCloseFalseRaw)
  $CompactFallbackPass = ($FallbackWorkerAliveCompact -and $FallbackAuthorityCompact -and $FallbackMayDecideFalseCompact -and $FallbackMayRatifyFalseCompact -and $FallbackMayCloseFalseCompact)

  if ($RawFallbackPass -or $CompactFallbackPass) {
    $Obj = [pscustomobject]@{
      worker_alive = $true
      authority = "scoped-labor-only"
      may_decide_nbm = $false
      may_ratify = $false
      may_close_root_cause = $false
    }
    if ($CompactFallbackPass -and -not $RawFallbackPass) {
      $JsonCandidate = "<compact-field-fallback>"
    } else {
      $JsonCandidate = "<field-regex-fallback>"
    }
    $FieldFallbackUsed = "YES"
  } else {
    Emit "LOCAL_WORKER_LIVE_PROBE_JSON_PARSE_FIELD_FALLBACK_USED" "NO"
    Emit "LOCAL_WORKER_LIVE_PROBE_RESULT" "FAIL"
    Emit "LOCAL_WORKER_LIVE_PROBE_FAILURE" "worker_output_json_parse_failed"
    exit 1
  }
}

$NonWarningLines = @($Output | ForEach-Object { [string]$_ } | Where-Object { $_ -notmatch '^wsl: Failed to start the systemd user session' -and -not [string]::IsNullOrWhiteSpace($_) })
$OutputBody = ($NonWarningLines -join "`n").Trim()
$ExactJsonOnly = ($OutputBody -eq $JsonCandidate.Trim())
Emit "LOCAL_WORKER_LIVE_PROBE_JSON_EXTRACTED_FROM_WORKER_OUTPUT" "YES"
Emit "LOCAL_WORKER_LIVE_PROBE_WORKER_OUTPUT_EXACT_JSON_ONLY" ([string]$ExactJsonOnly).ToUpperInvariant()
Emit "LOCAL_WORKER_LIVE_PROBE_JSON_PARSE_FIELD_FALLBACK_USED" $FieldFallbackUsed

$WorkerAlive = [bool]$Obj.worker_alive
$Authority = [string]$Obj.authority
$MayDecideNbm = [bool]$Obj.may_decide_nbm
$MayRatify = [bool]$Obj.may_ratify
$MayCloseRootCause = [bool]$Obj.may_close_root_cause

Emit "LOCAL_WORKER_LIVE_PROBE_WORKER_ALIVE" ([string]$WorkerAlive).ToUpperInvariant()
Emit "LOCAL_WORKER_LIVE_PROBE_WORKER_AUTHORITY" $Authority
Emit "LOCAL_WORKER_LIVE_PROBE_WORKER_MAY_DECIDE_NBM" ([string]$MayDecideNbm).ToUpperInvariant()
Emit "LOCAL_WORKER_LIVE_PROBE_WORKER_MAY_RATIFY" ([string]$MayRatify).ToUpperInvariant()
Emit "LOCAL_WORKER_LIVE_PROBE_WORKER_MAY_CLOSE_ROOT_CAUSE" ([string]$MayCloseRootCause).ToUpperInvariant()

if ($WorkerAlive -ne $true) {
  Emit "LOCAL_WORKER_LIVE_PROBE_RESULT" "FAIL"
  Emit "LOCAL_WORKER_LIVE_PROBE_FAILURE" "worker_alive_not_true"
  exit 1
}
if ($Authority -ne "scoped-labor-only") {
  Emit "LOCAL_WORKER_LIVE_PROBE_RESULT" "FAIL"
  Emit "LOCAL_WORKER_LIVE_PROBE_FAILURE" "worker_authority_not_scoped_labor_only"
  exit 1
}
if ($MayDecideNbm -ne $false -or $MayRatify -ne $false -or $MayCloseRootCause -ne $false) {
  Emit "LOCAL_WORKER_LIVE_PROBE_RESULT" "FAIL"
  Emit "LOCAL_WORKER_LIVE_PROBE_FAILURE" "worker_authority_denial_fields_not_false"
  exit 1
}

Emit "LOCAL_WORKER_LIVE_PROBE_RESULT" "PASS"
exit 0

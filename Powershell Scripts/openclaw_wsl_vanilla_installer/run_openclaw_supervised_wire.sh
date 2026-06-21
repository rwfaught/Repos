#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_NAME="$(basename "$0")"
CONFIG_PATH=""
PACKAGE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_ROOT="${HOME}/openclaw_install"
LOG_ROOT="${INSTALL_ROOT}/logs"
STAMP="$(date +%Y%m%d_%H%M%S)"
RUN_DIR="${LOG_ROOT}/${STAMP}"
STATUS_DIR="${RUN_DIR}/wire_status"
MARKER_DIR="${RUN_DIR}/wire_markers"
OPERATOR_STATE_FILE="${RUN_DIR}/operator_state_v1_7.json"
RUN_LOG="${RUN_DIR}/runner.log"

mkdir -p "$RUN_DIR" "$STATUS_DIR" "$MARKER_DIR"
exec > >(tee -a "$RUN_LOG") 2>&1

log() { printf '\n[%s] %s\n' "$SCRIPT_NAME" "$*"; }
die() { printf '\n[%s] ERROR: %s\n' "$SCRIPT_NAME" "$*" >&2; exit 1; }

usage() {
  cat <<'USAGE'
Usage:
  bash run_openclaw_supervised_wire.sh --config /path/to/install_config.json
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --config) CONFIG_PATH="${2:-}"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) die "Unknown option: $1" ;;
  esac
done

[[ -n "$CONFIG_PATH" ]] || { usage; die "--config is required"; }
[[ -f "$CONFIG_PATH" ]] || die "Config not found: $CONFIG_PATH"

json_get() {
  local expr="$1"
  python3 - "$CONFIG_PATH" "$expr" <<'PY'
import json,sys
path,expr=sys.argv[1],sys.argv[2]
cur=json.load(open(path,encoding="utf-8"))
for p in expr.split('.'):
    if not p:
        continue
    if isinstance(cur,dict) and p in cur:
        cur=cur[p]
    else:
        cur=None
        break
if isinstance(cur,bool):
    print("true" if cur else "false")
elif cur is None:
    print("")
else:
    print(cur)
PY
}
bool_true() { [[ "$(json_get "$1")" == "true" ]]; }
conductor_json_get() {
  local key="$1"
  local marker="${INSTALL_ROOT}/config/conductor_marker_v1_7.json"
  python3 - "$marker" "$key" <<'PY'
import json,sys,os
path,key=sys.argv[1],sys.argv[2]
if not os.path.exists(path):
    print("UNKNOWN")
    raise SystemExit(0)
try:
    data=json.load(open(path,encoding="utf-8"))
except Exception:
    print("UNKNOWN")
    raise SystemExit(0)
v=data.get(key, "UNKNOWN")
if isinstance(v, bool):
    print("true" if v else "false")
elif v in [None, ""]:
    print("UNKNOWN")
else:
    print(v)
PY
}

write_status() {
  local name="$1" result="$2" reason="$3" evidence="$4"
  cat >"${STATUS_DIR}/${name}.status" <<EOF2
status=${result}
timestamp=$(date -Iseconds)
reason=${reason}
evidence=${evidence}
EOF2
}

write_marker() {
  local key="$1" value="$2"
  cat >"${MARKER_DIR}/${key}.marker" <<EOF2
key=${key}
value=${value}
timestamp=$(date -Iseconds)
EOF2
}

INSTALL_TERMINAL_RESULT="NOT_STARTED"
INSTALL_FAILURE_REASON="NONE"
RUNTIME_PROOF_DISPOSITION="NOT_EVALUATED"
CURRENT_CRITICAL_STAGE="init"

write_install_terminal_markers() {
  write_marker "installTerminalResult" "$INSTALL_TERMINAL_RESULT"
  write_marker "installFailureReason" "$INSTALL_FAILURE_REASON"
  write_marker "runtimeProofDisposition" "$RUNTIME_PROOF_DISPOSITION"
}

runner_exit_trap() {
  local rc=$?
  if [[ "$rc" != "0" && "$INSTALL_TERMINAL_RESULT" == "IN_PROGRESS" ]]; then
    INSTALL_TERMINAL_RESULT="FAIL"
    INSTALL_FAILURE_REASON="${CURRENT_CRITICAL_STAGE:-bootstrap}"
    RUNTIME_PROOF_DISPOSITION="SKIPPED_INSTALL_FAILED"
    write_install_terminal_markers
  fi
  trap - EXIT
  exit "$rc"
}

trap runner_exit_trap EXIT

write_operator_state() {
  local stage="$1" phase="$2" input_required="$3" input_type="$4" instruction="$5" secret_expected="$6" recommended_window="$7" watch_command="$8" continue_instruction="$9" abort_instruction="${10}"
  python3 - "$OPERATOR_STATE_FILE" <<'PY'
import json,sys,os,datetime
path=sys.argv[1]
data={
  "runDir": os.environ.get("RUN_DIR",""),
  "stage": os.environ.get("OP_STAGE",""),
  "phase": os.environ.get("OP_PHASE",""),
  "inputRequired": os.environ.get("OP_INPUT_REQUIRED","false"),
  "inputType": os.environ.get("OP_INPUT_TYPE","none"),
  "instruction": os.environ.get("OP_INSTRUCTION",""),
  "secretExpected": os.environ.get("OP_SECRET_EXPECTED","false"),
  "recommendedWindow": os.environ.get("OP_RECOMMENDED_WINDOW","installer"),
  "watchCommand": os.environ.get("OP_WATCH_COMMAND",""),
  "continueInstruction": os.environ.get("OP_CONTINUE_INSTRUCTION",""),
  "abortInstruction": os.environ.get("OP_ABORT_INSTRUCTION",""),
  "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
}
with open(path,"w",encoding="utf-8") as f:
    json.dump(data,f,indent=2)
PY
}

set_operator_state() {
  OP_STAGE="$1" \
  OP_PHASE="$2" \
  OP_INPUT_REQUIRED="$3" \
  OP_INPUT_TYPE="$4" \
  OP_INSTRUCTION="$5" \
  OP_SECRET_EXPECTED="$6" \
  OP_RECOMMENDED_WINDOW="$7" \
  OP_WATCH_COMMAND="$8" \
  OP_CONTINUE_INSTRUCTION="$9" \
  OP_ABORT_INSTRUCTION="${10}" \
  RUN_DIR="$RUN_DIR" \
  write_operator_state "$@"
}

print_human_gate_banner() {
  local stage="$1" action="$2" where="$3" secret_expected="$4" secret_handling="$5" continue_instruction="$6" abort_instruction="$7" log_path="$8"
  cat <<EOF2

=== HUMAN ACTION REQUIRED ===
stage: ${stage}
run dir: ${RUN_DIR}
required action: ${action}
where: ${where}
secret expected: ${secret_expected}
secret handling: ${secret_handling}
continue: ${continue_instruction}
abort: ${abort_instruction}
relevant log: ${log_path}
EOF2
}

print_bootstrap_watcher_banner() {
  local runner_tail="tail -f ${RUN_DIR}/runner.log"
  local bootstrap_tail="tail -f ${RUN_DIR}/bootstrap.log"
  local canonical_tail="wsl.exe --distribution ${WSL_DISTRO_NAME:-<DistroName>} --user ${USER:-roger} -- bash -lc \"tail -n 80 -F ${RUN_DIR}/runner.log ${RUN_DIR}/bootstrap.log ${RUN_DIR}/openclaw_npm_install.log 2>/dev/null\""
  local ps_pattern="\$Current_log_number=\"$(basename "$RUN_DIR")\"; wsl.exe --distribution ${WSL_DISTRO_NAME:-<DistroName>} --user ${USER:-roger} -- bash -lc \"tail -n 80 -F /home/${USER:-roger}/openclaw_install/logs/\$Current_log_number/runner.log /home/${USER:-roger}/openclaw_install/logs/\$Current_log_number/bootstrap.log /home/${USER:-roger}/openclaw_install/logs/\$Current_log_number/openclaw_npm_install.log 2>/dev/null\""
  local proc_cmd="ps -ef | grep -E 'run_openclaw_supervised_wire|bootstrap_openclaw_wsl' | grep -v grep"
  local marker_cmd="ls -1 ${MARKER_DIR} && for f in ${MARKER_DIR}/*.marker; do echo \"--- \$f\"; cat \"\$f\"; done"
  cat <<EOF2

=== OPERATOR WATCH BANNER ===
run dir: ${RUN_DIR}
stage: bootstrap
Detailed bootstrap output is redirected to logs.
watch runner: ${runner_tail}
watch bootstrap: ${bootstrap_tail}
canonical watcher (copy/paste): ${canonical_tail}
PowerShell pattern: ${ps_pattern}
inspect process: ${proc_cmd}
inspect markers: ${marker_cmd}
Stop watcher with Ctrl+C only; do not stop installer.
Do not paste secrets into watcher windows.
Paste Discord token only into the foreground installer human-gate prompt.
EOF2
}

run_stage() {
  local name="$1" critical="$2"; shift 2
  local log_file="${RUN_DIR}/${name}.log"
  log "Stage: ${name}"
  if "$@" >"$log_file" 2>&1; then
    write_status "$name" "PASS" "completed" "$log_file"
    return 0
  fi
  local rc=$?
  write_status "$name" "FAIL" "exit ${rc}" "$log_file"
  if [[ "$critical" == "yes" ]]; then
    die "Critical stage failed: ${name}. See ${log_file}"
  fi
  return 0
}

run_stage_interactive() {
  local name="$1" critical="$2"; shift 2
  local log_file="${RUN_DIR}/${name}.log"
  log "Stage: ${name}"
  if "$@" 2>&1 | tee "$log_file"; then
    write_status "$name" "PASS" "completed" "$log_file"
    return 0
  fi
  local rc=${PIPESTATUS[0]}
  write_status "$name" "FAIL" "exit ${rc}" "$log_file"
  if [[ "$critical" == "yes" ]]; then
    die "Critical stage failed: ${name}. See ${log_file}"
  fi
  return 0
}

log "Starting v1.7 supervised wire runner"
log "Config: $CONFIG_PATH"
log "Run dir: $RUN_DIR"
set_operator_state "init" "starting" "false" "none" "Runner started." "false" "installer" "tail -f ${RUN_DIR}/runner.log" "Wait for next stage." "Ctrl+C in installer"

write_marker "userSystemdReadinessAttempted" "$(conductor_json_get userSystemdReadinessAttempted)"
write_marker "userSystemdReadinessResult" "$(conductor_json_get userSystemdReadinessResult)"
write_marker "userSystemdReadinessAttempts" "$(conductor_json_get userSystemdReadinessAttempts)"
write_install_terminal_markers

BOOTSTRAP="$PACKAGE_DIR/bootstrap_openclaw_wsl.sh"
BASELINE="$PACKAGE_DIR/verify_openclaw_baseline.sh"
DASHBOARD="$PACKAGE_DIR/verify_openclaw_dashboard.sh"
DISCORD_CFG="$PACKAGE_DIR/configure_openclaw_discord_v1.sh"
DISCORD_VERIFY="$PACKAGE_DIR/verify_openclaw_discord_v1_7.sh"
RUNTIME_READY="$PACKAGE_DIR/verify_openclaw_runtime_readiness.sh"
REPORT="$PACKAGE_DIR/write_wire_ratification_report_v1_7.sh"
OPTIONAL_VERIFY="$PACKAGE_DIR/verify_openclaw_optional_models.sh"
REPRO_COMPAT="$PACKAGE_DIR/apply_openclaw_repro_compat_layer_v1_7.sh"

for f in "$BOOTSTRAP" "$BASELINE" "$DASHBOARD" "$DISCORD_CFG" "$DISCORD_VERIFY" "$RUNTIME_READY" "$REPORT" "$REPRO_COMPAT"; do
  [[ -f "$f" ]] || die "Missing script: $f"
  chmod +x "$f"
done

BOOT_ARGS=(--yes)
bool_true "modelPolicy.includeReasoningModel" && BOOT_ARGS+=(--include-reasoning-model)
bool_true "modelPolicy.includeCoderModel" && BOOT_ARGS+=(--include-coder-model)
bool_true "modelPolicy.promoteReasoningModel" && BOOT_ARGS+=(--promote-reasoning-model)
bool_true "modelPolicy.promoteCoderModel" && BOOT_ARGS+=(--promote-coder-model)
bool_true "modelPolicy.includeRiskyModels" && BOOT_ARGS+=(--include-risky-models)
bool_true "modelPolicy.minimalWireModel" && BOOT_ARGS+=(--minimal-wire-model)
OPENCLAW_PACKAGE_SPEC="$(json_get "openclaw.packageSpec")"
OPENCLAW_EXPECTED_IDENTITY="$(json_get "openclaw.expectedIdentity")"
OPENCLAW_EXPECTED_BUILD_ID="$(json_get "openclaw.expectedBuildId")"
OPENCLAW_EXPECTED_PACKAGE_VERSION="$(json_get "openclaw.expectedPackageVersion")"
OPENCLAW_IDENTITY_POLICY="$(json_get "openclaw.identityPolicy")"

print_bootstrap_watcher_banner
set_operator_state "bootstrap" "running" "false" "none" "Bootstrap is running in quiet mode; watch logs." "false" "watcher" "tail -f ${RUN_DIR}/bootstrap.log" "Wait for stage completion." "Ctrl+C in installer"
CURRENT_CRITICAL_STAGE="bootstrap"
INSTALL_TERMINAL_RESULT="IN_PROGRESS"
INSTALL_FAILURE_REASON="NONE"
RUNTIME_PROOF_DISPOSITION="BLOCKED_PENDING_BOOTSTRAP"
write_install_terminal_markers
run_stage "bootstrap" "yes" env \
  WIRE_MARKER_DIR="$MARKER_DIR" \
  OPENCLAW_NPM_PACKAGE_SPEC="${OPENCLAW_PACKAGE_SPEC:-openclaw@2026.6.6}" \
  OPENCLAW_EXPECTED_IDENTITY="$OPENCLAW_EXPECTED_IDENTITY" \
  OPENCLAW_EXPECTED_BUILD_ID="$OPENCLAW_EXPECTED_BUILD_ID" \
  OPENCLAW_EXPECTED_PACKAGE_VERSION="$OPENCLAW_EXPECTED_PACKAGE_VERSION" \
  OPENCLAW_IDENTITY_POLICY="${OPENCLAW_IDENTITY_POLICY:-package-version}" \
  bash "$BOOTSTRAP" "${BOOT_ARGS[@]}"
INSTALL_TERMINAL_RESULT="PASS"
INSTALL_FAILURE_REASON="NONE"
RUNTIME_PROOF_DISPOSITION="ELIGIBLE_AFTER_BOOTSTRAP"
write_install_terminal_markers

if bool_true "verification.runBaselineVerifier"; then
  run_stage "baseline_verifier" "yes" bash "$BASELINE" --skip-dashboard
else
  write_status "baseline_verifier" "SKIPPED" "config disabled" ""
fi

if bool_true "verification.runDashboardVerifier" && ! bool_true "verification.skipDashboardVerifier"; then
  DASH_ARGS=()
  DASH_COPY_REQUESTED="NO"
  DASH_OPEN_REQUESTED="NO"
  if bool_true "dashboardAuth.copyAuthUrl"; then DASH_ARGS+=(--copy-auth-url); DASH_COPY_REQUESTED="YES"; fi
  if bool_true "dashboardAuth.openDashboard"; then DASH_ARGS+=(--open-dashboard); DASH_OPEN_REQUESTED="YES"; fi
  bool_true "dashboardAuth.resetGatewayToken" && DASH_ARGS+=(--reset-token)
  DASH_FALLBACK_CMD="powershell -ExecutionPolicy Bypass -File .\\watch_openclaw_wire.ps1 -DistroName \"$(json_get "distroName")\" -CopyDashboardUrl -OpenDashboard"
  print_human_gate_banner "dashboard_verifier" "Dashboard auth helper copy requested: ${DASH_COPY_REQUESTED}; open requested: ${DASH_OPEN_REQUESTED}. If auth helper fails, run fallback: ${DASH_FALLBACK_CMD}. Then send exactly 'Reply with OK only.' and return." "Dashboard browser tab + installer console" "NO" "No token should be pasted into logs. Token is never printed." "Follow verifier prompts, then press ENTER in installer when asked." "Ctrl+C in installer" "${RUN_DIR}/dashboard_verifier.log"
  write_marker "dashboard_prompt_surfaced" "YES"
  set_operator_state "dashboard_verifier" "awaiting_operator" "true" "dashboard_proof" "Complete dashboard auth and send proof prompt." "false" "installer" "tail -f ${RUN_DIR}/dashboard_verifier.log" "Press ENTER when fresh response appears." "Ctrl+C in installer"
  run_stage_interactive "dashboard_verifier" "yes" env WIRE_MARKER_DIR="$MARKER_DIR" bash "$DASHBOARD" "${DASH_ARGS[@]}"
else
  write_status "dashboard_verifier" "SKIPPED" "config skipped" ""
  write_marker "dashboard_prompt_sent" "SKIPPED"
fi

OWNER_ID="$(json_get "discord.ownerId")"
DISCORD_TOKEN_FILE_PATH="$(json_get "discord.tokenFilePath")"
if bool_true "discord.configure"; then
  [[ -n "$OWNER_ID" ]] || die "discord.configure=true but ownerId empty"
  CFG_ARGS=(--owner-id "$OWNER_ID")
  if [[ -n "$DISCORD_TOKEN_FILE_PATH" ]]; then
    CFG_ARGS+=(--token-file "$DISCORD_TOKEN_FILE_PATH")
  fi
  bool_true "discord.refreshToken" && CFG_ARGS+=(--refresh-token)
  bool_true "discord.skipPluginInstall" && CFG_ARGS+=(--skip-plugin-install)
  if [[ -n "$DISCORD_TOKEN_FILE_PATH" ]]; then
    print_human_gate_banner "discord_config" "Using staged local Discord credential file by reference; no token prompt expected." "Installer console" "NO" "Token remains in staged local secret file; no token is printed." "Watch stage complete." "Ctrl+C in installer" "${RUN_DIR}/discord_config.log"
    write_marker "discord_token_prompt_surfaced" "NO"
    set_operator_state "discord_config" "running" "false" "none" "Using staged local Discord token file by reference." "false" "installer" "tail -f ${RUN_DIR}/discord_config.log" "Wait for completion." "Ctrl+C in installer"
    run_stage "discord_config" "yes" env WIRE_MARKER_DIR="$MARKER_DIR" bash "$DISCORD_CFG" "${CFG_ARGS[@]}"
  else
    print_human_gate_banner "discord_config" "Provide Discord bot token when prompted." "Installer console" "YES" "Input is hidden; token is not logged/printed." "Enter token at prompt and continue." "Ctrl+C in installer" "${RUN_DIR}/discord_config.log"
    write_marker "discord_token_prompt_surfaced" "YES"
    set_operator_state "discord_config" "awaiting_operator" "true" "discord_token" "Paste Discord bot token in installer console (hidden input)." "true" "installer" "tail -f ${RUN_DIR}/discord_config.log" "Submit token and continue stage." "Ctrl+C in installer"
    run_stage_interactive "discord_config" "yes" env WIRE_MARKER_DIR="$MARKER_DIR" bash "$DISCORD_CFG" "${CFG_ARGS[@]}"
  fi
  write_marker "discord_token_provided" "YES"
  if bool_true "discord.refreshToken"; then
    write_marker "discord_refresh_token_requested" "YES"
  else
    write_marker "discord_refresh_token_requested" "NO"
  fi
else
  write_status "discord_config" "SKIPPED" "config disabled" ""
  write_marker "discord_token_provided" "SKIPPED"
  write_marker "discord_refresh_token_requested" "SKIPPED"
fi

if bool_true "discord.runVerifier"; then
  [[ -n "$OWNER_ID" ]] || die "discord.runVerifier=true but ownerId empty"
  TOKEN_MARKER_VALUE="$(sed -n 's/^value=//p' "$MARKER_DIR/discord_token_provided.marker" 2>/dev/null | head -n1)"
  REFRESH_MARKER_VALUE="$(sed -n 's/^value=//p' "$MARKER_DIR/discord_refresh_token_requested.marker" 2>/dev/null | head -n1)"
  print_human_gate_banner "discord_verifier" "DM the configured Discord bot exactly 'Reply with DISCORD_SMOKE_OK only.' and approve pairing if prompted." "Discord client + installer console" "NO" "Do not paste secrets; pairing command is non-secret." "Type DISCORD_SMOKE_OK in the installer only after the bot replies." "Ctrl+C in installer" "${RUN_DIR}/discord_verifier.log"
  write_marker "discord_pairing_prompt_surfaced" "YES"
  write_marker "discord_manual_proof_prompt_surfaced" "YES"
  set_operator_state "discord_verifier" "awaiting_operator" "true" "discord_manual_proof" "DM the configured Discord bot exactly: Reply with DISCORD_SMOKE_OK only." "false" "installer" "tail -f ${RUN_DIR}/discord_verifier.log" "Type DISCORD_SMOKE_OK only after the bot replies." "Ctrl+C in installer"
  run_stage_interactive "discord_verifier" "yes" env WIRE_MARKER_DIR="$MARKER_DIR" bash "$DISCORD_VERIFY" --owner-id "$OWNER_ID" --token-provided "${TOKEN_MARKER_VALUE:-UNKNOWN}" --refresh-token-requested "${REFRESH_MARKER_VALUE:-UNKNOWN}"
else
  write_status "discord_verifier" "SKIPPED" "config disabled" ""
  write_marker "discord_pairing_approved" "SKIPPED"
  write_marker "discord_prompt_sent" "SKIPPED"
  write_marker "discordManualMessageProof" "SKIPPED"
fi

if bool_true "discord.runVerifier"; then
  set_operator_state "runtime_readiness" "running" "false" "none" "Restarting gateway and verifying final Discord readiness." "false" "installer" "tail -f ${RUN_DIR}/runtime_readiness.log" "Wait for readiness PASS." "Ctrl+C in installer"
  run_stage "runtime_readiness" "yes" env WIRE_MARKER_DIR="$MARKER_DIR" bash "$RUNTIME_READY"
  DISCORD_TRANSPORT_VALUE="$(sed -n 's/^value=//p' "$MARKER_DIR/discordTransportProof.marker" 2>/dev/null | head -n1)"
  DISCORD_MANUAL_PROOF_VALUE="$(sed -n 's/^value=//p' "$MARKER_DIR/discordManualMessageProof.marker" 2>/dev/null | head -n1)"
  RUNTIME_READINESS_VALUE="$(sed -n 's/^value=//p' "$MARKER_DIR/postInstallRuntimeReadiness.marker" 2>/dev/null | head -n1)"
  FINAL_GATEWAY_VALUE="$(sed -n 's/^value=//p' "$MARKER_DIR/finalGatewayStatus.marker" 2>/dev/null | head -n1)"
  FINAL_DISCORD_VALUE="$(sed -n 's/^value=//p' "$MARKER_DIR/finalDiscordStatus.marker" 2>/dev/null | head -n1)"
  [[ "$DISCORD_TRANSPORT_VALUE" == "PASS" ]] || die "Discord transport proof is not PASS."
  [[ "$DISCORD_MANUAL_PROOF_VALUE" == "PASS" ]] || die "Discord manual message proof is not PASS."
  [[ "$RUNTIME_READINESS_VALUE" == "PASS" ]] || die "Post-install runtime readiness is not PASS."
  [[ "$FINAL_GATEWAY_VALUE" == "ACTIVE" ]] || die "Final gateway status is not ACTIVE."
  [[ "$FINAL_DISCORD_VALUE" == "RUNNING_CONNECTED_WORKS" ]] || die "Final Discord status is not RUNNING_CONNECTED_WORKS."
else
  write_status "runtime_readiness" "SKIPPED" "Discord verifier not requested" ""
  write_marker "postInstallRuntimeReadiness" "SKIPPED"
  write_marker "finalGatewayStatus" "UNKNOWN"
  write_marker "finalDiscordStatus" "SKIPPED"
fi

if bool_true "verification.runOptionalModelVerifier" && [[ -x "$OPTIONAL_VERIFY" ]]; then
  run_stage "optional_model_verifier" "no" bash "$OPTIONAL_VERIFY"
else
  write_status "optional_model_verifier" "NOT_RUN" "not requested" ""
fi

if bool_true "reportPolicy.runWireRatificationReport" || bool_true "supervisedWire.enabled"; then
  set_operator_state "wire_report" "running" "false" "none" "Generating wire report." "false" "installer" "tail -f ${RUN_DIR}/wire_report.log" "Wait for completion." "Ctrl+C in installer"
  run_stage "wire_report" "yes" bash "$REPORT" --run-dir "$RUN_DIR" --config "$CONFIG_PATH"
else
  write_status "wire_report" "SKIPPED" "config disabled" ""
fi

ARCHIVE="${HOME}/openclaw_wire_v1_7_${STAMP}.tar.gz"
tar -czf "$ARCHIVE" -C "$LOG_ROOT" "$STAMP"

for d in "/mnt/c/Users/${WINUSER:-}/Downloads" /mnt/c/Users/accou/Downloads /mnt/c/Users/*/Downloads; do
  [[ -d "$d" && -w "$d" ]] || continue
  case "$d" in *"Default User"*|*"All Users"*|*"Public"*) continue ;; esac
  cp "$ARCHIVE" "$d/" || true
  log "Final evidence archive copied to: $d/$(basename "$ARCHIVE")"
  break
done

log "Supervised wire run complete"
log "Status dir: $STATUS_DIR"
set_operator_state "complete" "done" "false" "none" "Run completed; inspect report and status markers." "false" "installer" "tail -n 120 ${RUN_DIR}/runner.log" "Review final report." "N/A"

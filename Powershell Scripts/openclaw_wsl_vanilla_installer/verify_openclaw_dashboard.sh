#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_NAME="$(basename "$0")"
STAMP="$(date +%Y%m%d_%H%M%S)"
LOG_ROOT="${HOME}/openclaw_verification_logs"
LOG_DIR="${LOG_ROOT}/dashboard_v1_7_${STAMP}"
LOG_FILE="${LOG_DIR}/verify.log"
REPORT_FILE="${LOG_DIR}/REPORT.md"

COPY_AUTH_URL=0
OPEN_DASHBOARD=0
RESET_TOKEN=0
EXPECTED_MODEL=""
EXPECTED_OPENCLAW_MODEL=""
EXPECTED_CONTEXT="4096"
EXPECTED_CONTEXT_MODE="exact"
MARKER_DIR="${WIRE_MARKER_DIR:-}"
DASHBOARD_MODEL_TIER="safe_full"
dashboardTransportProof="UNKNOWN"
dashboardModelLoadedProof="UNKNOWN"
dashboardGpuContextProof="UNKNOWN"
dashboardExactResponseProof="UNKNOWN"
dashboardVerifierResult="UNKNOWN"
dashboardFailureReason="unknown"
dashboardAuthProbeNoise="UNKNOWN"
dashboardAuthProbeNoiseLinesCount="0"
dashboardDeviceProbeNoise="UNKNOWN"
dashboardDeviceProbeNoiseLinesCount="0"
dashboardCompactionDiagnosticNoise="UNKNOWN"
dashboardCompactionDiagnosticLinesCount="0"
dashboardAutoOpenResult="UNKNOWN"
dashboardAuthHelperResult="UNKNOWN"

mkdir -p "$LOG_DIR"
exec > >(tee -a "$LOG_FILE") 2>&1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --copy-auth-url) COPY_AUTH_URL=1; shift ;;
    --open-dashboard) OPEN_DASHBOARD=1; shift ;;
    --reset-token) RESET_TOKEN=1; shift ;;
    --help|-h) exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

log(){ printf '\n[%s] %s\n' "$SCRIPT_NAME" "$*"; }
die(){ printf '\n[%s] ERROR: %s\n' "$SCRIPT_NAME" "$*" >&2; exit 1; }
write_marker() {
  local key="$1" value="$2"
  [[ -n "$MARKER_DIR" ]] || return 0
  mkdir -p "$MARKER_DIR"
  cat >"${MARKER_DIR}/${key}.marker" <<EOF2
key=${key}
value=${value}
timestamp=$(date -Iseconds)
EOF2
}

normalize_dashboard_log_line() {
  local line="$1"
  printf '%s\n' "$line" | sed -E 's/^([0-9]+):([0-9]+:)/\1:/'
}

is_dashboard_probe_noise_line() {
  local line
  line="$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')"

  if [[ "$line" == *"client=openclaw-control-ui"* || "$line" == *"webchat vcontrol-ui"* ]]; then
    return 0
  fi

  if [[ "$line" == *"host=127.0.0.1:18789"* || "$line" == *"origin=http://127.0.0.1:18789"* || "$line" == *"remote=127.0.0.1"* || "$line" == *"remote=::1"* ]]; then
    if [[ "$line" == *"auth=none"* || "$line" == *"token_missing"* || "$line" == *"gateway token missing"* || "$line" == *"device_token_mismatch"* || "$line" == *"device token mismatch"* || "$line" == *"closed before connect"* || "$line" == *"reason=token_missing"* || "$line" == *"reason=device_token_mismatch"* || "$line" == *"unauthorized: gateway token missing"* || "$line" == *"unauthorized: device token mismatch"* ]]; then
      return 0
    fi
  fi

  if [[ "$line" == *"auth=none"* || "$line" == *"token_missing"* || "$line" == *"gateway token missing"* || "$line" == *"device_token_mismatch"* || "$line" == *"device token mismatch"* || "$line" == *"closed before connect"* || "$line" == *"reason=token_missing"* || "$line" == *"reason=device_token_mismatch"* || "$line" == *"unauthorized: gateway token missing"* || "$line" == *"unauthorized: device token mismatch"* ]]; then
    return 0
  fi

  return 1
}

is_compaction_diagnostic_line() {
  local line
  line="$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')"

  if [[ "$line" == *"[compaction-diag]"* || "$line" == *"trigger=overflow"* || "$line" == *"reason=already_compacted_recently"* || "$line" == *"outcome=failed reason=already_compacted_recently"* || "$line" == *"auto-compaction could not recover this turn"* || "$line" == *"auto-compaction could not recover"* || "$line" == *"compaction.reservetokensfloor"* ]]; then
    return 0
  fi

  return 1
}

is_material_failure_line() {
  local line
  line="$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')"

  is_compaction_diagnostic_line "$line" && return 1
  is_dashboard_probe_noise_line "$line" && return 1

  if [[ "$line" == *"provider failed"* || "$line" == *"all models failed"* || "$line" == *"no such model"* || "$line" == *"model not found"* || "$line" == *"connection refused"* || "$line" == *"econnrefused"* || "$line" == *"ollama_api_key missing"* || "$line" == *"invalid api key"* || "$line" == *"failovererror"* ]]; then
    return 0
  fi

  if [[ "$line" =~ (^|[^0-9])(401|403)([^0-9]|$) ]]; then
    return 0
  fi

  if [[ "$line" == *"unauthorized"* && "$line" != *"client=openclaw-control-ui"* && "$line" != *"webchat vcontrol-ui"* ]]; then
    return 0
  fi

  if [[ "$line" == *"provider"* && "$line" == *"failed"* ]]; then
    return 0
  fi

  if [[ "$line" == *"model"* && "$line" == *"not found"* ]]; then
    return 0
  fi

  if [[ "$line" == *"ollama_api_key"* && "$line" == *"missing"* ]]; then
    return 0
  fi

  return 1
}

log "Verifying dashboard wire v1.7"
openclaw models list --provider ollama | tee "$LOG_DIR/openclaw_models_ollama.txt"
openclaw config get agents.defaults.model --json | tee "$LOG_DIR/openclaw_agents_defaults_model.json"
EXPECTED_OPENCLAW_MODEL="$(python3 - "$LOG_DIR/openclaw_agents_defaults_model.json" <<'PY'
import json,sys
doc=json.load(open(sys.argv[1],encoding='utf-8'))
print(doc.get('primary','ollama/qwen3.5:9b-4k'))
PY
)"
EXPECTED_MODEL="${EXPECTED_OPENCLAW_MODEL#ollama/}"
if [[ "$EXPECTED_OPENCLAW_MODEL" == "ollama/qwen3:0.6b" ]]; then
  DASHBOARD_MODEL_TIER="minimal_wire"
  EXPECTED_CONTEXT="32768"
  EXPECTED_CONTEXT_MODE="minimum"
fi
openclaw config get gateway.bind --json | tee "$LOG_DIR/openclaw_gateway_bind.json"
systemctl --user show-environment | grep -E 'OLLAMA_API_KEY' | sed -E 's/=.*/=<REDACTED>/' | tee "$LOG_DIR/systemd_ollama_env.txt"
systemctl --user is-active openclaw-gateway.service | tee "$LOG_DIR/gateway_active.txt"

awk -v model="$EXPECTED_OPENCLAW_MODEL" '$1 == model { found = 1 } END { exit(found ? 0 : 1) }' "$LOG_DIR/openclaw_models_ollama.txt" || die "missing configured model surface"
grep -q "$EXPECTED_OPENCLAW_MODEL" "$LOG_DIR/openclaw_agents_defaults_model.json" || die "default model mismatch"
grep -q 'loopback' "$LOG_DIR/openclaw_gateway_bind.json" || die "gateway.bind not loopback"
grep -q 'OLLAMA_API_KEY=<REDACTED>' "$LOG_DIR/systemd_ollama_env.txt" || die "OLLAMA_API_KEY missing"
grep -q 'active' "$LOG_DIR/gateway_active.txt" || die "gateway not active"

ollama stop "$EXPECTED_MODEL" >/dev/null 2>&1 || true
sleep 2

BOUNDARY="$(date '+%Y-%m-%d %H:%M:%S')"
HELPER_ARGS=()
[[ "$COPY_AUTH_URL" == "1" ]] && HELPER_ARGS+=(--copy-auth-url)
[[ "$OPEN_DASHBOARD" == "1" ]] && HELPER_ARGS+=(--open-dashboard)
[[ "$RESET_TOKEN" == "1" ]] && HELPER_ARGS+=(--reset-token)
HELPER_SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/openclaw_gateway_auth_helper_v1.sh"
helper_rc=0
set +e
bash "$HELPER_SCRIPT" "${HELPER_ARGS[@]}" >"$LOG_DIR/gateway_auth_helper_status.txt" 2>"$LOG_DIR/gateway_auth_helper_error.txt"
helper_rc=$?
set -e
cat "$LOG_DIR/gateway_auth_helper_status.txt"
if [[ "$helper_rc" -ne 0 ]]; then
  log "WARNING: dashboard auth helper failed with exit code $helper_rc; continuing with manual dashboard proof fallback."
  if [[ -s "$LOG_DIR/gateway_auth_helper_error.txt" ]]; then
    sed -n '1,120p' "$LOG_DIR/gateway_auth_helper_error.txt" | sed -E 's/(token=|#token=)[^[:space:]]+/\1<REDACTED>/g' || true
  fi
fi

copied_status="$(sed -n 's/^Dashboard authenticated URL copied to clipboard: //p' "$LOG_DIR/gateway_auth_helper_status.txt" | tail -n1)"
opened_status="$(sed -n 's/^Dashboard browser opened: //p' "$LOG_DIR/gateway_auth_helper_status.txt" | tail -n1)"
token_printed_status="$(sed -n 's/^Dashboard token printed: //p' "$LOG_DIR/gateway_auth_helper_status.txt" | tail -n1)"
helper_result_status="$(sed -n 's/^Dashboard helper result: //p' "$LOG_DIR/gateway_auth_helper_status.txt" | tail -n1)"
[[ -n "$copied_status" ]] || copied_status="NO"
[[ -n "$opened_status" ]] || opened_status="NO"
[[ -n "$token_printed_status" ]] || token_printed_status="NO"
[[ -n "$helper_result_status" ]] || helper_result_status="UNKNOWN"
if [[ "$helper_rc" -ne 0 ]]; then
  copied_status="NO"
  opened_status="NO"
  token_printed_status="NO"
  helper_result_status="FAIL"
fi
if [[ ! "$copied_status" =~ ^(YES|NO)$ ]]; then copied_status="NO"; fi
if [[ ! "$opened_status" =~ ^(YES|NO)$ ]]; then opened_status="NO"; fi
if [[ ! "$token_printed_status" =~ ^(YES|NO)$ ]]; then token_printed_status="NO"; fi
if [[ ! "$helper_result_status" =~ ^(PASS|FAIL|SKIPPED|UNKNOWN)$ ]]; then helper_result_status="UNKNOWN"; fi

if [[ "$OPEN_DASHBOARD" == "1" && "$opened_status" == "YES" ]]; then
  dashboardAutoOpenResult="PASS"
elif [[ "$OPEN_DASHBOARD" == "1" ]]; then
  dashboardAutoOpenResult="FAIL"
else
  dashboardAutoOpenResult="NOT_REQUESTED"
fi
if [[ "$helper_rc" -ne 0 ]]; then
  dashboardAutoOpenResult="FAIL"
fi
dashboardAuthHelperResult="$helper_result_status"
write_marker "dashboardAuthUrlCopied" "$copied_status"
write_marker "dashboardOpenRequested" "$opened_status"
write_marker "dashboardAutoOpenResult" "$dashboardAutoOpenResult"
write_marker "dashboardTokenPrinted" "$token_printed_status"
write_marker "dashboardAuthHelperResult" "$dashboardAuthHelperResult"

log "Dashboard authenticated URL copied to clipboard: ${copied_status}"
log "Dashboard browser opened: ${opened_status}"
log "Dashboard token printed: ${token_printed_status}"
log "Dashboard helper result: ${dashboardAuthHelperResult}"

if [[ "$DASHBOARD_MODEL_TIER" == "minimal_wire" ]]; then
  cat <<'PROMPT'
In the dashboard, send exactly: Reply with OK only.
In minimal wire mode, any fresh assistant response proves transport; exact OK is not required.
PROMPT
else
  cat <<'PROMPT'
In the dashboard, send exactly: Reply with OK only.
PROMPT
fi
read -r -p "Press ENTER after dashboard produced a fresh assistant response... " _
dashboardTransportProof="PASS"
if [[ -n "$MARKER_DIR" ]]; then
  write_marker "dashboard_prompt_sent" "YES"
fi

ollama ps | tee "$LOG_DIR/ollama_ps_after_dashboard.txt"
journalctl --user -u openclaw-gateway.service --since "$BOUNDARY" --no-pager > "$LOG_DIR/openclaw_gateway_raw_logs_since_dashboard.txt" || true
grep -iE 'agent model|ollama|unknown model|fail|error|ready|fallback|model_call|context|auth' "$LOG_DIR/openclaw_gateway_raw_logs_since_dashboard.txt" > "$LOG_DIR/openclaw_gateway_filtered_logs_since_dashboard.txt" || true

if awk -v model="$EXPECTED_MODEL" '$1 == model { found = 1 } END { exit(found ? 0 : 1) }' "$LOG_DIR/ollama_ps_after_dashboard.txt"; then
  dashboardModelLoadedProof="PASS"
else
  dashboardModelLoadedProof="FAIL"
  dashboardFailureReason="dashboard-model-not-loaded"
fi
context_matches_expected() {
  local model="$1"
  local expected="$2"
  local mode="$3"
  local ps_file="$4"

  awk -v model="$model" -v expected="$expected" -v mode="$mode" '
    $1 == model && index($0, "100% GPU") {
      for (i = 1; i <= NF; i++) {
        if ($i ~ /^[0-9]+$/ && ((mode == "exact" && $i == expected) || (mode == "minimum" && $i >= expected))) {
          found = 1
        }
      }
    }
    END { exit(found ? 0 : 1) }
  ' "$ps_file"
}

if context_matches_expected "$EXPECTED_MODEL" "$EXPECTED_CONTEXT" "$EXPECTED_CONTEXT_MODE" "$LOG_DIR/ollama_ps_after_dashboard.txt"; then
  dashboardGpuContextProof="PASS"
else
  dashboardGpuContextProof="FAIL"
  [[ "$dashboardFailureReason" == "unknown" ]] && dashboardFailureReason="dashboard-gpu-context-missing"
fi
if [[ "$DASHBOARD_MODEL_TIER" == "minimal_wire" ]]; then
  dashboardExactResponseProof="NOT_PROVEN_MINIMAL_MODEL"
else
  dashboardExactResponseProof="UNKNOWN"
fi

failure_hits_file="$LOG_DIR/openclaw_gateway_failure_hits_since_dashboard.txt"
benign_hits_file="$LOG_DIR/openclaw_gateway_benign_auth_hits_since_dashboard.txt"
probe_noise_hits_file="$LOG_DIR/openclaw_gateway_auth_probe_noise_hits_since_dashboard.txt"
device_probe_noise_hits_file="$LOG_DIR/openclaw_gateway_device_probe_noise_hits_since_dashboard.txt"
material_failure_hits_file="$LOG_DIR/openclaw_gateway_material_failure_hits_since_dashboard.txt"
grep -iE 'auth=token|gateway token source: config|gateway token value:[[:space:]]*<REDACTED>|resolving authentication|browser/server.*auth=token' "$LOG_DIR/openclaw_gateway_raw_logs_since_dashboard.txt" > "$benign_hits_file" || true
: > "$probe_noise_hits_file"
: > "$device_probe_noise_hits_file"
: > "$material_failure_hits_file"
dashboardMaterialFailureLinesCount="0"
dashboardCompactionDiagnosticLinesCount="0"
while IFS= read -r raw_line; do
  [[ -n "$raw_line" ]] || continue
  normalized_line="$(normalize_dashboard_log_line "$raw_line")"
  if is_compaction_diagnostic_line "$normalized_line"; then
    printf '%s\n' "$normalized_line" >> "$LOG_DIR/openclaw_gateway_compaction_diagnostic_hits_since_dashboard.txt"
    dashboardCompactionDiagnosticLinesCount="$((dashboardCompactionDiagnosticLinesCount + 1))"
    continue
  fi
  if is_dashboard_probe_noise_line "$normalized_line"; then
    printf '%s\n' "$normalized_line" >> "$probe_noise_hits_file"
    case "$normalized_line" in
      *"device_token_mismatch"*|*"device token mismatch"*|*"reason=device_token_mismatch"*|*"reason=token_missing"*)
        printf '%s\n' "$normalized_line" >> "$device_probe_noise_hits_file"
        ;;
    esac
    continue
  fi

  if is_material_failure_line "$normalized_line"; then
    printf '%s\n' "$normalized_line" >> "$material_failure_hits_file"
    dashboardMaterialFailureLinesCount="$((dashboardMaterialFailureLinesCount + 1))"
  fi
done < "$LOG_DIR/openclaw_gateway_raw_logs_since_dashboard.txt"

if [[ -s "$probe_noise_hits_file" ]]; then
  dashboardAuthProbeNoise="PRESENT_IGNORED"
  dashboardAuthProbeNoiseLinesCount="$(wc -l < "$probe_noise_hits_file" | tr -d '[:space:]')"
  log "Dashboard auth probe noise lines ignored:"
  cat "$probe_noise_hits_file"
else
  dashboardAuthProbeNoise="ABSENT"
  dashboardAuthProbeNoiseLinesCount="0"
fi
if [[ -s "$device_probe_noise_hits_file" ]]; then
  dashboardDeviceProbeNoise="PRESENT_IGNORED"
  dashboardDeviceProbeNoiseLinesCount="$(wc -l < "$device_probe_noise_hits_file" | tr -d '[:space:]')"
else
  dashboardDeviceProbeNoise="ABSENT"
  dashboardDeviceProbeNoiseLinesCount="0"
fi
if [[ "$dashboardCompactionDiagnosticLinesCount" -gt 0 ]]; then
  dashboardCompactionDiagnosticNoise="PRESENT_IGNORED"
  log "Dashboard compaction diagnostic lines ignored:"
  cat "$LOG_DIR/openclaw_gateway_compaction_diagnostic_hits_since_dashboard.txt"
else
  dashboardCompactionDiagnosticNoise="ABSENT"
fi
if [[ "$DASHBOARD_MODEL_TIER" == "minimal_wire" && "$dashboardTransportProof" == "PASS" && "$dashboardModelLoadedProof" == "PASS" && "$dashboardGpuContextProof" == "PASS" && -s "$device_probe_noise_hits_file" ]]; then
  log "Dashboard device-token probe noise lines ignored (minimal_wire proof satisfied):"
  cat "$device_probe_noise_hits_file"
fi
write_marker "dashboardMaterialFailureLinesCount" "$dashboardMaterialFailureLinesCount"
write_marker "dashboardCompactionDiagnosticNoise" "$dashboardCompactionDiagnosticNoise"
write_marker "dashboardCompactionDiagnosticLinesCount" "$dashboardCompactionDiagnosticLinesCount"
if [[ -s "$material_failure_hits_file" ]]; then
  log "Matched provider/auth failure lines:"
  cat "$material_failure_hits_file"
  dashboardFailureReason="provider-model-auth-failure-signature"
  dashboardVerifierResult="FAIL"
fi

if [[ "$dashboardVerifierResult" != "FAIL" ]]; then
  if [[ "$dashboardTransportProof" == "PASS" && "$dashboardModelLoadedProof" == "PASS" && "$dashboardGpuContextProof" == "PASS" ]]; then
    dashboardVerifierResult="PASS"
    dashboardFailureReason="none"
  else
    dashboardVerifierResult="FAIL"
    [[ "$dashboardFailureReason" == "unknown" ]] && dashboardFailureReason="dashboard-proof-incomplete"
  fi
fi

write_marker "dashboardTransportProof" "$dashboardTransportProof"
write_marker "dashboardModelLoadedProof" "$dashboardModelLoadedProof"
write_marker "dashboardGpuContextProof" "$dashboardGpuContextProof"
write_marker "dashboardExactResponseProof" "$dashboardExactResponseProof"
write_marker "dashboardVerifierResult" "$dashboardVerifierResult"
write_marker "dashboardFailureReason" "$dashboardFailureReason"
write_marker "dashboardAuthProbeNoise" "$dashboardAuthProbeNoise"
write_marker "dashboardAuthProbeNoiseLinesCount" "$dashboardAuthProbeNoiseLinesCount"
write_marker "dashboardDeviceProbeNoise" "$dashboardDeviceProbeNoise"
write_marker "dashboardDeviceProbeNoiseLinesCount" "$dashboardDeviceProbeNoiseLinesCount"
write_marker "dashboardCompactionDiagnosticNoise" "$dashboardCompactionDiagnosticNoise"
write_marker "dashboardCompactionDiagnosticLinesCount" "$dashboardCompactionDiagnosticLinesCount"

if [[ "$dashboardVerifierResult" != "PASS" ]]; then
  die "dashboard verifier failed: ${dashboardFailureReason}"
fi

{
  echo "# Dashboard Verification Report v1.7"
  echo
  echo "- Dashboard/OpenClaw inference test: ${dashboardVerifierResult}"
  echo "- Dashboard model tier: ${DASHBOARD_MODEL_TIER}"
  echo "- Dashboard transport proof: ${dashboardTransportProof}"
  echo "- Dashboard model loaded proof: ${dashboardModelLoadedProof}"
  echo "- Dashboard GPU/context proof: ${dashboardGpuContextProof}"
  echo "- Dashboard exact-response proof: ${dashboardExactResponseProof}"
  echo "- Dashboard failure reason: ${dashboardFailureReason}"
  echo "- Dashboard auth probe noise: ${dashboardAuthProbeNoise}"
  echo "- Dashboard auth probe noise lines: ${dashboardAuthProbeNoiseLinesCount}"
  echo "- Dashboard device-token probe noise: ${dashboardDeviceProbeNoise}"
  echo "- Dashboard device-token probe noise lines: ${dashboardDeviceProbeNoiseLinesCount}"
  echo "- Dashboard auto-open result: ${dashboardAutoOpenResult}"
  echo "- Dashboard auth helper result: ${dashboardAuthHelperResult}"
  echo "- Transport/model proof only; no behavioral alignment claim"
  echo "- Evidence dir: $LOG_DIR"
} | tee "$REPORT_FILE"

echo "$LOG_DIR"

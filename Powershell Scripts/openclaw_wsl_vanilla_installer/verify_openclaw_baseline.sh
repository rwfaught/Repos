#!/usr/bin/env bash
# verify_openclaw_baseline.sh
#
# Post-bootstrap verification tool for REDO WSL OPENCLAW v1.1.
#
# Purpose:
#   Verify that the fresh WSL/OpenClaw/Ollama install is using the selected
#   explicit Ollama provider surface:
#
#     safe_full: ollama/qwen3.5:9b-4k, CONTEXT 4096
#     minimal_wire: ollama/qwen3:0.6b, CONTEXT 32768 or larger
#
# This is intentionally a verification tool, not part of the full installer yet.
#
# Usage:
#   bash verify_openclaw_baseline.sh
#
# Non-interactive direct checks only:
#   bash verify_openclaw_baseline.sh --skip-dashboard
#
# The dashboard portion still requires you to send one tiny prompt in the browser:
#   Reply with OK only.

set -Eeuo pipefail

SCRIPT_NAME="$(basename "$0")"
STAMP="$(date +%Y%m%d_%H%M%S)"
LOG_ROOT="${HOME}/openclaw_verification_logs"
LOG_DIR="${LOG_ROOT}/${STAMP}"
LOG_FILE="${LOG_DIR}/verify.log"
REPORT_FILE="${LOG_DIR}/REPORT.md"

SKIP_DASHBOARD=0
PROMPT_TEXT="Reply with OK only."
EXPECTED_MODEL="qwen3.5:9b-4k"
EXPECTED_OPENCLAW_MODEL="ollama/qwen3.5:9b-4k"
EXPECTED_CONTEXT="4096"
EXPECTED_CONTEXT_MODE="exact"

mkdir -p "$LOG_DIR"
exec > >(tee -a "$LOG_FILE") 2>&1

log() {
  printf '\n[%s] %s\n' "$SCRIPT_NAME" "$*"
}

warn() {
  printf '\n[%s] WARNING: %s\n' "$SCRIPT_NAME" "$*" >&2
}

die() {
  printf '\n[%s] ERROR: %s\n' "$SCRIPT_NAME" "$*" >&2
  printf '[%s] Log preserved at: %s\n' "$SCRIPT_NAME" "$LOG_FILE" >&2
  exit 1
}

usage() {
  cat <<'EOF'
Usage:
  bash verify_openclaw_baseline.sh [options]

Options:
  --skip-dashboard       Run only local/direct checks; skip browser dashboard test.
  --help                 Show this help.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-dashboard) SKIP_DASHBOARD=1; shift ;;
    --help|-h) usage; exit 0 ;;
    *) die "Unknown option: $1" ;;
  esac
done

on_error() {
  local rc=$?
  log "FAILED with exit code $rc"
  log "Log preserved at: $LOG_FILE"
  exit "$rc"
}
trap on_error ERR

run_capture() {
  local label="$1"
  local outfile="$2"
  shift 2

  log "$label"
  {
    echo "## $label"
    echo "## Started: $(date -Iseconds)"
    echo "## Command: $*"
    echo
    "$@"
    rc=$?
    echo
    echo "## Exit code: $rc"
    echo "## Finished: $(date -Iseconds)"
    return "$rc"
  } | tee "$outfile"
}

run_shell_capture() {
  local label="$1"
  local outfile="$2"
  local cmd="$3"

  log "$label"
  {
    echo "## $label"
    echo "## Started: $(date -Iseconds)"
    echo "## Command: $cmd"
    echo
    bash -lc "$cmd"
    rc=$?
    echo
    echo "## Exit code: $rc"
    echo "## Finished: $(date -Iseconds)"
    return "$rc"
  } | tee "$outfile"
}

check_command() {
  command -v "$1" >/dev/null 2>&1 || die "Required command not found: $1"
}

log "Starting OpenClaw/Ollama 4K verification"
log "Log file: $LOG_FILE"

check_command openclaw
check_command ollama
check_command systemctl
check_command journalctl

if [[ -x /usr/lib/wsl/lib/nvidia-smi ]]; then
  export PATH="/usr/lib/wsl/lib:$PATH"
fi

log "Basic identity"
{
  echo "date=$(date -Iseconds)"
  echo "user=$(whoami)"
  echo "host=$(hostname)"
  echo "shell=${SHELL:-unknown}"
  echo "pwd=$(pwd)"
  echo
  echo "wsl_kernel=$(uname -a)"
  echo
  echo "openclaw=$(openclaw --version 2>/dev/null || true)"
  echo "ollama=$(ollama --version 2>/dev/null || true)"
  echo
  if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi -L || true
  elif [[ -x /usr/lib/wsl/lib/nvidia-smi ]]; then
    /usr/lib/wsl/lib/nvidia-smi -L || true
  else
    echo "nvidia-smi not found"
  fi
} | tee "$LOG_DIR/identity.txt"

log "Stopping any loaded models before verification"
ollama stop qwen3:30b-thinking-4k >/dev/null 2>&1 || true
ollama stop qwen3:30b-thinking >/dev/null 2>&1 || true
ollama stop qwen3.6:35b >/dev/null 2>&1 || true
ollama stop qwen3-coder:30b >/dev/null 2>&1 || true
ollama stop "$EXPECTED_MODEL" >/dev/null 2>&1 || true
sleep 2

run_capture "OpenClaw Ollama model list" "$LOG_DIR/openclaw_models_ollama.txt" openclaw models list --provider ollama
DEFAULT_MODEL_JSON_RAW="$LOG_DIR/openclaw_agents_defaults_model.raw.json"
DEFAULT_MODEL_JSON_ERR="$LOG_DIR/openclaw_agents_defaults_model.raw.err"
log "OpenClaw default model config (raw JSON capture)"
if ! openclaw config get agents.defaults.model --json >"$DEFAULT_MODEL_JSON_RAW" 2>"$DEFAULT_MODEL_JSON_ERR"; then
  cat "$DEFAULT_MODEL_JSON_ERR" | tee "$LOG_DIR/openclaw_agents_defaults_model.json" || true
  die "default-model-json-command-failed"
fi
if [[ ! -s "$DEFAULT_MODEL_JSON_RAW" ]]; then
  die "default-model-json-empty"
fi
cat "$DEFAULT_MODEL_JSON_RAW" | tee "$LOG_DIR/openclaw_agents_defaults_model.json"
parse_out="$(python3 - "$DEFAULT_MODEL_JSON_RAW" <<'PY'
import json,sys
path=sys.argv[1]
try:
    doc=json.load(open(path,encoding='utf-8'))
except Exception:
    print("PARSE_STATUS=INVALID")
    raise SystemExit(0)
primary=str(doc.get("primary",""))
fallbacks=doc.get("fallbacks",None)
if not isinstance(fallbacks,list):
    print("PARSE_STATUS=INVALID")
    raise SystemExit(0)
safe_required={"ollama/qwen3.5:4b-4k","ollama/qwen3.5:2b-4k","ollama/qwen3:0.6b-4k"}
if primary=="ollama/qwen3:0.6b" and len(fallbacks)==0:
    tier="minimal_wire"
elif primary=="ollama/qwen3.5:9b-4k" and safe_required.issubset(set(str(x) for x in fallbacks)):
    tier="safe_full"
else:
    print("PARSE_STATUS=UNSUPPORTED")
    raise SystemExit(0)
print("PARSE_STATUS=OK")
print(f"PRIMARY={primary}")
print(f"TIER={tier}")
PY
)"
if ! grep -q '^PARSE_STATUS=OK$' <<<"$parse_out"; then
  if grep -q '^PARSE_STATUS=INVALID$' <<<"$parse_out"; then
    die "default-model-json-invalid"
  fi
  die "default-model-json-unsupported"
fi
EXPECTED_OPENCLAW_MODEL="$(awk -F= '/^PRIMARY=/{print $2}' <<<"$parse_out")"
MODEL_TIER="$(awk -F= '/^TIER=/{print $2}' <<<"$parse_out")"
EXPECTED_MODEL="${EXPECTED_OPENCLAW_MODEL#ollama/}"
if [[ "$MODEL_TIER" == "minimal_wire" ]]; then
  EXPECTED_CONTEXT="32768"
  EXPECTED_CONTEXT_MODE="minimum"
fi
log "Detected default model tier: ${MODEL_TIER} primary=${EXPECTED_OPENCLAW_MODEL}"
ollama stop "$EXPECTED_MODEL" >/dev/null 2>&1 || true
run_capture "OpenClaw gateway bind" "$LOG_DIR/openclaw_gateway_bind.json" openclaw config get gateway.bind --json
run_shell_capture "OpenClaw user environment" "$LOG_DIR/systemd_user_environment.txt" "systemctl --user show-environment | grep -E 'OLLAMA|OPENCLAW|CUDA' || true"
run_capture "Ollama list" "$LOG_DIR/ollama_list.txt" ollama list
run_capture "Ollama ps before direct test" "$LOG_DIR/ollama_ps_before.txt" ollama ps

log "Asserting OpenClaw configured provider surface"
awk -v model="$EXPECTED_OPENCLAW_MODEL" '$1 == model { found = 1 } END { exit(found ? 0 : 1) }' "$LOG_DIR/openclaw_models_ollama.txt" || die "OpenClaw model list does not include $EXPECTED_OPENCLAW_MODEL"
if [[ "$MODEL_TIER" == "safe_full" ]]; then
  grep -qiE '\b4k\b|4096' "$LOG_DIR/openclaw_models_ollama.txt" || die "OpenClaw safe-full model list does not show bounded 4k context."
fi
grep -qi 'Auth.*yes\|yes.*default' "$LOG_DIR/openclaw_models_ollama.txt" || warn "Could not confidently parse Auth yes/default from model list; inspect $LOG_DIR/openclaw_models_ollama.txt"
grep -q "$EXPECTED_OPENCLAW_MODEL" "$LOG_DIR/openclaw_agents_defaults_model.json" || die "OpenClaw default model is not $EXPECTED_OPENCLAW_MODEL"
grep -q 'loopback' "$LOG_DIR/openclaw_gateway_bind.json" || die "gateway.bind is not loopback"
grep -q 'OLLAMA_API_KEY=ollama-local' "$LOG_DIR/systemd_user_environment.txt" || die "OLLAMA_API_KEY=ollama-local not present in systemd user environment."

log "Direct Ollama bounded model test"
DIRECT_SINCE="$(date '+%Y-%m-%d %H:%M:%S')"
{
  echo "## Direct Ollama prompt"
  echo "## Started: $(date -Iseconds)"
  echo "## Model: $EXPECTED_MODEL"
  echo "## Prompt: $PROMPT_TEXT"
  echo
  timeout 120s ollama run "$EXPECTED_MODEL" "$PROMPT_TEXT"
  echo
  echo "## Finished: $(date -Iseconds)"
} | tee "$LOG_DIR/direct_ollama_output.txt"

run_capture "Ollama ps after direct test" "$LOG_DIR/ollama_ps_after_direct.txt" ollama ps
run_shell_capture "Ollama logs since direct test" "$LOG_DIR/ollama_logs_since_direct.txt" \
  "sudo journalctl -u ollama --since '$DIRECT_SINCE' --no-pager | grep -iE 'cuda|gpu|nvidia|library|llm|offload|cpu|error|warn|num_ctx|context|kv|layers' || true"

log "Asserting direct Ollama GPU/context behavior"
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
context_matches_expected "$EXPECTED_MODEL" "$EXPECTED_CONTEXT" "$EXPECTED_CONTEXT_MODE" "$LOG_DIR/ollama_ps_after_direct.txt" || die "$EXPECTED_MODEL did not show expected GPU/context policy after direct test."

if [[ "$SKIP_DASHBOARD" == "1" ]]; then
  warn "Skipping dashboard/OpenClaw inference test by request."
  DASHBOARD_RESULT="skipped"
else
  log "Dashboard/OpenClaw inference test"

  log "Stopping loaded model before dashboard test so dashboard must reload it"
  ollama stop "$EXPECTED_MODEL" >/dev/null 2>&1 || true
  sleep 3
  run_capture "Ollama ps before dashboard test" "$LOG_DIR/ollama_ps_before_dashboard.txt" ollama ps
  if awk -v model="$EXPECTED_MODEL" '$1 == model { found = 1 } END { exit(found ? 0 : 1) }' "$LOG_DIR/ollama_ps_before_dashboard.txt"; then
    warn "$EXPECTED_MODEL still appears loaded before dashboard test. Continuing, but dashboard proof may be weaker."
  fi

  DASHBOARD_SINCE="$(date '+%Y-%m-%d %H:%M:%S')"

  cat <<EOF

The script will now open or prepare the OpenClaw dashboard.

In the browser, send exactly this prompt in the OpenClaw chat/control input:

  $PROMPT_TEXT

Wait until you see a fresh assistant response. Then return to this terminal and press ENTER.

If you cannot authenticate to the dashboard, stop here and fix dashboard access before pressing ENTER.

EOF

  # Run dashboard command. It usually copies an auto-auth URL to the Windows clipboard.
  openclaw dashboard | tee "$LOG_DIR/openclaw_dashboard_command.txt" || true

  # Try to open the copied auto-auth URL from the Windows clipboard, if available.
  if command -v powershell.exe >/dev/null 2>&1; then
    log "Attempting to open dashboard from Windows clipboard"
    powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "\$u = Get-Clipboard; if (\$u -match '^https?://(localhost|127\.0\.0\.1):18789') { Start-Process \$u } else { Start-Process 'http://localhost:18789/' }" >/dev/null 2>&1 || true
  else
    warn "powershell.exe not found. Open http://localhost:18789/ manually in Windows."
  fi

  read -r -p "Press ENTER only after sending the dashboard prompt and receiving a fresh reply... " _

  run_capture "Ollama ps after dashboard test" "$LOG_DIR/ollama_ps_after_dashboard.txt" ollama ps

  log "Capturing raw OpenClaw gateway logs since dashboard test"
  {
    echo "## OpenClaw gateway raw logs since dashboard test"
    echo "## Started: $(date -Iseconds)"
    echo
    journalctl --user -u openclaw-gateway.service --since "$DASHBOARD_SINCE" --no-pager || true
    echo
    echo "## Finished: $(date -Iseconds)"
  } | tee "$LOG_DIR/openclaw_gateway_raw_logs_since_dashboard.txt"

  # Filter separately for human inspection. Do not run failure assertions against this
  # wrapper file, because the old verifier accidentally matched words inside its own
  # recorded grep command.
  grep -iE 'agent model|ollama|unknown model|fail|error|ready|diagnostic|fallback|liveness|model_call|num_ctx|context' \
    "$LOG_DIR/openclaw_gateway_raw_logs_since_dashboard.txt" \
    > "$LOG_DIR/openclaw_gateway_filtered_logs_since_dashboard.txt" || true

  log "Asserting dashboard/OpenClaw GPU/context behavior"
  context_matches_expected "$EXPECTED_MODEL" "$EXPECTED_CONTEXT" "$EXPECTED_CONTEXT_MODE" "$LOG_DIR/ollama_ps_after_dashboard.txt" || die "$EXPECTED_MODEL did not show expected GPU/context policy after dashboard test."
  if grep -qiE 'unknown model|OLLAMA_API_KEY|All models failed|FailoverError' "$LOG_DIR/openclaw_gateway_raw_logs_since_dashboard.txt"; then
    die "Fresh OpenClaw gateway raw logs show model/provider failure after dashboard test."
  fi

  DASHBOARD_RESULT="passed"
fi

log "Writing report"
{
  echo "# OpenClaw/Ollama Verification Report"
  echo
  echo "Created: $(date -Iseconds)"
  echo "Host: $(hostname)"
  echo "User: $(whoami)"
  echo "Log directory: $LOG_DIR"
  echo
  echo "## Result"
  echo
  echo "- OpenClaw bounded provider surface: PASS"
  echo "- Direct Ollama ${EXPECTED_MODEL} GPU/context test: PASS"
  echo "- Dashboard/OpenClaw inference test: ${DASHBOARD_RESULT}"
  echo
  echo "## Expected stable baseline"
  echo
  echo "- OpenClaw default: $EXPECTED_OPENCLAW_MODEL"
  echo "- Context boundary: $EXPECTED_CONTEXT"
  echo "- GPU: 100% GPU in ollama ps"
  echo "- gateway.bind: loopback"
  echo "- OLLAMA_API_KEY: ollama-local in systemd user environment"
  echo
  echo "## Evidence files"
  echo
  echo "- $LOG_DIR/openclaw_models_ollama.txt"
  echo "- $LOG_DIR/openclaw_agents_defaults_model.json"
  echo "- $LOG_DIR/ollama_ps_after_direct.txt"
  echo "- $LOG_DIR/ollama_logs_since_direct.txt"
  if [[ "$SKIP_DASHBOARD" != "1" ]]; then
    echo "- $LOG_DIR/ollama_ps_after_dashboard.txt"
    echo "- $LOG_DIR/openclaw_gateway_raw_logs_since_dashboard.txt"
    echo "- $LOG_DIR/openclaw_gateway_filtered_logs_since_dashboard.txt"
  fi
} | tee "$REPORT_FILE"

log "Creating verification archive"
ARCHIVE="$HOME/openclaw_openclaw_ollama_4k_verification_${STAMP}.tar.gz"
tar -czf "$ARCHIVE" -C "$LOG_ROOT" "$STAMP"

EXPORT_DIR=""
for d in "/mnt/c/Users/${WINUSER:-}/Downloads" /mnt/c/Users/accou/Downloads /mnt/c/Users/*/Downloads; do
  [[ -d "$d" && -w "$d" ]] || continue
  case "$d" in
    *"Default User"*|*"All Users"*|*"Public"*) continue ;;
  esac
  EXPORT_DIR="$d"
  break
done

if [[ -n "$EXPORT_DIR" ]]; then
  cp "$ARCHIVE" "$EXPORT_DIR/" || true
  log "Verification archive copied to: $EXPORT_DIR/$(basename "$ARCHIVE")"
fi

log "Verification complete"
cat "$REPORT_FILE"

echo
echo "Archive:"
echo "  $ARCHIVE"
if [[ -n "$EXPORT_DIR" ]]; then
  echo "  $EXPORT_DIR/$(basename "$ARCHIVE")"
fi

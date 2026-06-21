#!/usr/bin/env bash
# verify_openclaw_optional_models.sh
#
# Verifies optional large local models if they were installed:
#   qwen3:30b-thinking-4k
#   qwen3-coder:30b-4k
#
# This script does not install models. It only tests installed aliases.

set -Eeuo pipefail

SCRIPT_NAME="$(basename "$0")"
STAMP="$(date +%Y%m%d_%H%M%S)"
LOG_ROOT="${HOME}/openclaw_optional_model_verification_logs"
LOG_DIR="${LOG_ROOT}/${STAMP}"
LOG_FILE="${LOG_DIR}/verify_optional_models.log"
mkdir -p "$LOG_DIR"
exec > >(tee -a "$LOG_FILE") 2>&1

MODELS=()
INCLUDE_REASONING=1
INCLUDE_CODER=1

log() { printf '\n[%s] %s\n' "$SCRIPT_NAME" "$*"; }
die() { printf '\n[%s] ERROR: %s\n' "$SCRIPT_NAME" "$*" >&2; exit 1; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --reasoning-only) INCLUDE_CODER=0; shift ;;
    --coder-only) INCLUDE_REASONING=0; shift ;;
    --help|-h)
      echo "Usage: bash $SCRIPT_NAME [--reasoning-only|--coder-only]"
      exit 0
      ;;
    *) die "Unknown option: $1" ;;
  esac
done

[[ "$INCLUDE_REASONING" == "1" ]] && MODELS+=(qwen3:30b-thinking-4k)
[[ "$INCLUDE_CODER" == "1" ]] && MODELS+=(qwen3-coder:30b-4k)

if [[ -x /usr/lib/wsl/lib/nvidia-smi ]]; then
  export PATH="/usr/lib/wsl/lib:$PATH"
fi

command -v ollama >/dev/null 2>&1 || die "ollama not found"
command -v nvidia-smi >/dev/null 2>&1 || die "nvidia-smi not visible"

log "GPU"
nvidia-smi -L || true

log "Ollama list"
ollama list

verify_model() {
  local model="$1"
  local safe="${model//[:\/]/_}"
  local out="$LOG_DIR/${safe}.out.txt"
  local psfile="$LOG_DIR/${safe}.ps.txt"

  if ! ollama list | awk 'NR>1 {print $1}' | grep -qx "$model"; then
    log "Skipping missing model: $model"
    return 0
  fi

  log "Testing $model"
  ollama stop "$model" >/dev/null 2>&1 || true
  sleep 3

  timeout 180s ollama run "$model" "Reply with OK only." > "$out" 2>&1 &
  local pid=$!
  sleep 20
  ollama ps | tee "$psfile" || true
  wait "$pid" || true

  if ! grep -q "$model" "$psfile"; then
    die "$model was not observed in ollama ps"
  fi
  if ! grep -q '100% GPU' "$psfile"; then
    die "$model did not show 100% GPU"
  fi
  if ! grep -q '4096' "$psfile"; then
    die "$model did not show CONTEXT 4096"
  fi

  ollama stop "$model" >/dev/null 2>&1 || true
  log "$model PASS: 100% GPU / 4096 context"
}

for m in "${MODELS[@]}"; do
  verify_model "$m"
done

log "Optional model verification complete"
echo "Log: $LOG_FILE"

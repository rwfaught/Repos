#!/usr/bin/env bash
# bootstrap_openclaw_wsl.sh
#
# REDO WSL OPENCLAW â€” v1.6 one-shot known-good bootstrap for fresh Ubuntu WSL.
#
# Intended first run:
#   bash bootstrap_openclaw_wsl.sh --yes
#
# Optional repo restore:
#   bash bootstrap_openclaw_wsl.sh --yes --archive /mnt/c/Users/accou/Downloads/projects.tar.gz
#
# Design:
#   - No reliance on old WSL state.
#   - System Node 24, not nvm, so OpenClaw's systemd gateway is stable.
#   - Handles WSL's NVIDIA shim path: /usr/lib/wsl/lib/nvidia-smi.
#   - Installs Ollama before OpenClaw.
#   - Pulls core local model pack before OpenClaw model config, with optional gated reasoning/coder models.
#   - Configures OpenClaw primary/fallback model schema correctly.
#   - Leaves a timestamped build log and evidence archive.

set -Eeuo pipefail

SCRIPT_NAME="$(basename "$0")"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STAMP="$(date +%Y%m%d_%H%M%S)"
LOG_ROOT="${HOME}/openclaw_bootstrap_logs"
LOG_DIR="${LOG_ROOT}/${STAMP}"
LOG_FILE="${LOG_DIR}/bootstrap.log"
SUMMARY_FILE="${LOG_DIR}/SUMMARY.md"
RED_DIR="${LOG_DIR}/redacted"

mkdir -p "$LOG_DIR" "$RED_DIR"
exec > >(tee -a "$LOG_FILE") 2>&1

YES=0
ARCHIVE_PATH=""
MODEL_PACK="core"
SKIP_MODELS=0
SKIP_OLLAMA=0
SKIP_OPENCLAW=0
VERIFY_MODELS=1
VERIFY_TIER="safe"
INCLUDE_HEAVY_MODELS=0
INCLUDE_REASONING_MODEL=0
INCLUDE_CODER_MODEL=0
PROMOTE_REASONING_MODEL=0
PROMOTE_CODER_MODEL=0
INCLUDE_RISKY_MODELS=0
CREATE_LOW_CTX_ALIASES=1
WITH_DISCORD=0
STRICT_SHELL_CUSTOMIZATION=0
MINIMAL_WIRE_MODEL=0
OLLAMA_MODEL_TIER="${OLLAMA_MODEL_TIER:-safe_full}"
DISCORD_OWNER_ID="${DISCORD_OWNER_ID:-}"
DISCORD_TOKEN_ENV="${DISCORD_TOKEN_ENV:-DISCORD_BOT_TOKEN}"
CODE_DIR="${HOME}/codex"
PROJECT_DIR="${CODE_DIR}/projects"
WIRE_MARKER_DIR="${WIRE_MARKER_DIR:-}"
OPENCLAW_NPM_PACKAGE_SPEC="${OPENCLAW_NPM_PACKAGE_SPEC:-openclaw@2026.6.6}"
OPENCLAW_EXPECTED_IDENTITY="${OPENCLAW_EXPECTED_IDENTITY-}"
OPENCLAW_EXPECTED_BUILD_ID="${OPENCLAW_EXPECTED_BUILD_ID-}"
OPENCLAW_EXPECTED_PACKAGE_VERSION="${OPENCLAW_EXPECTED_PACKAGE_VERSION-}"
OPENCLAW_IDENTITY_POLICY="${OPENCLAW_IDENTITY_POLICY-}"
if [[ -z "$OPENCLAW_IDENTITY_POLICY" ]]; then
  if [[ "$OPENCLAW_NPM_PACKAGE_SPEC" == "openclaw@2026.6.6" ]]; then
    OPENCLAW_EXPECTED_IDENTITY="OpenClaw 2026.6.6 (8c802aa)"
    OPENCLAW_EXPECTED_BUILD_ID="8c802aa"
    OPENCLAW_EXPECTED_PACKAGE_VERSION="2026.6.6"
    OPENCLAW_IDENTITY_POLICY="observed-build-string"
  elif [[ "$OPENCLAW_NPM_PACKAGE_SPEC" == "openclaw@latest" ]]; then
    OPENCLAW_IDENTITY_POLICY="version-command"
  else
    OPENCLAW_EXPECTED_PACKAGE_VERSION="${OPENCLAW_NPM_PACKAGE_SPEC#openclaw@}"
    OPENCLAW_IDENTITY_POLICY="package-version"
  fi
fi
OPENCLAW_NPM_INSTALL_TIMEOUT_SECONDS="${OPENCLAW_NPM_INSTALL_TIMEOUT_SECONDS:-600}"
OPENCLAW_NPM_INSTALL_MAX_ATTEMPTS="${OPENCLAW_NPM_INSTALL_MAX_ATTEMPTS:-2}"
OPENCLAW_NPM_INSTALL_RETRY_DELAY_SECONDS="${OPENCLAW_NPM_INSTALL_RETRY_DELAY_SECONDS:-15}"
OLLAMA_PULL_TIMEOUT_SECONDS="${OLLAMA_PULL_TIMEOUT_SECONDS:-600}"
OLLAMA_PULL_MAX_ATTEMPTS="${OLLAMA_PULL_MAX_ATTEMPTS:-3}"
OLLAMA_PULL_RETRY_DELAY_SECONDS="${OLLAMA_PULL_RETRY_DELAY_SECONDS:-15}"

SHELL_CUSTOMIZATION_ATTEMPTED="NO"
SHELL_CUSTOMIZATION_RESULT="NOT_RUN"
SHELL_CUSTOMIZATION_FAILURE_REASON="NONE"
OPENCLAW_NPM_INSTALL_ATTEMPTED="NO"
OPENCLAW_NPM_INSTALL_RESULT="UNKNOWN"
OPENCLAW_NPM_INSTALL_ATTEMPTS="0"
OPENCLAW_NPM_INSTALL_FAILURE_REASON="unknown"
OPENCLAW_NPM_INSTALL_DURATION_SECONDS="0"
OLLAMA_MODEL_PULL_ATTEMPTED="NO"
OLLAMA_MODEL_PULL_RESULT="UNKNOWN"
OLLAMA_MODEL_PULL_FAILURE_REASON="unknown"
OLLAMA_MODEL_PULL_ATTEMPTS="0"
OLLAMA_INSTALL_ATTEMPTED="NO"
OLLAMA_INSTALL_RESULT="UNKNOWN"
OLLAMA_INSTALL_METHOD="none"
OLLAMA_INSTALL_FAILURE_REASON="NONE"
PREFERRED_SAFE_MODEL_TIER_RESULT="UNKNOWN"
MINIMAL_WIRE_MODEL_RESULT="NOT_REQUESTED"

CURL_RETRY_OPTS=(
  --fail
  --silent
  --show-error
  --location
  --connect-timeout 15
  --max-time 120
  --retry 3
  --retry-delay 3
)

OLLAMA_INSTALL_CURL_RETRY_OPTS=(
  --fail
  --silent
  --show-error
  --location
  --connect-timeout 15
  --max-time 180
  --retry 3
  --retry-delay 5
)

OPENCLAW_PRIMARY="ollama/qwen3.5:9b-4k"
OPENCLAW_FALLBACKS='["ollama/qwen3.5:4b-4k","ollama/qwen3.5:2b-4k","ollama/qwen3:0.6b-4k"]'

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

install_and_validate_local_worker_routing_scaffold() {
  local target_dir="${HOME}/.config/openclaw/local_worker_routing"
  local item name expected_hash source_path target_path actual_hash
  local payload=(
    "local_worker_routing_v1.json:65dc436abeba0dea7fb3ea15366cb1ce52005133d9037fe50fff3770741bbc20"
    "Get-LocalWorkerRoutingConfig_v1.ps1:8326d71f3b48b29b605864292655231c5d1eb13d6c904b635e2e86f6c467cb71"
    "Invoke-LocalWorkerRouting_v1.ps1:b9a25c0d177471919319b2dd6e814770185b04292d02aa781c33f82c6d53628c"
    "Invoke-LocalWorkerRoutingRuntimeBridge_v1.ps1:af864a89fadaf250e5ab397f3ddaa772458ee891e850ebd0f79813b465e4f3f8"
  )

  install -d -m 0755 "$target_dir"
  for item in "${payload[@]}"; do
    name="${item%%:*}"
    expected_hash="${item#*:}"
    source_path="${SCRIPT_DIR}/${name}"
    target_path="${target_dir}/${name}"

    [[ -f "$source_path" ]] || die "Local worker routing scaffold source missing: ${name}"
    actual_hash="$(sha256sum "$source_path" | awk '{print $1}')"
    [[ "$actual_hash" == "$expected_hash" ]] || die "Local worker routing scaffold source hash mismatch: ${name}"

    install -m 0644 "$source_path" "$target_path"
    actual_hash="$(sha256sum "$target_path" | awk '{print $1}')"
    [[ "$actual_hash" == "$expected_hash" ]] || die "Local worker routing scaffold installed hash mismatch: ${name}"
  done

  python3 - "${target_dir}/local_worker_routing_v1.json" <<'PY'
import json
import sys

with open(sys.argv[1], "r", encoding="utf-8-sig") as handle:
    config = json.load(handle)

checks = {
    "runtimeIntegrationEnabled": config["localWorkerSurface"]["runtimeIntegrationEnabled"] is True,
    "runtimeConsumptionEnabled": config["futureIntegration"]["runtimeConsumptionEnabled"] is False,
    "routingScriptMutationAllowedHere": config["futureIntegration"]["routingScriptMutationAllowedHere"] is False,
}
failed = [name for name, passed in checks.items() if not passed]
if failed:
    raise SystemExit("routing scaffold policy validation failed: " + ",".join(failed))
PY

  write_wire_marker "localWorkerRoutingScaffoldInstallResult" "PASS"
  write_wire_marker "localWorkerRoutingScaffoldInstallPath" "$target_dir"
  write_wire_marker "localWorkerRoutingRuntimeIntegrationEnabled" "YES"
  write_wire_marker "localWorkerRoutingRuntimeConsumptionEnabled" "NO"
  write_wire_marker "localWorkerRoutingScriptMutationAllowed" "NO"
  log "Local worker routing scaffold installed and validated as inert scaffold: $target_dir"
}

usage() {
  cat <<'EOF'
Usage:
  bash bootstrap_openclaw_wsl.sh [options]

Options:
  --yes                         Assume yes for non-secret prompts and model pulls.
  --archive PATH                Restore OpenClaw repo from a tar.gz archive.
  --model-pack core|minimal     Default: core.
  --skip-models                 Do not pull Ollama models.
  --skip-ollama                 Do not install/configure Ollama.
  --skip-openclaw               Do not install/configure OpenClaw.
  --no-verify-models            Skip per-model Ollama GPU verification.
  --verify-tier safe|medium|all Model verification tier. Default: medium.
  --include-reasoning-model    Pull/test qwen3:30b-thinking and create qwen3:30b-thinking-4k. Off by default.
  --include-coder-model        Pull/test qwen3-coder:30b and create qwen3-coder:30b-4k. Off by default.
  --promote-reasoning-model    Make ollama/qwen3:30b-thinking-4k the OpenClaw primary after gated install.
  --promote-coder-model        Make ollama/qwen3-coder:30b-4k the OpenClaw primary after gated install.
  --include-heavy-models       Backward-compatible alias for --include-reasoning-model.
  --include-risky-models       Pull/test known-risky large models. Off by default and not recommended.
  --no-low-ctx-aliases          Do not create 4K-context aliases for large models.
  --with-discord                Configure Discord token env-ref and optional owner.
  --minimal-wire-model          Use minimal wire tier (qwen3:0.6b only).
  --strict-shell-customization  Make optional shell customization failures fatal.
  --discord-owner-id ID         Set commands.ownerAllowFrom to ["discord:ID"].
  --discord-token-env NAME      Env var name for Discord token. Default: DISCORD_BOT_TOKEN.
  --primary MODEL               OpenClaw primary model. Default: ollama/qwen3.5:9b-4k.
  --help                        Show this help.
EOF
}

ask_yes_no() {
  local prompt="$1"
  local default="${2:-n}"
  if [[ "$YES" == "1" ]]; then
    return 0
  fi
  local suffix="[y/N]"
  [[ "$default" == "y" ]] && suffix="[Y/n]"
  read -r -p "$prompt $suffix " ans || true
  ans="${ans:-$default}"
  [[ "$ans" =~ ^[Yy]$ ]]
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --yes) YES=1; shift ;;
    --archive) ARCHIVE_PATH="${2:-}"; [[ -n "$ARCHIVE_PATH" ]] || die "--archive requires path"; shift 2 ;;
    --model-pack) MODEL_PACK="${2:-}"; [[ "$MODEL_PACK" == "core" || "$MODEL_PACK" == "minimal" ]] || die "--model-pack must be core or minimal"; shift 2 ;;
    --skip-models) SKIP_MODELS=1; shift ;;
    --skip-ollama) SKIP_OLLAMA=1; shift ;;
    --skip-openclaw) SKIP_OPENCLAW=1; shift ;;
    --no-verify-models) VERIFY_MODELS=0; shift ;;
    --verify-tier) VERIFY_TIER="${2:-}"; [[ "$VERIFY_TIER" == "safe" || "$VERIFY_TIER" == "medium" || "$VERIFY_TIER" == "all" ]] || die "--verify-tier must be safe, medium, or all"; shift 2 ;;
    --include-reasoning-model) INCLUDE_REASONING_MODEL=1; INCLUDE_HEAVY_MODELS=1; shift ;;
    --include-coder-model) INCLUDE_CODER_MODEL=1; shift ;;
    --promote-reasoning-model) INCLUDE_REASONING_MODEL=1; INCLUDE_HEAVY_MODELS=1; PROMOTE_REASONING_MODEL=1; OPENCLAW_PRIMARY="ollama/qwen3:30b-thinking-4k"; OPENCLAW_FALLBACKS='["ollama/qwen3.5:9b-4k","ollama/qwen3.5:4b-4k","ollama/qwen3.5:2b-4k","ollama/qwen3:0.6b-4k"]'; shift ;;
    --promote-coder-model) INCLUDE_CODER_MODEL=1; PROMOTE_CODER_MODEL=1; OPENCLAW_PRIMARY="ollama/qwen3-coder:30b-4k"; OPENCLAW_FALLBACKS='["ollama/qwen3.5:9b-4k","ollama/qwen3.5:4b-4k","ollama/qwen3.5:2b-4k","ollama/qwen3:0.6b-4k"]'; shift ;;
    --include-heavy-models) INCLUDE_HEAVY_MODELS=1; INCLUDE_REASONING_MODEL=1; shift ;;
    --include-risky-models) INCLUDE_RISKY_MODELS=1; shift ;;
    --no-low-ctx-aliases) CREATE_LOW_CTX_ALIASES=0; shift ;;
    --with-discord) WITH_DISCORD=1; shift ;;
    --minimal-wire-model) MINIMAL_WIRE_MODEL=1; OLLAMA_MODEL_TIER="minimal_wire"; shift ;;
    --strict-shell-customization) STRICT_SHELL_CUSTOMIZATION=1; shift ;;
    --discord-owner-id) DISCORD_OWNER_ID="${2:-}"; [[ -n "$DISCORD_OWNER_ID" ]] || die "--discord-owner-id requires value"; shift 2 ;;
    --discord-token-env) DISCORD_TOKEN_ENV="${2:-}"; [[ -n "$DISCORD_TOKEN_ENV" ]] || die "--discord-token-env requires value"; shift 2 ;;
    --primary) OPENCLAW_PRIMARY="${2:-}"; [[ -n "$OPENCLAW_PRIMARY" ]] || die "--primary requires model"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) die "Unknown option: $1" ;;
  esac
done

if [[ "$MINIMAL_WIRE_MODEL" == "1" ]]; then
  OLLAMA_MODEL_TIER="minimal_wire"
fi
if [[ "$OLLAMA_MODEL_TIER" != "safe_full" && "$OLLAMA_MODEL_TIER" != "minimal_wire" ]]; then
  die "OLLAMA_MODEL_TIER must be safe_full or minimal_wire"
fi
if [[ "$OLLAMA_MODEL_TIER" == "minimal_wire" ]]; then
  MINIMAL_WIRE_MODEL=1
fi

write_shell_customization_markers() {
  [[ -n "$WIRE_MARKER_DIR" && -d "$WIRE_MARKER_DIR" ]] || return 0
  local ts
  ts="$(date -Iseconds)"
  cat > "${WIRE_MARKER_DIR}/shellCustomizationAttempted.marker" <<EOF
key=shellCustomizationAttempted
value=${SHELL_CUSTOMIZATION_ATTEMPTED}
timestamp=${ts}
EOF
  cat > "${WIRE_MARKER_DIR}/shellCustomizationResult.marker" <<EOF
key=shellCustomizationResult
value=${SHELL_CUSTOMIZATION_RESULT}
timestamp=${ts}
EOF
  cat > "${WIRE_MARKER_DIR}/shellCustomizationFailureReason.marker" <<EOF
key=shellCustomizationFailureReason
value=${SHELL_CUSTOMIZATION_FAILURE_REASON}
timestamp=${ts}
EOF
}

write_wire_marker() {
  local key="$1" value="$2"
  [[ -n "$WIRE_MARKER_DIR" && -d "$WIRE_MARKER_DIR" ]] || return 0
  cat > "${WIRE_MARKER_DIR}/${key}.marker" <<EOF
key=${key}
value=${value}
timestamp=$(date -Iseconds)
EOF
}

resolve_cmd_path() {
  command -v "$1" 2>/dev/null || echo "MISSING"
}

path_has_windows_segments() {
  local entry
  IFS=':' read -r -a __path_entries <<< "${PATH:-}"
  for entry in "${__path_entries[@]}"; do
    [[ "$entry" == /mnt/c/* ]] && return 0
  done
  return 1
}

apply_linux_path_hardening() {
  local hardened_entries=()
  [[ -d /usr/lib/wsl/lib ]] && hardened_entries+=("/usr/lib/wsl/lib")
  hardened_entries+=("/usr/local/sbin" "/usr/local/bin" "/usr/sbin" "/usr/bin" "/sbin" "/bin")
  [[ -d "${HOME}/bin" ]] && hardened_entries+=("${HOME}/bin")
  [[ -d "${HOME}/.local/bin" ]] && hardened_entries+=("${HOME}/.local/bin")
  PATH="$(IFS=:; printf '%s' "${hardened_entries[*]}")"
  export PATH
}

detect_append_windows_path_policy() {
  if [[ -f /etc/wsl.conf ]] && grep -Eiq '^[[:space:]]*appendWindowsPath[[:space:]]*=[[:space:]]*false([[:space:]]*)$' /etc/wsl.conf; then
    echo "appendWindowsPath=false"
  elif [[ -f /etc/wsl.conf ]] && grep -Eq '^\[interop\]' /etc/wsl.conf; then
    echo "interop-present-without-appendWindowsPath=false"
  else
    echo "interop-policy-not-declared"
  fi
}

record_linux_path_state() {
  local phase="$1"
  local windows_segments="NO"
  local append_policy
  append_policy="$(detect_append_windows_path_policy)"
  if path_has_windows_segments; then
    windows_segments="YES"
  fi
  write_wire_marker "linuxPathHardeningResult" "$([[ "$windows_segments" == "NO" ]] && echo PASS || echo FAIL)"
  write_wire_marker "linuxPathWindowsSegmentsPresent" "$windows_segments"
  write_wire_marker "appendWindowsPathPolicy" "$append_policy"
  write_wire_marker "linuxPathHardeningPhase" "$phase"
  write_wire_marker "linuxNodeResolution${phase}" "$(resolve_cmd_path node)"
  write_wire_marker "linuxNpmResolution${phase}" "$(resolve_cmd_path npm)"
  write_wire_marker "openclawResolution${phase}" "$(resolve_cmd_path openclaw)"
}

assert_not_windows_resolution() {
  local cmd="$1" marker_key="$2" failure_reason="$3"
  local resolved
  resolved="$(resolve_cmd_path "$cmd")"
  write_wire_marker "$marker_key" "$resolved"
  if [[ "$resolved" == /mnt/c/* ]]; then
    write_wire_marker "linuxNodeNpmGateResult" "FAIL"
    write_wire_marker "openclawCommandResolutionGuardResult" "FAIL"
    die "${failure_reason}: ${cmd} resolves to Windows shim ${resolved}"
  fi
}

write_openclaw_npm_markers() {
  [[ -n "$WIRE_MARKER_DIR" && -d "$WIRE_MARKER_DIR" ]] || return 0
  local ts
  ts="$(date -Iseconds)"
  cat > "${WIRE_MARKER_DIR}/openclawNpmInstallAttempted.marker" <<EOF
key=openclawNpmInstallAttempted
value=${OPENCLAW_NPM_INSTALL_ATTEMPTED}
timestamp=${ts}
EOF
  cat > "${WIRE_MARKER_DIR}/openclawNpmInstallResult.marker" <<EOF
key=openclawNpmInstallResult
value=${OPENCLAW_NPM_INSTALL_RESULT}
timestamp=${ts}
EOF
  cat > "${WIRE_MARKER_DIR}/openclawNpmInstallAttempts.marker" <<EOF
key=openclawNpmInstallAttempts
value=${OPENCLAW_NPM_INSTALL_ATTEMPTS}
timestamp=${ts}
EOF
  cat > "${WIRE_MARKER_DIR}/openclawNpmInstallFailureReason.marker" <<EOF
key=openclawNpmInstallFailureReason
value=${OPENCLAW_NPM_INSTALL_FAILURE_REASON}
timestamp=${ts}
EOF
  cat > "${WIRE_MARKER_DIR}/openclawNpmInstallDurationSeconds.marker" <<EOF
key=openclawNpmInstallDurationSeconds
value=${OPENCLAW_NPM_INSTALL_DURATION_SECONDS}
timestamp=${ts}
EOF
}

write_ollama_model_markers() {
  [[ -n "$WIRE_MARKER_DIR" && -d "$WIRE_MARKER_DIR" ]] || return 0
  local ts
  ts="$(date -Iseconds)"
  cat > "${WIRE_MARKER_DIR}/ollamaModelTier.marker" <<EOF
key=ollamaModelTier
value=${OLLAMA_MODEL_TIER}
timestamp=${ts}
EOF
  cat > "${WIRE_MARKER_DIR}/ollamaModelPullAttempted.marker" <<EOF
key=ollamaModelPullAttempted
value=${OLLAMA_MODEL_PULL_ATTEMPTED}
timestamp=${ts}
EOF
  cat > "${WIRE_MARKER_DIR}/ollamaModelPullResult.marker" <<EOF
key=ollamaModelPullResult
value=${OLLAMA_MODEL_PULL_RESULT}
timestamp=${ts}
EOF
  cat > "${WIRE_MARKER_DIR}/ollamaModelPullFailureReason.marker" <<EOF
key=ollamaModelPullFailureReason
value=${OLLAMA_MODEL_PULL_FAILURE_REASON}
timestamp=${ts}
EOF
  cat > "${WIRE_MARKER_DIR}/ollamaModelPullAttempts.marker" <<EOF
key=ollamaModelPullAttempts
value=${OLLAMA_MODEL_PULL_ATTEMPTS}
timestamp=${ts}
EOF
  cat > "${WIRE_MARKER_DIR}/preferredSafeModelTierResult.marker" <<EOF
key=preferredSafeModelTierResult
value=${PREFERRED_SAFE_MODEL_TIER_RESULT}
timestamp=${ts}
EOF
  cat > "${WIRE_MARKER_DIR}/minimalWireModelResult.marker" <<EOF
key=minimalWireModelResult
value=${MINIMAL_WIRE_MODEL_RESULT}
timestamp=${ts}
EOF
}

write_ollama_install_markers() {
  [[ -n "$WIRE_MARKER_DIR" && -d "$WIRE_MARKER_DIR" ]] || return 0
  local ts
  ts="$(date -Iseconds)"
  cat > "${WIRE_MARKER_DIR}/ollamaInstallAttempted.marker" <<EOF
key=ollamaInstallAttempted
value=${OLLAMA_INSTALL_ATTEMPTED}
timestamp=${ts}
EOF
  cat > "${WIRE_MARKER_DIR}/ollamaInstallResult.marker" <<EOF
key=ollamaInstallResult
value=${OLLAMA_INSTALL_RESULT}
timestamp=${ts}
EOF
  cat > "${WIRE_MARKER_DIR}/ollamaInstallMethod.marker" <<EOF
key=ollamaInstallMethod
value=${OLLAMA_INSTALL_METHOD}
timestamp=${ts}
EOF
  cat > "${WIRE_MARKER_DIR}/ollamaInstallFailureReason.marker" <<EOF
key=ollamaInstallFailureReason
value=${OLLAMA_INSTALL_FAILURE_REASON}
timestamp=${ts}
EOF
}

compatibility_marker_val() {
  local key="$1"
  local file="${WIRE_MARKER_DIR}/${key}.marker"
  [[ -f "$file" ]] && sed -n 's/^value=//p' "$file" | head -n1 || echo ""
}

fail_ollama_install() {
  local reason="$1"
  OLLAMA_INSTALL_RESULT="FAIL"
  OLLAMA_INSTALL_FAILURE_REASON="$reason"
  write_ollama_install_markers
  die "Failed to install Ollama (${reason})"
}

record_shell_customization_failure() {
  local reason="$1"
  SHELL_CUSTOMIZATION_RESULT="FAILED_NONCRITICAL"
  SHELL_CUSTOMIZATION_FAILURE_REASON="$reason"
  log "WARNING: shell customization issue: $reason"
}

on_error() {
  local rc=$?
  log "FAILED with exit code $rc"
  log "Log preserved at: $LOG_FILE"
  exit "$rc"
}
trap on_error ERR

log "Starting v1 one-shot bootstrap"
log "Log file: $LOG_FILE"

log "Checking sudo mode near the start"
cat <<'EOF'
The script will first try passwordless sudo. If that is unavailable,
it will ask for your Linux password once and keep sudo alive during the run.
EOF

SUDO_KEEPALIVE_PID=""
if sudo -n true 2>/dev/null; then
  log "Passwordless sudo is active for this user."
else
  log "Passwordless sudo is not active; prompting once for sudo credentials."
  sudo -v
  # Keep sudo alive while this script runs. This avoids timeout during multi-hour model pulls.
  ( while true; do sudo -n true 2>/dev/null || exit; sleep 60; done ) &
  SUDO_KEEPALIVE_PID=$!
fi

trap 'if [[ -n "${SUDO_KEEPALIVE_PID:-}" ]]; then kill "$SUDO_KEEPALIVE_PID" 2>/dev/null || true; fi' EXIT

# WSL GPU utilities live here, but keep PATH Linux-only and explicit.
apply_linux_path_hardening
record_linux_path_state "Initial"

if [[ "$(id -u)" == "0" ]]; then
  die "Run as normal Linux user, not root."
fi

if ! grep -qi microsoft /proc/version 2>/dev/null; then
  log "This does not look like WSL. Continuing anyway."
fi

log "Checking systemd"
PID1_COMM="$(ps -p 1 -o comm= 2>/dev/null || true)"
if [[ "$PID1_COMM" == "systemd" ]] && [[ -d /run/systemd/system ]] && command -v systemctl >/dev/null 2>&1; then
  SYSTEMD_STATE="$(systemctl is-system-running 2>/dev/null || true)"
  log "systemd is active enough for bootstrap. state=${SYSTEMD_STATE:-unknown}"
else
  log "systemd is not active as PID 1. Enabling it in /etc/wsl.conf."
  sudo tee /etc/wsl.conf >/dev/null <<'EOF'
[boot]
systemd=true

[user]
default=roger
EOF
  cat <<EOF

systemd was enabled for future WSL launches.

From POWERSHELL, not inside WSL, run:
  wsl --shutdown

Then rerun the package runner from inside the distro:
  cd ${HOME}/openclaw_install/package
  bash ./run_openclaw_install_from_config.sh --config ${HOME}/openclaw_install/config/install_config.json

EOF
  exit 20
fi

log "Installing base Ubuntu packages"
sudo apt-get -o Acquire::Retries=5 update
sudo DEBIAN_FRONTEND=noninteractive apt-get -o Acquire::Retries=5 install -y \
  ca-certificates curl wget git git-lfs gnupg software-properties-common \
  build-essential make cmake ninja-build pkg-config \
  python3 python3-dev python3-venv python3-pip pipx \
  jq ripgrep fd-find bat tree htop btop unzip zip tar xz-utils zstd rsync \
  nano vim tmux zsh fonts-font-awesome pciutils openssl lsb-release

log "Installing inert local worker routing scaffold"
install_and_validate_local_worker_routing_scaffold

log "Persisting WSL GPU shim path for future shells"
if ! grep -q 'REDO_WSL_OPENCLAW_WSL_GPU_PATH' "$HOME/.profile" 2>/dev/null; then
  cat >> "$HOME/.profile" <<'EOF'

# REDO_WSL_OPENCLAW_WSL_GPU_PATH
# REDO_WSL_OPENCLAW_STRICT_LINUX_PATH
PATH_ENTRIES=""
if [ -d /usr/lib/wsl/lib ]; then
  PATH_ENTRIES="/usr/lib/wsl/lib"
fi
for _entry in /usr/local/sbin /usr/local/bin /usr/sbin /usr/bin /sbin /bin "$HOME/bin" "$HOME/.local/bin"; do
  [ -d "$_entry" ] || continue
  if [ -n "$PATH_ENTRIES" ]; then
    PATH_ENTRIES="${PATH_ENTRIES}:$_entry"
  else
    PATH_ENTRIES="$_entry"
  fi
done
export PATH="$PATH_ENTRIES"
EOF
fi

log "Installing zsh, Oh My Zsh, Powerlevel10k, and plugins"
SHELL_CUSTOMIZATION_ATTEMPTED="YES"
SHELL_CUSTOMIZATION_RESULT="PASS"
SHELL_CUSTOMIZATION_FAILURE_REASON="NONE"

if [[ ! -d "$HOME/.oh-my-zsh" ]]; then
  OMZ_INSTALLER_URL="https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh"
  tmp_omz="$(mktemp)"
  if curl "${CURL_RETRY_OPTS[@]}" "$OMZ_INSTALLER_URL" -o "$tmp_omz"; then
    if [[ -s "$tmp_omz" ]]; then
      if ! RUNZSH=no CHSH=no KEEP_ZSHRC=yes sh "$tmp_omz"; then
        record_shell_customization_failure "oh-my-zsh-installer-exit-nonzero"
      fi
    else
      record_shell_customization_failure "oh-my-zsh-installer-empty"
    fi
  else
    record_shell_customization_failure "oh-my-zsh-download-failed"
  fi
  rm -f "$tmp_omz"
fi

ZSH_CUSTOM="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}"
if ! mkdir -p "$ZSH_CUSTOM/themes" "$ZSH_CUSTOM/plugins"; then
  record_shell_customization_failure "zsh-custom-dir-create-failed"
else
  [[ -d "$ZSH_CUSTOM/themes/powerlevel10k" ]] || git clone --depth=1 https://github.com/romkatv/powerlevel10k.git "$ZSH_CUSTOM/themes/powerlevel10k" || record_shell_customization_failure "powerlevel10k-clone-failed"
  [[ -d "$ZSH_CUSTOM/plugins/zsh-autosuggestions" ]] || git clone --depth=1 https://github.com/zsh-users/zsh-autosuggestions "$ZSH_CUSTOM/plugins/zsh-autosuggestions" || record_shell_customization_failure "zsh-autosuggestions-clone-failed"
  [[ -d "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting" ]] || git clone --depth=1 https://github.com/zsh-users/zsh-syntax-highlighting "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting" || record_shell_customization_failure "zsh-syntax-highlighting-clone-failed"
fi

if ! touch "$HOME/.zshrc"; then
  record_shell_customization_failure "zshrc-touch-failed"
else
  if grep -q '^ZSH_THEME=' "$HOME/.zshrc"; then
    sed -i 's|^ZSH_THEME=.*|ZSH_THEME="powerlevel10k/powerlevel10k"|' "$HOME/.zshrc" || record_shell_customization_failure "zsh-theme-update-failed"
  else
    echo 'ZSH_THEME="powerlevel10k/powerlevel10k"' >> "$HOME/.zshrc" || record_shell_customization_failure "zsh-theme-append-failed"
  fi

  if grep -q '^plugins=' "$HOME/.zshrc"; then
    sed -i 's|^plugins=.*|plugins=(git zsh-autosuggestions zsh-syntax-highlighting)|' "$HOME/.zshrc" || record_shell_customization_failure "zsh-plugins-update-failed"
  else
    echo 'plugins=(git zsh-autosuggestions zsh-syntax-highlighting)' >> "$HOME/.zshrc" || record_shell_customization_failure "zsh-plugins-append-failed"
  fi

  if ! grep -q 'REDO_WSL_OPENCLAW_PATH_GUARD' "$HOME/.zshrc"; then
    cat >> "$HOME/.zshrc" <<'EOF'

# REDO_WSL_OPENCLAW_PATH_GUARD
PATH_ENTRIES=""
if [ -d /usr/lib/wsl/lib ]; then
  PATH_ENTRIES="/usr/lib/wsl/lib"
fi
for _entry in /usr/local/sbin /usr/local/bin /usr/sbin /usr/bin /sbin /bin "$HOME/bin" "$HOME/.local/bin"; do
  [ -d "$_entry" ] || continue
  if [ -n "$PATH_ENTRIES" ]; then
    PATH_ENTRIES="${PATH_ENTRIES}:$_entry"
  else
    PATH_ENTRIES="$_entry"
  fi
done
export PATH="$PATH_ENTRIES"
EOF
  fi
fi

ZSH_BIN="$(command -v zsh)"
if [[ "$SHELL" != "$ZSH_BIN" ]]; then
  log "Setting zsh as default shell for $USER"
  sudo chsh -s "$ZSH_BIN" "$USER" || record_shell_customization_failure "zsh-chsh-failed"
fi
write_shell_customization_markers
if [[ "$SHELL_CUSTOMIZATION_RESULT" != "PASS" ]]; then
  if [[ "$STRICT_SHELL_CUSTOMIZATION" == "1" ]]; then
    die "Strict shell customization enabled and optional customization failed: $SHELL_CUSTOMIZATION_FAILURE_REASON"
  fi
  log "Continuing bootstrap; shell customization is optional by default."
fi

record_linux_path_state "BeforeNodeInstall"
assert_not_windows_resolution "node" "linuxNodeResolutionBeforeNodeInstallGate" "LINUX_NODE_WINDOWS_SHIM_DETECTED_BEFORE_INSTALL"
assert_not_windows_resolution "npm" "linuxNpmResolutionBeforeNodeInstallGate" "LINUX_NPM_WINDOWS_SHIM_DETECTED_BEFORE_INSTALL"
assert_not_windows_resolution "openclaw" "openclawResolutionBeforeInstallGate" "OPENCLAW_WINDOWS_SHIM_DETECTED_BEFORE_INSTALL"

log "Installing system Node.js 24"
if ! command -v node >/dev/null 2>&1 || ! node --version | grep -q '^v24\.'; then
  curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash -
  sudo DEBIAN_FRONTEND=noninteractive apt-get -o Acquire::Retries=5 install -y nodejs
fi
hash -r
apply_linux_path_hardening
record_linux_path_state "AfterNodeInstall"
assert_not_windows_resolution "node" "linuxNodeResolutionAfterNodeInstallGate" "LINUX_NODE_WINDOWS_SHIM_DETECTED_AFTER_INSTALL"
assert_not_windows_resolution "npm" "linuxNpmResolutionAfterNodeInstallGate" "LINUX_NPM_WINDOWS_SHIM_DETECTED_AFTER_INSTALL"
if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
  write_wire_marker "linuxNodeNpmGateResult" "FAIL"
  die "LINUX_NODE_NPM_GATE_FAILED: node and npm must resolve to Linux commands after installation."
fi
write_wire_marker "linuxNodeNpmGateResult" "PASS"
node --version
npm --version
which -a node npm || true

pull_ollama_model_with_retry() {
  local model="$1"
  local attempt rc
  local model_log="$LOG_DIR/ollama_pull_${model//[:\/]/_}.log"
  : > "$model_log"
  for ((attempt=1; attempt<=OLLAMA_PULL_MAX_ATTEMPTS; attempt++)); do
    OLLAMA_MODEL_PULL_ATTEMPTS="$((OLLAMA_MODEL_PULL_ATTEMPTS + 1))"
    log "Pulling Ollama model: $model (attempt ${attempt}/${OLLAMA_PULL_MAX_ATTEMPTS})"
    {
      echo "model=$model"
      echo "attempt=$attempt"
      echo "started_at=$(date -Iseconds)"
    } >> "$model_log"
    set +e
    timeout "${OLLAMA_PULL_TIMEOUT_SECONDS}s" ollama pull "$model" >> "$model_log" 2>&1
    rc=$?
    set -e
    echo "exit_code=$rc" >> "$model_log"
    if [[ "$rc" == "0" ]]; then
      OLLAMA_MODEL_PULL_RESULT="PASS"
      OLLAMA_MODEL_PULL_FAILURE_REASON="none"
      return 0
    fi
    if grep -qiE 'TLS handshake timeout|handshake timeout|i/o timeout' "$model_log"; then
      OLLAMA_MODEL_PULL_RESULT="TIMEOUT"
      OLLAMA_MODEL_PULL_FAILURE_REASON="ollama-pull-tls-handshake-timeout"
    elif [[ "$rc" == "124" ]]; then
      OLLAMA_MODEL_PULL_RESULT="TIMEOUT"
      OLLAMA_MODEL_PULL_FAILURE_REASON="ollama-pull-timeout"
    else
      OLLAMA_MODEL_PULL_RESULT="FAIL"
      OLLAMA_MODEL_PULL_FAILURE_REASON="ollama-pull-exit-nonzero"
    fi
    if (( attempt < OLLAMA_PULL_MAX_ATTEMPTS )); then
      sleep "$OLLAMA_PULL_RETRY_DELAY_SECONDS"
    fi
  done
  return 1
}

if [[ "$SKIP_OLLAMA" != "1" ]]; then
  log "Checking NVIDIA GPU visibility inside WSL"
  if ! command -v nvidia-smi >/dev/null 2>&1; then
    if [[ -x /usr/lib/wsl/lib/nvidia-smi ]]; then
      export PATH="/usr/lib/wsl/lib:$PATH"
    fi
  fi

  if ! command -v nvidia-smi >/dev/null 2>&1; then
    cat <<'EOF'

nvidia-smi is not visible inside WSL.

From POWERSHELL, not inside WSL, check:
  nvidia-smi
  wsl --status
  wsl --update
  wsl --shutdown

Then reopen Ubuntu and rerun this script.

Inside WSL, the expected NVIDIA shim is:
  /usr/lib/wsl/lib/nvidia-smi

Do not install a normal Linux NVIDIA display driver inside WSL.
EOF
    die "nvidia-smi not found inside WSL."
  fi

  nvidia-smi
  GPU_ID="$(nvidia-smi -L | sed -n 's/.*UUID: \(GPU-[^)]*\)).*/\1/p' | head -1 || true)"
  [[ -n "$GPU_ID" ]] || GPU_ID="0"
  log "Selected CUDA_VISIBLE_DEVICES for Ollama: $GPU_ID"

  log "Installing Ollama"
  if ! command -v ollama >/dev/null 2>&1; then
    OLLAMA_INSTALL_ATTEMPTED="YES"
    OLLAMA_INSTALL_RESULT="IN_PROGRESS"
    OLLAMA_INSTALL_METHOD="install.sh"
    OLLAMA_INSTALL_FAILURE_REASON="NONE"
    write_ollama_install_markers

    ollama_install_log="$LOG_DIR/ollama_install.log"
    : > "$ollama_install_log"
    tmp_install_sh="$(mktemp)"
    if ! curl "${OLLAMA_INSTALL_CURL_RETRY_OPTS[@]}" "https://ollama.com/install.sh" -o "$tmp_install_sh"; then
      rm -f "$tmp_install_sh"
      fail_ollama_install "ollama-install-script-download-failed"
    fi
    if [[ ! -s "$tmp_install_sh" ]]; then
      rm -f "$tmp_install_sh"
      fail_ollama_install "ollama-install-script-empty"
    fi

    set +e
    sh "$tmp_install_sh" >"$ollama_install_log" 2>&1
    install_script_rc=$?
    set -e
    rm -f "$tmp_install_sh"

    fallback_required=0
    if [[ "$install_script_rc" -ne 0 ]]; then
      OLLAMA_INSTALL_FAILURE_REASON="ollama-install-script-exit-nonzero"
      if grep -Eiq 'ollama-linux-amd64\.tgz|404|500|requested url returned error: (404|500)|curl: \(22\)|gzip: stdin: unexpected end of file|tar: Child returned status|tar: Error is not recoverable' "$ollama_install_log"; then
        OLLAMA_INSTALL_FAILURE_REASON="ollama-install-archive-download-or-extract-failed"
        fallback_required=1
      else
        fail_ollama_install "ollama-install-script-exit-nonzero"
      fi
    fi

    if [[ "$fallback_required" != "1" ]] && ! command -v ollama >/dev/null 2>&1; then
      if grep -Eiq 'ollama-linux-amd64\.tgz|404|500|requested url returned error: (404|500)|curl: \(22\)|gzip: stdin: unexpected end of file|tar: Child returned status|tar: Error is not recoverable' "$ollama_install_log"; then
        OLLAMA_INSTALL_FAILURE_REASON="ollama-install-command-missing-after-archive-download-or-extract-failed"
        fallback_required=1
      fi
    fi

    if [[ "$fallback_required" == "1" ]]; then
      log "Ollama install.sh failed or left no ollama command; using manual .tar.zst fallback"
      OLLAMA_INSTALL_METHOD="manual-tar-zst-fallback"
      write_ollama_install_markers

      if ! command -v zstd >/dev/null 2>&1; then
        sudo DEBIAN_FRONTEND=noninteractive apt-get -o Acquire::Retries=5 install -y zstd
      fi

      tmp_ollama_archive="$(mktemp --suffix=.tar.zst)"
      if ! curl "${OLLAMA_INSTALL_CURL_RETRY_OPTS[@]}" "https://ollama.com/download/ollama-linux-amd64.tar.zst" -o "$tmp_ollama_archive"; then
        rm -f "$tmp_ollama_archive"
        fail_ollama_install "ollama-install-archive-download-failed"
      fi
      if [[ ! -s "$tmp_ollama_archive" ]]; then
        rm -f "$tmp_ollama_archive"
        fail_ollama_install "ollama-install-archive-empty"
      fi
      if ! sudo tar --zstd -x -f "$tmp_ollama_archive" -C /usr >>"$ollama_install_log" 2>&1; then
        rm -f "$tmp_ollama_archive"
        fail_ollama_install "ollama-install-archive-extract-failed"
      fi
      rm -f "$tmp_ollama_archive"

      if ! getent group ollama >/dev/null 2>&1; then
        sudo groupadd --system ollama
      fi
      if ! id -u ollama >/dev/null 2>&1; then
        sudo useradd --system --gid ollama --home-dir /usr/share/ollama --create-home --shell /usr/sbin/nologin ollama
      fi
      if [[ ! -f /etc/systemd/system/ollama.service && ! -f /usr/lib/systemd/system/ollama.service && ! -f /lib/systemd/system/ollama.service ]]; then
        sudo tee /etc/systemd/system/ollama.service >/dev/null <<'EOF'
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
ExecStart=/usr/bin/ollama serve
User=ollama
Group=ollama
Restart=always
RestartSec=3
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

[Install]
WantedBy=default.target
EOF
      fi
    fi

    if ! command -v ollama >/dev/null 2>&1; then
      fail_ollama_install "ollama-command-missing-after-install"
    fi
    OLLAMA_INSTALL_RESULT="PASS"
    OLLAMA_INSTALL_FAILURE_REASON="NONE"
    write_ollama_install_markers
  else
    OLLAMA_INSTALL_ATTEMPTED="NO"
    OLLAMA_INSTALL_RESULT="ALREADY_PRESENT"
    OLLAMA_INSTALL_METHOD="preinstalled"
    OLLAMA_INSTALL_FAILURE_REASON="NONE"
    write_ollama_install_markers
    log "Ollama already installed: $(ollama --version || true)"
  fi

  log "Configuring Ollama systemd service for NVIDIA/WSL"
  sudo mkdir -p /etc/systemd/system/ollama.service.d
  sudo tee /etc/systemd/system/ollama.service.d/override.conf >/dev/null <<EOF
[Service]
Environment="PATH=/usr/lib/wsl/lib:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="CUDA_VISIBLE_DEVICES=${GPU_ID}"
Environment="OLLAMA_HOST=127.0.0.1:11434"
Environment="OLLAMA_KEEP_ALIVE=30m"
Environment="OLLAMA_NUM_PARALLEL=1"
Environment="OLLAMA_MAX_LOADED_MODELS=1"
EOF

  sudo systemctl daemon-reload
  sudo systemctl enable ollama
  sudo systemctl restart ollama

  log "Waiting for Ollama API"
  for _ in {1..90}; do
    if curl -fsS http://127.0.0.1:11434/api/version >/dev/null 2>&1; then
      break
    fi
    sleep 1
  done
  curl -fsS http://127.0.0.1:11434/api/version || die "Ollama API did not become ready"
  ollama --version

  if [[ "$OLLAMA_MODEL_TIER" == "minimal_wire" ]]; then
    MODELS=(qwen3:0.6b)
    OPENCLAW_PRIMARY="ollama/qwen3:0.6b"
    OPENCLAW_FALLBACKS='[]'
    PREFERRED_SAFE_MODEL_TIER_RESULT="SKIPPED_MINIMAL"
    MINIMAL_WIRE_MODEL_RESULT="UNKNOWN"
  else
    MODELS=(qwen3:0.6b qwen3.5:2b qwen3.5:4b qwen3.5:9b)
    PREFERRED_SAFE_MODEL_TIER_RESULT="UNKNOWN"
    MINIMAL_WIRE_MODEL_RESULT="NOT_REQUESTED"
  fi
  OLLAMA_MODEL_PULL_ATTEMPTED="NO"
  OLLAMA_MODEL_PULL_RESULT="UNKNOWN"
  OLLAMA_MODEL_PULL_FAILURE_REASON="unknown"
  OLLAMA_MODEL_PULL_ATTEMPTS="0"

  if [[ "$SKIP_MODELS" != "1" ]]; then
    OLLAMA_MODEL_PULL_ATTEMPTED="YES"
    log "Models queued for pull (tier=${OLLAMA_MODEL_TIER}): ${MODELS[*]}"
    if ask_yes_no "Pull these Ollama models now? This can download many tens of GB." "n"; then
      for model in "${MODELS[@]}"; do
        if ! pull_ollama_model_with_retry "$model"; then
          if [[ "$OLLAMA_MODEL_TIER" == "minimal_wire" ]]; then
            MINIMAL_WIRE_MODEL_RESULT="FAIL"
            PREFERRED_SAFE_MODEL_TIER_RESULT="SKIPPED_MINIMAL"
          else
            PREFERRED_SAFE_MODEL_TIER_RESULT="FAIL"
            MINIMAL_WIRE_MODEL_RESULT="NOT_REQUESTED"
          fi
          write_ollama_model_markers
          die "Failed pulling required model for selected tier (${OLLAMA_MODEL_TIER}): $model (${OLLAMA_MODEL_PULL_FAILURE_REASON})"
        fi
      done
    else
      OLLAMA_MODEL_PULL_RESULT="FAIL"
      OLLAMA_MODEL_PULL_FAILURE_REASON="operator-skipped-required-model-pulls"
      write_ollama_model_markers
      die "Model pulls are required for selected tier ${OLLAMA_MODEL_TIER}."
    fi
  else
    OLLAMA_MODEL_PULL_RESULT="FAIL"
    OLLAMA_MODEL_PULL_FAILURE_REASON="skip-models-not-allowed-for-wire-proof"
    write_ollama_model_markers
    die "--skip-models cannot be used for supervised wire proof."
  fi

  create_low_ctx_alias() {
    local source_model="$1"
    local alias_model="$2"
    local num_ctx="${3:-4096}"

    if [[ "$CREATE_LOW_CTX_ALIASES" != "1" ]]; then
      return 0
    fi

    if ! ollama list | awk 'NR>1 {print $1}' | grep -qx "$source_model"; then
      log "Skipping low-context alias $alias_model; source model missing: $source_model"
      return 0
    fi

    if ollama list | awk 'NR>1 {print $1}' | grep -qx "$alias_model"; then
      log "Low-context alias already exists: $alias_model"
      return 0
    fi

    local modelfile="$LOG_DIR/Modelfile.${alias_model//[:\/]/_}"
    cat > "$modelfile" <<EOF
FROM $source_model
PARAMETER num_ctx $num_ctx
PARAMETER num_predict 512
EOF
    log "Creating low-context alias: $alias_model FROM $source_model num_ctx=$num_ctx"
    ollama create "$alias_model" -f "$modelfile" || log "WARNING: failed to create alias $alias_model"
  }

  verify_model_gpu() {
    local model="$1"
    local expected_context="${2:-4096}"
    local safe_name="${model//[:\/]/_}"
    local out_file="$LOG_DIR/verify_${safe_name}.out.txt"
    local ps_file="$LOG_DIR/verify_${safe_name}.ps.txt"
    local status_file="$LOG_DIR/verify_${safe_name}.status.txt"

    log "Verifying Ollama model GPU/context usage: $model"
    if ! ollama list | awk 'NR>1 {print $1}' | grep -qx "$model"; then
      echo "missing" > "$status_file"
      log "Skipping $model; not installed."
      return 0
    fi

    # Keep one model loaded at a time.
    ollama stop "$model" >/dev/null 2>&1 || true
    sleep 2

    local run_timeout=90
    if [[ "$model" =~ 30b|32b|35b ]]; then
      run_timeout=180
    fi

    timeout "${run_timeout}s" ollama run "$model" "Reply with OK only." > "$out_file" 2>&1 &
    local run_pid=$!

    # Poll Ollama until the model appears or the run exits. A single fixed sleep
    # caused false "not_observed" results for qwen3.5:9b-4k on fresh installs.
    local observed=0
    local gpu_ok=0
    local context_ok=0
    local deadline=$((SECONDS + run_timeout))
    : > "$ps_file"

    while (( SECONDS < deadline )); do
      ollama ps | tee "$ps_file.tmp" >/dev/null || true
      cat "$ps_file.tmp" > "$ps_file"

      if grep -q "$model" "$ps_file"; then
        observed=1
        grep -q "100% GPU" "$ps_file" && gpu_ok=1
        grep -q "$expected_context" "$ps_file" && context_ok=1
        if [[ "$gpu_ok" == "1" && "$context_ok" == "1" ]]; then
          break
        fi
      fi

      if ! kill -0 "$run_pid" >/dev/null 2>&1; then
        ollama ps | tee "$ps_file.tmp" >/dev/null || true
        cat "$ps_file.tmp" > "$ps_file"
        if grep -q "$model" "$ps_file"; then
          observed=1
          grep -q "100% GPU" "$ps_file" && gpu_ok=1
          grep -q "$expected_context" "$ps_file" && context_ok=1
        fi
        break
      fi

      sleep 2
    done
    rm -f "$ps_file.tmp"

    {
      echo
      echo "## ollama ps final sample for $model"
      ollama ps || true
    } >> "$ps_file"

    # Do not let a stuck model test block the whole script.
    wait "$run_pid" || true
    ollama stop "$model" >/dev/null 2>&1 || true
    sleep 3

    if [[ "$observed" == "1" && "$gpu_ok" == "1" && "$context_ok" == "1" ]]; then
      echo "gpu_${expected_context}" > "$status_file"
      log "GPU/context observed for $model"
    elif [[ "$observed" == "1" && "$gpu_ok" == "1" ]]; then
      echo "gpu_context_unconfirmed" > "$status_file"
      log "WARNING: $model showed 100% GPU but context $expected_context was not confirmed."
    elif [[ "$observed" == "1" ]]; then
      echo "loaded_no_gpu_observed" > "$status_file"
      log "WARNING: $model loaded, but GPU was not observed in ollama ps."
    else
      echo "not_observed" > "$status_file"
      log "WARNING: $model was not observed in ollama ps during verification."
    fi
  }

  run_model_verification_suite() {
    if [[ "$VERIFY_MODELS" != "1" ]]; then
      log "Skipping per-model GPU verification by user choice."
      return 0
    fi

    log "Preparing model surfaces before verification (tier=${OLLAMA_MODEL_TIER})"
    if [[ "$OLLAMA_MODEL_TIER" == "minimal_wire" ]]; then
      log "Minimal wire uses base qwen3:0.6b with its 32768 context; no 4K alias required."
    else
      create_low_ctx_alias qwen3.5:9b qwen3.5:9b-4k 4096
      create_low_ctx_alias qwen3.5:4b qwen3.5:4b-4k 4096
      create_low_ctx_alias qwen3.5:2b qwen3.5:2b-4k 4096
      create_low_ctx_alias qwen3:0.6b qwen3:0.6b-4k 4096
    fi

    if [[ "$INCLUDE_REASONING_MODEL" == "1" ]]; then
      create_low_ctx_alias qwen3:30b-thinking qwen3:30b-thinking-4k 4096
    else
      log "Skipping Qwen3 30B Thinking alias. Use --include-reasoning-model for supervised testing."
    fi

    if [[ "$INCLUDE_CODER_MODEL" == "1" ]]; then
      create_low_ctx_alias qwen3-coder:30b qwen3-coder:30b-4k 4096
    else
      log "Skipping Qwen3 Coder 30B alias. Use --include-coder-model for supervised testing."
    fi

    if [[ "$INCLUDE_RISKY_MODELS" == "1" ]]; then
      create_low_ctx_alias qwen2.5-coder:32b qwen2.5-coder:32b-4k 4096
      create_low_ctx_alias qwen3:32b qwen3:32b-4k 4096
      create_low_ctx_alias qwen3.6:35b qwen3.6:35b-4k 4096
    fi

    local verify_models=()
    if [[ "$OLLAMA_MODEL_TIER" == "minimal_wire" ]]; then
      verify_models=(qwen3:0.6b)
    else
      verify_models=(qwen3.5:9b-4k qwen3.5:4b-4k qwen3.5:2b-4k qwen3:0.6b-4k)
    fi

    if [[ "$OLLAMA_MODEL_TIER" != "minimal_wire" && ("$VERIFY_TIER" == "medium" || "$VERIFY_TIER" == "all") && "$INCLUDE_REASONING_MODEL" == "1" ]]; then
      verify_models+=(qwen3:30b-thinking-4k)
    elif [[ "$VERIFY_TIER" == "medium" || "$VERIFY_TIER" == "all" ]]; then
      log "Reasoning verification tier requested, but --include-reasoning-model was not set. Staying on bounded safe models."
    fi

    if [[ "$OLLAMA_MODEL_TIER" != "minimal_wire" && ("$VERIFY_TIER" == "medium" || "$VERIFY_TIER" == "all") && "$INCLUDE_CODER_MODEL" == "1" ]]; then
      verify_models+=(qwen3-coder:30b-4k)
    fi

    if [[ "$OLLAMA_MODEL_TIER" != "minimal_wire" && "$VERIFY_TIER" == "all" && "$INCLUDE_RISKY_MODELS" == "1" ]]; then
      verify_models+=(qwen2.5-coder:32b-4k qwen3:32b-4k qwen3.6:35b-4k)
    fi

    log "Model verification tier: $VERIFY_TIER"
    log "Models queued for verification: ${verify_models[*]}"

    for model in "${verify_models[@]}"; do
      if [[ "$OLLAMA_MODEL_TIER" == "minimal_wire" && "$model" == "qwen3:0.6b" ]]; then
        verify_model_gpu "$model" 32768
      else
        verify_model_gpu "$model" 4096
      fi
    done

    if [[ "$OLLAMA_MODEL_TIER" == "minimal_wire" ]]; then
      if [[ -f "$LOG_DIR/verify_qwen3_0.6b.status.txt" ]] && grep -q 'gpu_32768' "$LOG_DIR/verify_qwen3_0.6b.status.txt"; then
        MINIMAL_WIRE_MODEL_RESULT="PASS"
      else
        OLLAMA_MODEL_PULL_RESULT="FAIL"
        OLLAMA_MODEL_PULL_FAILURE_REASON="gpu-context-verification-failed"
        MINIMAL_WIRE_MODEL_RESULT="FAIL"
        write_ollama_model_markers
        die "Minimal wire model verification failed for qwen3:0.6b with context 32768"
      fi
    else
      PREFERRED_SAFE_MODEL_TIER_RESULT="PASS"
    fi

    log "Model verification summary"
    {
      echo "model,status"
      for f in "$LOG_DIR"/verify_*.status.txt; do
        [[ -f "$f" ]] || continue
        base="$(basename "$f" .status.txt)"
        model="${base#verify_}"
        echo "$model,$(cat "$f")"
      done
    } | tee "$LOG_DIR/model_verification_summary.csv"
  }


  log "Ollama model list"
  ollama list || true

  run_model_verification_suite
  if [[ "$OLLAMA_MODEL_TIER" == "safe_full" && "$PREFERRED_SAFE_MODEL_TIER_RESULT" == "UNKNOWN" ]]; then
    PREFERRED_SAFE_MODEL_TIER_RESULT="PASS"
  fi

  log "Running final Ollama GPU smoke test with qwen3:0.6b"
  ollama pull qwen3:0.6b >/dev/null 2>&1 || true
  timeout 90s ollama run qwen3:0.6b "Reply with OK only." >/tmp/openclaw_ollama_smoke.txt 2>&1 || true
  ollama ps | tee "$LOG_DIR/ollama_ps_after_smoke.txt" || true

  if ollama ps | grep -qi 'GPU'; then
    log "Ollama reports GPU usage."
  else
    log "WARNING: ollama ps did not show GPU usage. Check journalctl -u ollama."
  fi
  write_ollama_model_markers
fi

if [[ "$SKIP_OPENCLAW" != "1" ]]; then
  log "Installing OpenClaw after Ollama/model setup"
  record_linux_path_state "BeforeOpenClawInstall"
  assert_not_windows_resolution "node" "linuxNodeResolutionBeforeOpenClawInstallGate" "LINUX_NODE_WINDOWS_SHIM_DETECTED_BEFORE_OPENCLAW_INSTALL"
  assert_not_windows_resolution "npm" "linuxNpmResolutionBeforeOpenClawInstallGate" "LINUX_NPM_WINDOWS_SHIM_DETECTED_BEFORE_OPENCLAW_INSTALL"
  assert_not_windows_resolution "openclaw" "openclawResolutionBeforeOpenClawInstallGate" "OPENCLAW_WINDOWS_SHIM_DETECTED_BEFORE_OPENCLAW_INSTALL"
  # Do not call plain `sudo -v` here. With mixed sudoers entries, `sudo -v`
  # can still prompt even when command-specific NOPASSWD sudo works.
  # `sudo -n true` is the automation-safe check; it fails instead of prompting.
  if ! sudo -n true 2>/dev/null; then
    log "sudo credential timestamp unavailable before OpenClaw install; prompting once."
    sudo -v
  fi
  OPENCLAW_NPM_INSTALL_ATTEMPTED="YES"
  OPENCLAW_NPM_INSTALL_RESULT="UNKNOWN"
  OPENCLAW_NPM_INSTALL_ATTEMPTS="0"
  OPENCLAW_NPM_INSTALL_FAILURE_REASON="unknown"
  OPENCLAW_NPM_INSTALL_DURATION_SECONDS="0"
  OPENCLAW_NPM_LOG="$LOG_DIR/openclaw_npm_install.log"
  npm_stage_start_epoch="$(date +%s)"
  {
    echo "=== OpenClaw npm install diagnostics ==="
    echo "package_spec=$OPENCLAW_NPM_PACKAGE_SPEC"
    echo "timeout_seconds=$OPENCLAW_NPM_INSTALL_TIMEOUT_SECONDS"
    echo "max_attempts=$OPENCLAW_NPM_INSTALL_MAX_ATTEMPTS"
    echo "retry_delay_seconds=$OPENCLAW_NPM_INSTALL_RETRY_DELAY_SECONDS"
    echo "started_at=$(date -Iseconds)"
    echo "node_version=$(node --version 2>/dev/null || echo UNKNOWN)"
    echo "npm_version=$(npm --version 2>/dev/null || echo UNKNOWN)"
    echo "npm_registry=$(npm config get registry 2>/dev/null || echo UNKNOWN)"
    echo "npm_cache=$(npm config get cache 2>/dev/null || echo UNKNOWN)"
    echo "======================================="
  } > "$OPENCLAW_NPM_LOG"

  npm_install_ok=0
  for ((attempt=1; attempt<=OPENCLAW_NPM_INSTALL_MAX_ATTEMPTS; attempt++)); do
    OPENCLAW_NPM_INSTALL_ATTEMPTS="$attempt"
    attempt_start_iso="$(date -Iseconds)"
    log "OpenClaw npm install attempt ${attempt}/${OPENCLAW_NPM_INSTALL_MAX_ATTEMPTS} (timeout ${OPENCLAW_NPM_INSTALL_TIMEOUT_SECONDS}s)"
    {
      echo
      echo "attempt=$attempt"
      echo "attempt_started_at=$attempt_start_iso"
      echo "command=sudo -n npm install -g $OPENCLAW_NPM_PACKAGE_SPEC"
    } >> "$OPENCLAW_NPM_LOG"

    set +e
    if timeout "${OPENCLAW_NPM_INSTALL_TIMEOUT_SECONDS}s" sudo -n npm install -g "$OPENCLAW_NPM_PACKAGE_SPEC" >> "$OPENCLAW_NPM_LOG" 2>&1; then
      attempt_rc=0
    else
      attempt_rc=$?
    fi
    set -e

    attempt_end_iso="$(date -Iseconds)"
    {
      echo "attempt_finished_at=$attempt_end_iso"
      echo "attempt_exit_code=$attempt_rc"
    } >> "$OPENCLAW_NPM_LOG"

    if [[ "$attempt_rc" == "0" ]]; then
      OPENCLAW_NPM_INSTALL_RESULT="PASS"
      OPENCLAW_NPM_INSTALL_FAILURE_REASON="none"
      npm_install_ok=1
      break
    fi

    if [[ "$attempt_rc" == "124" ]]; then
      OPENCLAW_NPM_INSTALL_RESULT="TIMEOUT"
      OPENCLAW_NPM_INSTALL_FAILURE_REASON="npm-timeout"
      log "WARNING: OpenClaw npm install attempt ${attempt} timed out."

      hash -r
      resolved_openclaw_after_timeout="$(resolve_cmd_path openclaw)"
      if [[ "$resolved_openclaw_after_timeout" != "MISSING" && "$resolved_openclaw_after_timeout" != /mnt/c/* ]]; then
        log "OpenClaw command resolves after npm timeout at ${resolved_openclaw_after_timeout}; validating before accepting post-timeout install state."
        if openclaw --version >> "$OPENCLAW_NPM_LOG" 2>&1; then
          OPENCLAW_NPM_INSTALL_RESULT="PASS"
          OPENCLAW_NPM_INSTALL_FAILURE_REASON="none"
          npm_install_ok=1
          write_wire_marker "openclawNpmInstallPostTimeoutGuardResult" "PASS"
          log "OpenClaw npm timeout left a usable Linux OpenClaw command; accepting post-timeout install state."
          break
        else
          write_wire_marker "openclawNpmInstallPostTimeoutGuardResult" "FAIL_VERSION_CHECK"
          log "WARNING: OpenClaw command resolved after npm timeout, but openclaw --version failed."
        fi
      else
        write_wire_marker "openclawNpmInstallPostTimeoutGuardResult" "FAIL_COMMAND_MISSING_OR_WINDOWS_PATH"
      fi
    else
      OPENCLAW_NPM_INSTALL_RESULT="FAIL"
      OPENCLAW_NPM_INSTALL_FAILURE_REASON="npm-exit-nonzero"
      log "WARNING: OpenClaw npm install attempt ${attempt} failed with exit code ${attempt_rc}."
    fi

    if (( attempt < OPENCLAW_NPM_INSTALL_MAX_ATTEMPTS )); then
      sleep "$OPENCLAW_NPM_INSTALL_RETRY_DELAY_SECONDS"
    fi
  done
  npm_stage_end_epoch="$(date +%s)"
  OPENCLAW_NPM_INSTALL_DURATION_SECONDS="$((npm_stage_end_epoch - npm_stage_start_epoch))"
  write_openclaw_npm_markers

  if [[ "$npm_install_ok" != "1" ]]; then
    write_wire_marker "openclawCommandResolutionGuardResult" "FAIL"
    die "OpenClaw npm install failed (${OPENCLAW_NPM_INSTALL_FAILURE_REASON}) after ${OPENCLAW_NPM_INSTALL_ATTEMPTS} attempt(s). See $OPENCLAW_NPM_LOG"
  fi

  hash -r
  apply_linux_path_hardening
  record_linux_path_state "AfterOpenClawInstall"

  if ! command -v openclaw >/dev/null 2>&1; then
    OPENCLAW_NPM_INSTALL_RESULT="FAIL"
    OPENCLAW_NPM_INSTALL_FAILURE_REASON="openclaw-command-missing-after-install"
    write_openclaw_npm_markers
    write_wire_marker "openclawCommandResolutionGuardResult" "FAIL"
    die "openclaw command not found after npm install. See $OPENCLAW_NPM_LOG"
  fi
  assert_not_windows_resolution "openclaw" "openclawResolutionAfterInstallGate" "OPENCLAW_WINDOWS_SHIM_DETECTED_AFTER_INSTALL"
  if ! openclaw --version >> "$OPENCLAW_NPM_LOG" 2>&1; then
    OPENCLAW_NPM_INSTALL_RESULT="FAIL"
    OPENCLAW_NPM_INSTALL_FAILURE_REASON="openclaw-version-check-failed"
    write_openclaw_npm_markers
    write_wire_marker "openclawCommandResolutionGuardResult" "FAIL"
    die "openclaw --version failed after npm install. See $OPENCLAW_NPM_LOG"
  fi
  write_wire_marker "openclawCommandResolutionGuardResult" "PASS"
  write_openclaw_npm_markers

  OPENCLAW_REPRO_COMPAT_HELPER="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/apply_openclaw_repro_compat_layer_v1_7.sh"
  [[ -f "$OPENCLAW_REPRO_COMPAT_HELPER" ]] || die "Missing OpenClaw repro compatibility helper: $OPENCLAW_REPRO_COMPAT_HELPER"
  chmod +x "$OPENCLAW_REPRO_COMPAT_HELPER"
  log "Running OpenClaw identity verification and fail-closed compatibility stage"
  write_wire_marker "openclawCompatibilityPrivilegeMode" "sudo-root"
  write_wire_marker "openclawCompatibilityPrivilegeResult" "IN_PROGRESS"
  write_wire_marker "openclawCompatibilityPrivilegeReason" "awaiting-root-assisted-helper"
  compat_owner_user="$(id -un)"
  compat_owner_group="$(id -gn)"
  set +e
  sudo -n env \
    PATH="$PATH" \
    WIRE_MARKER_DIR="$WIRE_MARKER_DIR" \
    OPENCLAW_NPM_PACKAGE_SPEC="$OPENCLAW_NPM_PACKAGE_SPEC" \
    OPENCLAW_EXPECTED_IDENTITY="$OPENCLAW_EXPECTED_IDENTITY" \
    OPENCLAW_EXPECTED_BUILD_ID="$OPENCLAW_EXPECTED_BUILD_ID" \
    OPENCLAW_EXPECTED_PACKAGE_VERSION="$OPENCLAW_EXPECTED_PACKAGE_VERSION" \
    OPENCLAW_IDENTITY_POLICY="$OPENCLAW_IDENTITY_POLICY" \
    OPENCLAW_COMPAT_ORIGINAL_USER="$compat_owner_user" \
    OPENCLAW_COMPAT_ORIGINAL_GROUP="$compat_owner_group" \
    OPENCLAW_COMPAT_PRIVILEGE_MODE="sudo-root" \
    bash "$OPENCLAW_REPRO_COMPAT_HELPER" --log-dir "$LOG_DIR" --marker-dir "$WIRE_MARKER_DIR"
  compat_helper_rc=$?
  set -e
  compat_report="${LOG_DIR}/openclaw_repro_compat_stage_report.md"
  compat_summary="${LOG_DIR}/openclaw_repro_compat_stage_summary.json"
  if [[ -f "$compat_report" || -f "$compat_summary" || -d "$WIRE_MARKER_DIR" ]]; then
    sudo -n bash -lc '
      shopt -s nullglob
      files=()
      [[ -f "$1" ]] && files+=("$1")
      [[ -f "$2" ]] && files+=("$2")
      for f in "$3"/openclaw*.marker; do files+=("$f"); done
      if (( ${#files[@]} > 0 )); then
        chown "$4:$5" "${files[@]}"
        chmod 0644 "${files[@]}" 2>/dev/null || true
      fi
    ' _ "$compat_report" "$compat_summary" "$WIRE_MARKER_DIR" "$compat_owner_user" "$compat_owner_group" 2>/dev/null || true
  fi
  if [[ "$compat_helper_rc" != "0" ]]; then
    if [[ -z "$(compatibility_marker_val openclawCompatibilityPrivilegeResult)" || "$(compatibility_marker_val openclawCompatibilityPrivilegeResult)" == "IN_PROGRESS" ]]; then
      write_wire_marker "openclawCompatibilityPrivilegeMode" "sudo-root"
      write_wire_marker "openclawCompatibilityPrivilegeResult" "FAIL"
      write_wire_marker "openclawCompatibilityPrivilegeReason" "sudo-root-helper-exit-${compat_helper_rc}"
    fi
    die "OpenClaw compatibility helper failed under sudo-root privilege mode (rc=${compat_helper_rc}). See ${compat_report} and ${compat_summary}"
  fi

  log "Repairing user config ownership before OpenClaw environment persistence"
  sudo mkdir -p "$HOME/.config/environment.d"
  sudo chown -R "$USER:$USER" "$HOME/.config"
  chmod 700 "$HOME/.config" || true
  chmod 700 "$HOME/.config/environment.d" || true
  log "Persisting OLLAMA_API_KEY=ollama-local for OpenClaw Ollama provider"
  mkdir -p "$HOME/.openclaw" "$HOME/.config/environment.d"
  touch "$HOME/.openclaw/.env"
  if grep -q '^OLLAMA_API_KEY=' "$HOME/.openclaw/.env"; then
    sed -i 's/^OLLAMA_API_KEY=.*/OLLAMA_API_KEY=ollama-local/' "$HOME/.openclaw/.env"
  else
    printf '\nOLLAMA_API_KEY=ollama-local\n' >> "$HOME/.openclaw/.env"
  fi
  cat > "$HOME/.config/environment.d/openclaw-ollama.conf" <<'EOF'
OLLAMA_API_KEY=ollama-local
EOF
  chmod 600 "$HOME/.openclaw/.env" "$HOME/.config/environment.d/openclaw-ollama.conf"
  export OLLAMA_API_KEY=ollama-local
  systemctl --user import-environment OLLAMA_API_KEY || true

  log "Patching OpenClaw explicit Ollama provider config for selected model tier"
  export ORCH_INCLUDE_REASONING_MODEL="$INCLUDE_REASONING_MODEL"
  export ORCH_INCLUDE_CODER_MODEL="$INCLUDE_CODER_MODEL"
  export ORCH_PROMOTE_REASONING_MODEL="$PROMOTE_REASONING_MODEL"
  export ORCH_PROMOTE_CODER_MODEL="$PROMOTE_CODER_MODEL"
  export ORCH_MINIMAL_WIRE_MODEL="$MINIMAL_WIRE_MODEL"
  python3 - <<'PY'
import json, time, os
from pathlib import Path
p = Path.home() / '.openclaw' / 'openclaw.json'
p.parent.mkdir(parents=True, exist_ok=True)
if p.exists():
    cfg = json.loads(p.read_text())
    backup = p.with_name(f'openclaw.json.before-v8-explicit-ollama.{time.strftime("%Y%m%d_%H%M%S")}.bak')
    backup.write_text(json.dumps(cfg, indent=2) + '\n')
else:
    cfg = {}

cfg.setdefault('models', {})
cfg['models'].setdefault('providers', {})

def model(mid, name, max_tokens=1024, num_predict=512, context_window=4096):
    return {
        'id': mid,
        'name': name,
        'reasoning': False,
        'input': ['text'],
        'cost': {'input': 0, 'output': 0, 'cacheRead': 0, 'cacheWrite': 0},
        'contextWindow': context_window,
        'contextTokens': context_window,
        'maxTokens': max_tokens,
        'params': {'num_ctx': context_window, 'num_predict': num_predict, 'temperature': 0.2, 'think': False},
    }

if os.environ.get('ORCH_MINIMAL_WIRE_MODEL') == '1':
    provider_context = 32768
    provider_models = [model('qwen3:0.6b', 'Qwen 3 0.6B', 512, 256, provider_context)]
else:
    provider_context = 4096
    provider_models = [
        model('qwen3.5:9b-4k', 'Qwen 3.5 9B 4K'),
        model('qwen3.5:4b-4k', 'Qwen 3.5 4B 4K'),
        model('qwen3.5:2b-4k', 'Qwen 3.5 2B 4K'),
        model('qwen3:0.6b-4k', 'Qwen 3 0.6B 4K', 512, 256),
    ]

if os.environ.get('ORCH_MINIMAL_WIRE_MODEL') != '1' and os.environ.get('ORCH_INCLUDE_REASONING_MODEL') == '1':
    m = model('qwen3:30b-thinking-4k', 'Qwen 3 30B Thinking 4K', 1024, 512)
    m['reasoning'] = True
    m['params']['think'] = True
    provider_models.append(m)

if os.environ.get('ORCH_MINIMAL_WIRE_MODEL') != '1' and os.environ.get('ORCH_INCLUDE_CODER_MODEL') == '1':
    provider_models.append(model('qwen3-coder:30b-4k', 'Qwen 3 Coder 30B 4K', 1024, 512))

cfg['models']['providers']['ollama'] = {
    'baseUrl': 'http://127.0.0.1:11434',
    'apiKey': 'ollama-local',
    'api': 'ollama',
    'contextWindow': provider_context,
    'contextTokens': provider_context,
    'maxTokens': 1024,
    'timeoutSeconds': 240,
    'models': provider_models,
}

cfg.setdefault('gateway', {})
cfg['gateway']['bind'] = 'loopback'
cfg.setdefault('agents', {})
cfg['agents'].setdefault('defaults', {})
if os.environ.get('ORCH_MINIMAL_WIRE_MODEL') == '1':
    cfg['agents']['defaults']['model'] = {
        'primary': 'ollama/qwen3:0.6b',
        'fallbacks': [],
    }
else:
    cfg['agents']['defaults']['model'] = {
        'primary': 'ollama/qwen3.5:9b-4k',
        'fallbacks': ['ollama/qwen3.5:4b-4k', 'ollama/qwen3.5:2b-4k', 'ollama/qwen3:0.6b-4k'],
    }
p.write_text(json.dumps(cfg, indent=2) + '\n')
print(f'patched {p}')
PY

  log "Configuring OpenClaw default model object"
  MODEL_JSON="{\"primary\":\"${OPENCLAW_PRIMARY}\",\"fallbacks\":${OPENCLAW_FALLBACKS}}"
  openclaw config set agents.defaults.model "$MODEL_JSON" --strict-json
  openclaw config get agents.defaults.model --json | tee "$LOG_DIR/openclaw_model_config.json"

  log "Configuring OpenClaw gateway local mode and token"
  openclaw config set gateway.mode local
  openclaw config set gateway.bind loopback || true

  GATEWAY_TOKEN="${OPENCLAW_GATEWAY_TOKEN:-sk-OPENCLAW-$(openssl rand -hex 32)}"
  openclaw config set gateway.auth.mode token || true
  openclaw config set gateway.auth.token "$GATEWAY_TOKEN" || true

  mkdir -p "$HOME/.openclaw/agents/main/sessions"

  if [[ -n "$DISCORD_OWNER_ID" ]]; then
    log "Configuring OpenClaw command owner for Discord ID: $DISCORD_OWNER_ID"
    openclaw config set commands.ownerAllowFrom "[\"discord:${DISCORD_OWNER_ID}\"]" --strict-json
  fi

  if [[ "$WITH_DISCORD" == "1" ]]; then
    log "Configuring Discord channel token env-ref"
    if [[ -z "${!DISCORD_TOKEN_ENV:-}" ]]; then
      read -rsp "Paste Discord bot token for ${DISCORD_TOKEN_ENV}: " TOKEN_INPUT
      echo
      export "${DISCORD_TOKEN_ENV}=${TOKEN_INPUT}"
    fi

    mkdir -p "$HOME/.openclaw" "$HOME/.config/environment.d"
    umask 077
    printf '%s=%s\n' "$DISCORD_TOKEN_ENV" "${!DISCORD_TOKEN_ENV}" > "$HOME/.openclaw/.env"
    printf '%s=%s\n' "$DISCORD_TOKEN_ENV" "${!DISCORD_TOKEN_ENV}" > "$HOME/.config/environment.d/openclaw-discord.conf"
    chmod 600 "$HOME/.openclaw/.env" "$HOME/.config/environment.d/openclaw-discord.conf"

    openclaw config set channels.discord.token \
      --ref-provider default \
      --ref-source env \
      --ref-id "$DISCORD_TOKEN_ENV"
    openclaw config set channels.discord.enabled true --strict-json
    openclaw config set channels.discord.groupPolicy allowlist || true
    systemctl --user import-environment "$DISCORD_TOKEN_ENV" || true
  fi

  log "Installing and starting OpenClaw gateway service"
  openclaw gateway install --force || openclaw gateway install || true
  sudo loginctl enable-linger "$USER" || true
  systemctl --user daemon-reload
  systemctl --user enable openclaw-gateway.service || true
  systemctl --user restart openclaw-gateway.service

  sleep 5
  systemctl --user status openclaw-gateway.service --no-pager | tee "$LOG_DIR/openclaw_gateway_status.txt" || true
  journalctl --user -u openclaw-gateway.service -n 120 --no-pager | tee "$LOG_DIR/openclaw_gateway_journal_last120.txt" || true

  if systemctl --user is-active --quiet openclaw-gateway.service; then
    log "OpenClaw gateway is active."
  else
    die "OpenClaw gateway did not become active."
  fi
fi

restore_archive() {
  local archive="$1"
  [[ -f "$archive" ]] || die "Archive not found: $archive"

  log "Restoring OpenClaw from archive: $archive"
  mkdir -p "$CODE_DIR"

  local prefix=""
  if tar -tf "$archive" | grep -q '^projects/'; then
    prefix="projects"
  elif tar -tf "$archive" | grep -q '^codex/projects/'; then
    prefix="codex/projects"
  elif tar -tf "$archive" | grep -q '^home/roger/codex/projects/'; then
    prefix="home/roger/codex/projects"
  else
    die "Could not find projects/, codex/projects/, or home/roger/codex/projects/ inside archive."
  fi

  local tmp
  tmp="$(mktemp -d)"
  tar -xzf "$archive" -C "$tmp" "$prefix"

  mkdir -p "$PROJECT_DIR"
  rsync -a --delete \
    --exclude='.venv' \
    --exclude='venv' \
    --exclude='node_modules' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='*:Zone.Identifier' \
    "$tmp/$prefix/" "$PROJECT_DIR/"

  rm -rf "$tmp"

  find "$PROJECT_DIR" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
  find "$PROJECT_DIR" -name '*.pyc' -delete 2>/dev/null || true
  find "$PROJECT_DIR" -name '*:Zone.Identifier' -delete 2>/dev/null || true

  log "OpenClaw restored to: $PROJECT_DIR"

  if [[ -f "$PROJECT_DIR/main.py" ]]; then
    python3 -m venv "$PROJECT_DIR/.venv"
    # shellcheck disable=SC1091
    source "$PROJECT_DIR/.venv/bin/activate"
    (cd "$PROJECT_DIR" && python main.py --help >/dev/null 2>&1 || true)
    deactivate || true
  fi

  mkdir -p "$HOME/bin"
  cat > "$HOME/bin/orch" <<EOF
#!/usr/bin/env bash
cd "$PROJECT_DIR" || exit 1
if [ -f ".venv/bin/activate" ]; then
  source ".venv/bin/activate"
fi
exec python main.py "\$@"
EOF
  chmod +x "$HOME/bin/orch"
}

if [[ -n "$ARCHIVE_PATH" ]]; then
  restore_archive "$ARCHIVE_PATH"
else
  log "No --archive provided. Skipping OpenClaw restore."
fi

log "Writing redacted OpenClaw config snapshot"
if [[ -f "$HOME/.openclaw/openclaw.json" ]]; then
  python3 - <<'PY' > "$RED_DIR/openclaw.redacted.json" 2>/dev/null || true
import json, os
p=os.path.expanduser("~/.openclaw/openclaw.json")
data=json.load(open(p))
def redact(x):
    if isinstance(x, dict):
        out={}
        for k,v in x.items():
            if any(s in k.lower() for s in ["token","secret","password","key"]):
                out[k]="<REDACTED>"
            else:
                out[k]=redact(v)
        return out
    if isinstance(x, list):
        return [redact(v) for v in x]
    return x
print(json.dumps(redact(data), indent=2, sort_keys=True))
PY
fi

log "Writing summary"
{
  echo "# REDO WSL OPENCLAW v1 one-shot bootstrap summary"
  echo
  echo "Created: $(date -Iseconds)"
  echo "User: $USER"
  echo "Host: $(hostname)"
  echo "Log: $LOG_FILE"
  echo
  echo "## Versions"
  command -v node >/dev/null && echo "node: $(node --version)"
  command -v npm >/dev/null && echo "npm: $(npm --version)"
  command -v openclaw >/dev/null && echo "openclaw: $(openclaw --version)"
  command -v ollama >/dev/null && echo "ollama: $(ollama --version)"
  command -v zsh >/dev/null && echo "zsh: $(zsh --version)"
  echo
  echo "## Evidence"
  echo "- Ollama ps after smoke: $LOG_DIR/ollama_ps_after_smoke.txt"
  echo "- Model verification summary: $LOG_DIR/model_verification_summary.csv"
  if [[ "$OLLAMA_MODEL_TIER" == "minimal_wire" ]]; then
    echo "- OpenClaw minimal-wire provider uses qwen3:0.6b with contextWindow/contextTokens/num_ctx=32768"
  else
    echo "- OpenClaw safe-full provider uses bounded contextWindow/contextTokens/num_ctx=4096"
  fi
  echo "- OpenClaw gateway status: $LOG_DIR/openclaw_gateway_status.txt"
  echo "- OpenClaw gateway journal: $LOG_DIR/openclaw_gateway_journal_last120.txt"
  echo "- Redacted OpenClaw config: $RED_DIR/openclaw.redacted.json"
  echo "- Shell customization attempted: $SHELL_CUSTOMIZATION_ATTEMPTED"
  echo "- Shell customization result: $SHELL_CUSTOMIZATION_RESULT"
  echo "- Shell customization failure reason: $SHELL_CUSTOMIZATION_FAILURE_REASON"
  echo "- OpenClaw npm install attempted: $OPENCLAW_NPM_INSTALL_ATTEMPTED"
  echo "- OpenClaw npm install result: $OPENCLAW_NPM_INSTALL_RESULT"
  echo "- OpenClaw npm install attempts: $OPENCLAW_NPM_INSTALL_ATTEMPTS"
  echo "- OpenClaw npm install failure reason: $OPENCLAW_NPM_INSTALL_FAILURE_REASON"
  echo "- OpenClaw npm install duration seconds: $OPENCLAW_NPM_INSTALL_DURATION_SECONDS"
  echo "- Ollama model tier: $OLLAMA_MODEL_TIER"
  echo "- Ollama model pull attempted: $OLLAMA_MODEL_PULL_ATTEMPTED"
  echo "- Ollama model pull result: $OLLAMA_MODEL_PULL_RESULT"
  echo "- Ollama model pull failure reason: $OLLAMA_MODEL_PULL_FAILURE_REASON"
  echo "- Ollama model pull attempts: $OLLAMA_MODEL_PULL_ATTEMPTS"
  echo "- Preferred safe model tier result: $PREFERRED_SAFE_MODEL_TIER_RESULT"
  echo "- Minimal wire model result: $MINIMAL_WIRE_MODEL_RESULT"
  echo
  echo "## Manual items"
  echo "- Close/reopen WSL after completion so zsh becomes the login shell."
  echo "- Windows Terminal font: select MesloLGS NF / Nerd Font for Powerlevel10k."
  echo "- Discord Developer Portal intents are separate if --with-discord is used."
  echo "- qwen3:30b-thinking is opt-in behind --include-reasoning-model and should not be promoted automatically."
  echo "- qwen3-coder:30b is opt-in behind --include-coder-model and should not be promoted automatically."
  echo "- qwen3.6:35b is intentionally excluded unless --include-risky-models is used."
} > "$SUMMARY_FILE"

log "Creating evidence archive"
EVIDENCE_TAR="$HOME/openclaw_one_shot_bootstrap_${STAMP}.tar.gz"
tar -czf "$EVIDENCE_TAR" -C "$LOG_ROOT" "$STAMP"

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
  cp "$EVIDENCE_TAR" "$EXPORT_DIR/" || true
  log "Evidence archive copied to: $EXPORT_DIR/$(basename "$EVIDENCE_TAR")"
else
  warn "No writable Windows Downloads folder found for evidence archive export. Local archive remains: $EVIDENCE_TAR"
fi

log "Completed v1 one-shot bootstrap"
cat "$SUMMARY_FILE"

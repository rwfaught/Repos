#!/usr/bin/env bash
# run_openclaw_install_from_config.sh
#
# Linux-side package runner.
# Reads /home/<user>/openclaw_install/config/install_config.json
# and calls the package scripts with the correct flags.
#
# This wrapper keeps the PowerShell -> WSL handoff explicit:
#   PowerShell writes config.
#   Bash reads config.
#   Each stage logs and proves itself.

set -Eeuo pipefail

SCRIPT_NAME="$(basename "$0")"
CONFIG_PATH=""
PACKAGE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_ROOT="${HOME}/openclaw_install"
LOG_ROOT="${INSTALL_ROOT}/logs"
STAMP="$(date +%Y%m%d_%H%M%S)"
RUN_LOG_DIR="${LOG_ROOT}/${STAMP}"
RUN_LOG="${RUN_LOG_DIR}/runner.log"

mkdir -p "$RUN_LOG_DIR"
exec > >(tee -a "$RUN_LOG") 2>&1

log() { printf '\n[%s] %s\n' "$SCRIPT_NAME" "$*"; }
die() { printf '\n[%s] ERROR: %s\n' "$SCRIPT_NAME" "$*" >&2; exit 1; }

usage() {
  cat <<'EOF'
Usage:
  bash run_openclaw_install_from_config.sh --config /path/to/install_config.json
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --config) CONFIG_PATH="${2:-}"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) die "Unknown option: $1" ;;
  esac
done

[[ -n "$CONFIG_PATH" ]] || { usage; die "--config is required"; }
[[ -f "$CONFIG_PATH" ]] || die "Config file not found: $CONFIG_PATH"
command -v python3 >/dev/null 2>&1 || die "python3 not found. PowerShell init should install python3 before this runner."

json_get() {
  local expr="$1"
  python3 - "$CONFIG_PATH" "$expr" <<'PY'
import json, sys
path, expr = sys.argv[1], sys.argv[2]
data = json.load(open(path, encoding="utf-8"))
cur = data
for part in expr.split("."):
    if not part:
        continue
    if isinstance(cur, dict) and part in cur:
        cur = cur[part]
    else:
        cur = None
        break
if isinstance(cur, bool):
    print("true" if cur else "false")
elif cur is None:
    print("")
else:
    print(cur)
PY
}

json_array_lines() {
  local expr="$1"
  python3 - "$CONFIG_PATH" "$expr" <<'PY'
import json, sys
path, expr = sys.argv[1], sys.argv[2]
data = json.load(open(path, encoding="utf-8"))
cur = data
for part in expr.split("."):
    if not part:
        continue
    if isinstance(cur, dict) and part in cur:
        cur = cur[part]
    else:
        cur = []
        break
if isinstance(cur, list):
    for item in cur:
        print(item)
PY
}

bool_is_true() {
  [[ "$(json_get "$1")" == "true" ]]
}

log "Starting config-driven OpenClaw install runner"
log "Package dir: $PACKAGE_DIR"
log "Config: $CONFIG_PATH"
log "Runner log: $RUN_LOG"

log "Config summary"
python3 - "$CONFIG_PATH" <<'PY'
import json, sys
data=json.load(open(sys.argv[1], encoding="utf-8"))
safe=json.loads(json.dumps(data))
# Never print secret values. This config should not contain secrets anyway.
print(json.dumps(safe, indent=2, sort_keys=True))
PY

BOOTSTRAP="$PACKAGE_DIR/bootstrap_openclaw_wsl.sh"
BASELINE_VERIFY="$PACKAGE_DIR/verify_openclaw_baseline.sh"
OPTIONAL_VERIFY="$PACKAGE_DIR/verify_openclaw_optional_models.sh"
DISCORD_CONFIG="$PACKAGE_DIR/configure_openclaw_discord_v1.sh"
DISCORD_VERIFY="$PACKAGE_DIR/verify_openclaw_discord_v1.sh"

[[ -x "$BOOTSTRAP" ]] || chmod +x "$BOOTSTRAP"
[[ -x "$BASELINE_VERIFY" ]] || chmod +x "$BASELINE_VERIFY"
[[ -x "$OPTIONAL_VERIFY" ]] || chmod +x "$OPTIONAL_VERIFY" || true
[[ -x "$DISCORD_CONFIG" ]] || chmod +x "$DISCORD_CONFIG"
[[ -x "$DISCORD_VERIFY" ]] || chmod +x "$DISCORD_VERIFY"

BOOT_ARGS=(--yes)

if bool_is_true "modelPolicy.includeReasoningModel"; then
  BOOT_ARGS+=(--include-reasoning-model)
fi
if bool_is_true "modelPolicy.includeCoderModel"; then
  BOOT_ARGS+=(--include-coder-model)
fi
if bool_is_true "modelPolicy.promoteReasoningModel"; then
  BOOT_ARGS+=(--promote-reasoning-model)
fi
if bool_is_true "modelPolicy.promoteCoderModel"; then
  BOOT_ARGS+=(--promote-coder-model)
fi
if bool_is_true "modelPolicy.includeRiskyModels"; then
  BOOT_ARGS+=(--include-risky-models)
fi

while IFS= read -r extra; do
  [[ -n "$extra" ]] && BOOT_ARGS+=("$extra")
done < <(json_array_lines "bootstrap.extraArgs")

log "Running bootstrap with args: ${BOOT_ARGS[*]}"
bash "$BOOTSTRAP" "${BOOT_ARGS[@]}"

if bool_is_true "verification.runBaselineVerifier"; then
  VERIFY_ARGS=()
  if bool_is_true "verification.skipDashboardVerifier"; then
    VERIFY_ARGS+=(--skip-dashboard)
  fi
  log "Running baseline verifier with args: ${VERIFY_ARGS[*]:-(none)}"
  bash "$BASELINE_VERIFY" "${VERIFY_ARGS[@]}"
else
  log "Skipping baseline verifier by config."
fi

if bool_is_true "verification.runOptionalModelVerifier"; then
  if [[ -x "$OPTIONAL_VERIFY" ]]; then
    log "Running optional model verifier"
    bash "$OPTIONAL_VERIFY"
  else
    die "Optional verifier requested but not executable: $OPTIONAL_VERIFY"
  fi
else
  log "Skipping optional model verifier by config."
fi

if bool_is_true "discord.configure"; then
  OWNER_ID="$(json_get "discord.ownerId")"
  [[ -n "$OWNER_ID" ]] || die "discord.configure=true but discord.ownerId is empty."

  DISCORD_ARGS=(--owner-id "$OWNER_ID")
  if bool_is_true "discord.refreshToken"; then
    DISCORD_ARGS+=(--refresh-token)
  fi
  if bool_is_true "discord.skipPluginInstall"; then
    DISCORD_ARGS+=(--skip-plugin-install)
  fi

  log "Running Discord configure. Token may be requested interactively."
  bash "$DISCORD_CONFIG" "${DISCORD_ARGS[@]}"

  if bool_is_true "discord.runVerifier"; then
    log "Running Discord verifier"
    bash "$DISCORD_VERIFY" --owner-id "$OWNER_ID"
  else
    log "Skipping Discord verifier by config."
  fi
else
  log "Skipping Discord configure by config."
fi

log "Config-driven runner complete"
echo "Runner log: $RUN_LOG"

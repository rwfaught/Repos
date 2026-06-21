#!/usr/bin/env bash
# verify_openclaw_discord_v1.sh

set -Eeuo pipefail

SCRIPT_NAME="$(basename "$0")"
STAMP="$(date +%Y%m%d_%H%M%S)"
LOG_ROOT="${HOME}/openclaw_discord_addon_logs"
LOG_DIR="${LOG_ROOT}/verify_${STAMP}"
LOG_FILE="${LOG_DIR}/verify.log"
REPORT_FILE="${LOG_DIR}/REPORT.md"
RED_DIR="${LOG_DIR}/redacted"

mkdir -p "$LOG_DIR" "$RED_DIR"
exec > >(tee -a "$LOG_FILE") 2>&1

OWNER_ID=""
TOKEN_ENV="DISCORD_BOT_TOKEN"
SKIP_MANUAL_MESSAGE=0

log() { printf '\n[%s] %s\n' "$SCRIPT_NAME" "$*"; }
warn() { printf '\n[%s] WARNING: %s\n' "$SCRIPT_NAME" "$*" >&2; }
die() {
  printf '\n[%s] ERROR: %s\n' "$SCRIPT_NAME" "$*" >&2
  printf '[%s] Log preserved at: %s\n' "$SCRIPT_NAME" "$LOG_FILE" >&2
  exit 1
}

usage() {
  cat <<'EOF'
Usage:
  bash verify_openclaw_discord_addon_v3.sh --owner-id <DISCORD_USER_ID> [options]

Options:
  --owner-id ID           Required. Expected Discord command owner ID.
  --token-env NAME        Env var holding bot token. Default: DISCORD_BOT_TOKEN.
  --skip-manual-message   Skip manual DM/guild message test prompt.
  --help                  Show help.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --owner-id) OWNER_ID="${2:-}"; shift 2 ;;
    --token-env) TOKEN_ENV="${2:-}"; shift 2 ;;
    --skip-manual-message) SKIP_MANUAL_MESSAGE=1; shift ;;
    --help|-h) usage; exit 0 ;;
    *) die "Unknown option: $1" ;;
  esac
done

[[ -n "$OWNER_ID" ]] || { usage; die "--owner-id is required"; }

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

require_cmd() { command -v "$1" >/dev/null 2>&1 || die "Required command not found: $1"; }

log "Starting Discord verification v1"
log "Log file: $LOG_FILE"

require_cmd openclaw
require_cmd systemctl
require_cmd journalctl
require_cmd python3

PROBE_SINCE="$(date '+%Y-%m-%d %H:%M:%S')"
log "Using fresh probe boundary for log assertions: $PROBE_SINCE"

run_capture "OpenClaw Ollama model list" "$LOG_DIR/openclaw_models_ollama.txt" openclaw models list --provider ollama
run_capture "OpenClaw default model config" "$LOG_DIR/openclaw_agents_defaults_model.json" openclaw config get agents.defaults.model --json
run_capture "OpenClaw Discord config" "$LOG_DIR/openclaw_channels_discord.json" openclaw config get channels.discord --json
run_capture "OpenClaw command owner" "$LOG_DIR/openclaw_commands_ownerAllowFrom.json" openclaw config get commands.ownerAllowFrom --json
run_shell_capture "systemd user environment redacted" "$LOG_DIR/systemd_user_environment.txt" \
  "systemctl --user show-environment | grep -E 'OLLAMA|OPENCLAW|DISCORD|CUDA' | sed -E 's/^([^=]*(TOKEN|SECRET|PASSWORD|KEY)[^=]*)=.*/\\1=<REDACTED>/I' || true"
run_capture "OpenClaw gateway status" "$LOG_DIR/openclaw_gateway_status.txt" systemctl --user status openclaw-gateway.service --no-pager
run_shell_capture "OpenClaw channel status probe" "$LOG_DIR/openclaw_channels_status_probe.txt" "openclaw channels status --probe || true"
run_shell_capture "OpenClaw gateway journal since fresh probe" "$LOG_DIR/openclaw_gateway_journal.txt" \
  "journalctl --user -u openclaw-gateway.service --since '$PROBE_SINCE' --no-pager | grep -iE 'discord|gateway|plugin|ready|error|warn|owner|token|pair|channel|unknown|fail|login|connected|intent|unauthorized' || true"

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

log "Assertions"
if grep -qiE '401: Unauthorized|401\):|gateway websocket closed: 4004|Fatal gateway close code: 4004' "$LOG_DIR/openclaw_channels_status_probe.txt" "$LOG_DIR/openclaw_gateway_journal.txt" 2>/dev/null; then
  die "Discord token is unauthorized/invalid. Reset the bot token in Discord Developer Portal, then rerun configure_openclaw_discord_v1.sh --owner-id $OWNER_ID --refresh-token."
fi
grep -q 'ollama/qwen3.5:9b-4k' "$LOG_DIR/openclaw_models_ollama.txt" || die "Bounded base model qwen3.5:9b-4k missing."
grep -qiE '\b4k\b|4096' "$LOG_DIR/openclaw_models_ollama.txt" || die "OpenClaw model list does not show 4k context."
grep -q 'OLLAMA_API_KEY=<REDACTED>' "$LOG_DIR/systemd_user_environment.txt" || die "OLLAMA_API_KEY missing from systemd user environment."
grep -q "${TOKEN_ENV}=<REDACTED>" "$LOG_DIR/systemd_user_environment.txt" || die "$TOKEN_ENV missing from systemd user environment."
grep -q "discord:${OWNER_ID}" "$LOG_DIR/openclaw_commands_ownerAllowFrom.json" || die "commands.ownerAllowFrom does not include discord:${OWNER_ID}."
grep -q '"enabled": true' "$LOG_DIR/openclaw_channels_discord.json" || die "channels.discord.enabled is not true."
systemctl --user is-active --quiet openclaw-gateway.service || die "OpenClaw gateway is not active."
if grep -qi 'plugin not installed: discord' "$LOG_DIR/openclaw_gateway_journal.txt"; then
  die "Gateway still reports Discord plugin not installed."
fi
python3 - <<'PY'
import json, os, sys
p=os.path.expanduser("~/.openclaw/openclaw.json")
cfg=json.load(open(p))
allow=cfg.get("plugins", {}).get("allow")
approved={"discord", "ollama"}
if not isinstance(allow, list) or "discord" not in allow:
    print(f"plugins.allow must be a list including 'discord'; got {allow!r}", file=sys.stderr)
    sys.exit(1)
unknown=[x for x in allow if x not in approved]
if unknown:
    print(f"plugins.allow contains unapproved entries {unknown!r}; full allowlist={allow!r}", file=sys.stderr)
    sys.exit(1)
print(f"plugins.allow approved: {allow!r}")
PY
grep -qi 'Discord default: enabled, configured, running, connected' "$LOG_DIR/openclaw_channels_status_probe.txt" || {
  echo "Discord channel status probe did not report connected/running." >&2
  exit 1
}
if grep -qi 'plugins.allow is empty' "$LOG_DIR/openclaw_gateway_journal.txt"; then
  die "Gateway still reports plugins.allow is empty in fresh post-probe logs."
fi

if [[ "$SKIP_MANUAL_MESSAGE" != "1" ]]; then
  SINCE="$(date '+%Y-%m-%d %H:%M:%S')"
  cat <<EOF

Manual Discord delivery test:

1. In Discord, DM the bot or use the target guild/channel.
2. Send:

   Reply with OK only.

3. Wait for a bot response or pairing code.
4. Return here and press ENTER.

EOF
  read -r -p "Press ENTER after the Discord message test..." _

  run_shell_capture "Gateway logs since manual Discord test" "$LOG_DIR/openclaw_gateway_logs_since_manual_discord.txt" \
    "journalctl --user -u openclaw-gateway.service --since '$SINCE' --no-pager | grep -iE 'discord|gateway|ready|error|warn|owner|token|pair|channel|unknown|fail|model_call|ollama|login|connected|intent|unauthorized' || true"
  run_capture "Ollama ps after manual Discord test" "$LOG_DIR/ollama_ps_after_manual_discord.txt" ollama ps
  if grep -qiE 'unknown model|OLLAMA_API_KEY|All models failed|FailoverError' "$LOG_DIR/openclaw_gateway_logs_since_manual_discord.txt"; then
    die "Fresh gateway logs show provider/model failure during Discord manual test."
  fi
  MANUAL_RESULT="completed"
else
  MANUAL_RESULT="skipped"
fi

log "Writing report"
{
  echo "# OpenClaw Discord Verification Report v1"
  echo
  echo "Created: $(date -Iseconds)"
  echo "Owner expected: discord:$OWNER_ID"
  echo "Token env var: $TOKEN_ENV"
  echo "Log directory: $LOG_DIR"
  echo "Gateway log boundary: $PROBE_SINCE"
  echo
  echo "## Result"
  echo
  echo "- Base bounded model surface: PASS"
  echo "- Discord token env present: PASS"
  echo "- Owner allowlist present: PASS"
  echo "- channels.discord.enabled: PASS"
  echo "- Gateway active: PASS"
  echo "- Manual Discord message test: $MANUAL_RESULT"
} | tee "$REPORT_FILE"

ARCHIVE="$HOME/openclaw_discord_verify_v1_${STAMP}.tar.gz"
tar -czf "$ARCHIVE" -C "$LOG_ROOT" "verify_${STAMP}"

EXPORT_DIR=""
for d in "/mnt/c/Users/${WINUSER:-}" /mnt/c/Users/accou /mnt/c/Users/*; do
  [[ -n "$d" && -d "$d/Downloads" && -w "$d/Downloads" ]] || continue
  case "$d" in *"Default User"*|*"All Users"*|*"Public"*) continue ;; esac
  EXPORT_DIR="$d/Downloads"
  break
done
if [[ -n "$EXPORT_DIR" ]]; then
  cp "$ARCHIVE" "$EXPORT_DIR/" || true
  log "Verification archive copied to: $EXPORT_DIR/$(basename "$ARCHIVE")"
fi

log "Discord verification v1 complete"
cat "$REPORT_FILE"

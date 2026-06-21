#!/usr/bin/env bash
# configure_openclaw_discord_v1.sh
#
# Standalone Discord add-on for an already-working REDO WSL OPENCLAW baseline.
#
# v3 fixes:
#   - installs the official Discord plugin: @openclaw/discord
#   - removes invalid custom properties under channels.discord
#   - uses shell-neutral hidden token input
#   - strengthens token redaction in captured logs
#
# Usage:
#   bash configure_openclaw_discord_addon_v3.sh --owner-id <DISCORD_USER_ID> --token-file <local-secret-path>
#   Omitting --token-file preserves the hidden interactive prompt fallback.

set -Eeuo pipefail

SCRIPT_NAME="$(basename "$0")"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STAMP="$(date +%Y%m%d_%H%M%S)"
LOG_ROOT="${HOME}/openclaw_discord_addon_logs"
LOG_DIR="${LOG_ROOT}/${STAMP}"
LOG_FILE="${LOG_DIR}/configure.log"
REPORT_FILE="${LOG_DIR}/REPORT.md"
RED_DIR="${LOG_DIR}/redacted"

mkdir -p "$LOG_DIR" "$RED_DIR"
exec > >(tee -a "$LOG_FILE") 2>&1

OWNER_ID=""
TOKEN_ENV="DISCORD_BOT_TOKEN"
TOKEN_FILE=""
SKIP_BASELINE_CHECK=0
NO_RESTART=0
REFRESH_TOKEN=0
MARKER_DIR="${WIRE_MARKER_DIR:-}"
DISCORD_TOKEN_SOURCE="unknown"
DISCORD_TOKEN_FILE_CONFIGURED="NO"
DISCORD_TOKEN_FILE_PRESENT="UNKNOWN"
DISCORD_TOKEN_FILE_NON_EMPTY="UNKNOWN"
DISCORD_TOKEN_READ_RESULT="NOT_ATTEMPTED"
DISCORD_TOKEN_VALUE_LOGGED="NO"
DISCORD_RUNTIME_SECRET_HANDLING="local-env-required"
DISCORD_RUNTIME_SECRET_PERSISTENCE="local-user-env-file"
DISCORD_TOKEN_DURABLE_EXPOSURE="NO"
DISCORD_TOKEN_INSTALL_CONFIG_VALUE_STORED="NO"
DISCORD_CONFIG_MODEL_GUARD_RESULT="UNKNOWN"
DISCORD_CONFIG_EXPECTED_PRIMARY_MODEL="UNKNOWN"
DISCORD_CONFIG_MODEL_TIER="UNKNOWN"
DISCORD_CONFIG_FAILURE_REASON="unknown"
DISCORD_EXTERNAL_PLUGIN_INSTALL_REQUIRED="NO"
DISCORD_EXTERNAL_PLUGIN_INSTALL_ATTEMPTED="NO"
DISCORD_EXTERNAL_PLUGIN_INSTALL_RESULT="NOT_REQUIRED"
DISCORD_NATIVE_CHANNEL_ADD_ATTEMPTED="NO"
DISCORD_NATIVE_CHANNEL_ADD_METHODS_TRIED="none"
DISCORD_NATIVE_CHANNEL_ADD_FINAL_METHOD="not-attempted"
DISCORD_NATIVE_CHANNEL_ADD_COMMAND_RESULT="UNKNOWN"
DISCORD_NATIVE_CHANNEL_ADD_STATE_RESULT="UNKNOWN"
DISCORD_NATIVE_CHANNEL_ADD_RESULT="UNKNOWN"
DISCORD_NATIVE_CHANNEL_ADD_FAILURE_REASON="unknown"
DISCORD_SETUP_METHOD="unknown"
DISCORD_SECRETREF_CONFIG_ATTEMPTED="NO"
DISCORD_SECRETREF_CONFIG_RESULT="UNKNOWN"
DISCORD_SECRETREF_CONFIG_FAILURE_REASON="unknown"
DISCORD_ENABLED_CONFIG_RESULT="UNKNOWN"
DISCORD_ACCOUNT_SCOPED_CONFIG_ATTEMPTED="NO"
DISCORD_ACCOUNT_SCOPED_CONFIG_RESULT="UNKNOWN"
DISCORD_ACCOUNT_SCOPED_CONFIG_FAILURE_REASON="unknown"
DISCORD_ACCOUNT_SCOPED_TOKEN_RESULT="UNKNOWN"
DISCORD_ACCOUNT_SCOPED_ENABLED_RESULT="UNKNOWN"
DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_ATTEMPTED="NO"
DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_RESULT="UNKNOWN"
DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_FAILURE_REASON="unknown"
DISCORD_TOP_LEVEL_TOKEN_REMOVED_FOR_ENV_ONLY="NO"
DISCORD_ACCOUNT_SCOPED_TOKEN_REMOVED_FOR_ENV_ONLY="NO"
DISCORD_SCRIPT_ENV_TOKEN_PRESENT="UNKNOWN"
DISCORD_SCRIPT_ENV_TOKEN_LENGTH="UNKNOWN"
DISCORD_SYSTEMD_ENV_TOKEN_PRESENT="UNKNOWN"
DISCORD_SYSTEMD_ENV_TOKEN_LENGTH="UNKNOWN"
DISCORD_GATEWAY_ENV_TOKEN_PRESENT="UNKNOWN"
DISCORD_GATEWAY_ENV_TOKEN_LENGTH="UNKNOWN"
DISCORD_CLI_ENV_INJECTED_FOR_STATUS="NO"
DISCORD_CLI_ENV_INJECTED_ACCOUNTS_JSON_COUNT="UNKNOWN"
DISCORD_CLI_ENV_INJECTED_LINE="UNKNOWN"
DISCORD_INACTIVE_SURFACE_WARNING_SEEN="UNKNOWN"
DISCORD_ACCOUNTS_JSON_COUNT="UNKNOWN"
DISCORD_LOADED_ADAPTER_PROOF_ATTEMPTED="NO"
DISCORD_LOADED_ADAPTER_PROOF_RESULT="UNKNOWN"
DISCORD_LOADED_ADAPTER_PROOF_FAILURE_REASON="unknown"
DISCORD_LOADED_ADAPTER_IDS_ENV_ONLY="UNKNOWN"
DISCORD_LOADED_ADAPTER_DEFAULT_ACCOUNT_ID_ENV_ONLY="UNKNOWN"
DISCORD_LOADED_ADAPTER_CONFIGURED_ENV_ONLY="UNKNOWN"
DISCORD_LOADED_ADAPTER_TOKEN_SOURCE_ENV_ONLY="UNKNOWN"
DISCORD_LOADED_ADAPTER_TOKEN_STATUS_ENV_ONLY="UNKNOWN"
DISCORD_LOADED_ADAPTER_TOKEN_LENGTH_ENV_ONLY="UNKNOWN"
DISCORD_LOADED_ADAPTER_IDS_EXPLICIT_DEFAULT="UNKNOWN"
DISCORD_LOADED_ADAPTER_CONFIGURED_EXPLICIT_DEFAULT="UNKNOWN"
DISCORD_LOADED_ADAPTER_PROOF_GATE_MODE="hard-until-public-env-only-pass"
DISCORD_PUBLIC_STATUS_ACCOUNTS_COUNT="UNKNOWN"
DISCORD_PUBLIC_ENV_ONLY_GATE_RESULT="UNKNOWN"
DISCORD_PUBLIC_ENV_ONLY_GATE_FAILURE_REASON="unknown"
DISCORD_PUBLIC_ENV_ONLY_LINE_RESULT="UNKNOWN"
DISCORD_PUBLIC_ENV_ONLY_LINE="UNKNOWN"
DISCORD_PUBLIC_ENV_ONLY_JSON_RESULT="UNKNOWN"
DISCORD_PUBLIC_ENV_ONLY_JSON_INSTALLED="UNKNOWN"
DISCORD_PUBLIC_ENV_ONLY_JSON_ORIGIN="UNKNOWN"
DISCORD_PUBLIC_ENV_ONLY_JSON_DEFAULT_ACCOUNT="UNKNOWN"
DISCORD_PUBLIC_ENV_ONLY_GATEWAY_REACHABLE="UNKNOWN"
DISCORD_PUBLIC_ENV_ONLY_SYSTEMD_TOKEN_REDACTED="UNKNOWN"
DISCORD_PUBLIC_ENV_ONLY_CONFIG_TOKEN_FIELDS_ABSENT="UNKNOWN"
DISCORD_PUBLIC_ENV_ONLY_CONFIG_TOKEN_FIELD_PATHS="UNKNOWN"
DISCORD_STATUS_LAYER_LAZY_PLUGIN_BUG_SUSPECTED="NO"
DISCORD_FAILURE_CLASS="unknown"
DISCORD_ROLLBACK_DECISION="unknown"
DISCORD_ROLLBACK_REASON="unknown"
DISCORD_ENV_ONLY_CONFIG_PRESERVED="UNKNOWN"
DISCORD_KNOWN_BAD_SECRETREF_RESTORE_SKIPPED="UNKNOWN"
DISCORD_POST_FAILURE_CONFIG_HAS_TOP_LEVEL_TOKEN="UNKNOWN"
DISCORD_POST_FAILURE_CONFIG_SHAPE="unknown"
DISCORD_GATEWAY_PROVIDER_STARTUP_SEEN="UNKNOWN"
DISCORD_GATEWAY_PROVIDER_STARTUP_PATTERN="none"
DISCORD_GATEWAY_GENERIC_READY_ONLY="UNKNOWN"
DISCORD_GATEWAY_PROVIDER_STARTUP_DETECTION_RESULT="UNKNOWN"
DISCORD_GATEWAY_PROVIDER_STARTUP_MATCHED_LINE="UNKNOWN"
DISCORD_GATEWAY_PROVIDER_STARTUP_MATCHED_LINE_SHA256="UNKNOWN"
DISCORD_RUNTIME_MAY_STILL_WORK="UNKNOWN"
DISCORD_CHANNEL_CONFIG_RESULT="UNKNOWN"
DISCORD_CHANNEL_STATE_BEFORE_REPAIR="unknown"
DISCORD_CHANNEL_STATE_AFTER_REPAIR="unknown"
DISCORD_LINE_BEFORE_NATIVE_ADD="UNKNOWN"
DISCORD_LINE_AFTER_USE_ENV="UNKNOWN"
DISCORD_LINE_AFTER_TOKEN_FILE="UNKNOWN"
DISCORD_LINE_AFTER_BOT_TOKEN="UNKNOWN"
DISCORD_LINE_AFTER_NATIVE_ADD="UNKNOWN"
DISCORD_LINE_AFTER_SECRETREF_CONFIG="UNKNOWN"
DISCORD_LINE_AFTER_ACCOUNT_SCOPED_CONFIG="UNKNOWN"
DISCORD_LINE_AFTER_ENV_ONLY_IMPLICIT_DEFAULT="UNKNOWN"
DISCORD_CHANNEL_STATE_PARSER_RESULT="UNKNOWN"
DISCORD_CHANNEL_STATE_LINE="UNKNOWN"
DISCORD_CHANNEL_INSTALLED="unknown"
DISCORD_CHANNEL_CONFIGURED="unknown"
DISCORD_CHANNEL_ENABLED="UNKNOWN"
DISCORD_CHANNEL_ACTIVATION_RESULT="UNKNOWN"
DISCORD_REPAIR_ATTEMPTED="NO"
DISCORD_REPAIR_METHOD="not-required"
DISCORD_REPAIR_RESULT="UNKNOWN"
DISCORD_REPAIR_FAILURE_REASON="unknown"
DISCORD_CONFIG_RESULT="UNKNOWN"
DISCORD_PLUGIN_INSTALLED="UNKNOWN"
DISCORD_ENV_TOKEN_PRESENT="UNKNOWN"
DISCORD_ADAPTER_ENV_CONFIGURED_PLAUSIBLE="UNKNOWN"
DISCORD_PUBLIC_ACCOUNT_RECOGNIZED="UNKNOWN"
DISCORD_PUBLIC_STATUS_CONFIGURED_ENABLED="UNKNOWN"
DISCORD_PROVIDER_STARTUP_OBSERVED="UNKNOWN"
DISCORD_MESSAGE_PROOF_COMPLETED="NOT_RUN"
DISCORD_VERIFIER_ALLOWED="NO"
DISCORD_PUBLIC_ACCOUNT_RECOGNITION_SOURCE="openclaw-public-channels-list-json-plugin.config.listAccountIds(cfg)"
OPENCLAW_READONLY_EXTERNAL_PLUGINS_PATCH_RESULT="UNKNOWN"
OPENCLAW_READONLY_EXTERNAL_PLUGINS_PATCH_PROOF="UNKNOWN"
DISCORD_PLUGIN_ENTRY_GATE_ATTEMPTED="NO"
DISCORD_PLUGIN_ENTRY_GATE_RESULT="UNKNOWN"
DISCORD_PLUGIN_ENTRY_GATE_FAILURE_REASON="unknown"
DISCORD_PLUGIN_ENTRY_KEYS="UNKNOWN"
DISCORD_PLUGIN_ENTRY_DISCORD_PRESENT="UNKNOWN"
DISCORD_PLUGIN_ENTRY_DISCORD_ENABLED="UNKNOWN"
DISCORD_PLUGIN_ENTRY_CONFIG_VALIDATE_RESULT="UNKNOWN"
DISCORD_DEEP_STATUS_GATE_RESULT="UNKNOWN"
DISCORD_DEEP_STATUS_GATE_FAILURE_REASON="unknown"
DISCORD_DEEP_STATUS_HAS_DISCORD="UNKNOWN"
DISCORD_DEEP_STATUS_NO_CHANNELS_CONFIGURED="UNKNOWN"

log() { printf '\n[%s] %s\n' "$SCRIPT_NAME" "$*"; }
warn() { printf '\n[%s] WARNING: %s\n' "$SCRIPT_NAME" "$*" >&2; }
die() {
  DISCORD_CONFIG_RESULT="FAIL"
  write_discord_channel_markers || true
  printf '\n[%s] ERROR: %s\n' "$SCRIPT_NAME" "$*" >&2
  printf '[%s] Log preserved at: %s\n' "$SCRIPT_NAME" "$LOG_FILE" >&2
  exit 1
}

usage() {
  cat <<'EOF'
Usage:
  bash configure_openclaw_discord_addon_v3.sh --owner-id <DISCORD_USER_ID> [options]

Options:
  --owner-id ID             Required. Discord user ID allowed to run owner commands.
  --token-env NAME          Env var holding bot token. Default: DISCORD_BOT_TOKEN.
  --token-file PATH         Read Discord bot token from local file by reference.
  --skip-baseline-check     Skip base OpenClaw/Ollama sanity guard.
  --refresh-token           Force hidden prompt for a new Discord bot token.
  --no-restart              Write config but do not restart gateway.
  --help                    Show this help.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --owner-id) OWNER_ID="${2:-}"; shift 2 ;;
    --token-env) TOKEN_ENV="${2:-}"; shift 2 ;;
    --token-file) TOKEN_FILE="${2:-}"; shift 2 ;;
    --skip-baseline-check) SKIP_BASELINE_CHECK=1; shift ;;
    --refresh-token) REFRESH_TOKEN=1; shift ;;
    --no-restart) NO_RESTART=1; shift ;;
    --help|-h) usage; exit 0 ;;
    *) die "Unknown option: $1" ;;
  esac
done

[[ -n "$OWNER_ID" ]] || { usage; die "--owner-id is required"; }
[[ "$OWNER_ID" =~ ^[0-9]+$ ]] || die "--owner-id should be a numeric Discord user ID"

on_error() {
  local rc=$?
  log "FAILED with exit code $rc"
  log "Log preserved at: $LOG_FILE"
  exit "$rc"
}
trap on_error ERR

require_cmd() { command -v "$1" >/dev/null 2>&1 || die "Required command not found: $1"; }

redact_env_command='sed -E "s/^([^=]*(TOKEN|SECRET|PASSWORD|KEY)[^=]*)=.*/\1=<REDACTED>/I"'

prompt_secret() {
  local prompt="$1"
  local var_name="$2"
  local value=""
  local tty_dev="/dev/tty"

  [[ -r "$tty_dev" && -w "$tty_dev" ]] || die "Interactive terminal required for secret input."

  printf "%s" "$prompt" >"$tty_dev"
  stty -echo <"$tty_dev"
  IFS= read -r value <"$tty_dev"
  stty echo <"$tty_dev"
  printf "\n" >"$tty_dev"

  printf -v "$var_name" "%s" "$value"
}

load_secret_from_file() {
  local path="$1"
  [[ -n "$path" ]] || return 1
  DISCORD_TOKEN_FILE_CONFIGURED="YES"
  if [[ ! -f "$path" ]]; then
    DISCORD_TOKEN_FILE_PRESENT="NO"
    DISCORD_TOKEN_FILE_NON_EMPTY="NO"
    DISCORD_TOKEN_READ_RESULT="FAIL"
    return 1
  fi
  DISCORD_TOKEN_FILE_PRESENT="YES"
  local value=""
  value="$(python3 - "$path" <<'PY'
from pathlib import Path
import sys
print(Path(sys.argv[1]).read_text(encoding="utf-8").strip(), end="")
PY
)"
  if [[ -z "$value" ]]; then
    DISCORD_TOKEN_FILE_NON_EMPTY="NO"
    DISCORD_TOKEN_READ_RESULT="FAIL"
    return 1
  fi
  DISCORD_TOKEN_FILE_NON_EMPTY="YES"
  DISCORD_TOKEN_READ_RESULT="PASS"
  printf '%s' "$value"
}

load_existing_secret() {
  local env_name="$1"
  local value=""

  # Prefer the current shell env.
  value="${!env_name:-}"
  if [[ -n "$value" ]]; then
    printf "%s" "$value"
    return 0
  fi

  # Then systemd user environment.
  value="$(systemctl --user show-environment 2>/dev/null | sed -n "s/^${env_name}=//p" | head -n 1 || true)"
  if [[ -n "$value" ]]; then
    printf "%s" "$value"
    return 0
  fi

  # Then the persisted OpenClaw env file.
  if [[ -f "$HOME/.openclaw/.env" ]]; then
    value="$(sed -n "s/^${env_name}=//p" "$HOME/.openclaw/.env" | tail -n 1 || true)"
    if [[ -n "$value" ]]; then
      printf "%s" "$value"
      return 0
    fi
  fi

  return 1
}

redact_file() {
  local src="$1"
  local dst="$2"
  if [[ -f "$src" ]]; then
    sed -E 's/^([^=]*(TOKEN|SECRET|PASSWORD|KEY)[^=]*)=.*/\1=<REDACTED>/I' "$src" > "$dst" || true
  fi
}

capture_script_systemd_discord_env_proof() {
  local outfile="$LOG_DIR/discord_env_token_proof.script_systemd.txt"
  local script_value="${!TOKEN_ENV:-}"
  local systemd_value

  systemd_value="$(systemctl --user show-environment 2>/dev/null | sed -n "s/^${TOKEN_ENV}=//p" | head -n 1 || true)"

  if [[ -n "$script_value" ]]; then
    DISCORD_SCRIPT_ENV_TOKEN_PRESENT="YES"
    DISCORD_SCRIPT_ENV_TOKEN_LENGTH="NOT_REPORTED"
  else
    DISCORD_SCRIPT_ENV_TOKEN_PRESENT="NO"
    DISCORD_SCRIPT_ENV_TOKEN_LENGTH="UNKNOWN"
  fi

  if [[ -n "$systemd_value" ]]; then
    DISCORD_SYSTEMD_ENV_TOKEN_PRESENT="YES"
    DISCORD_SYSTEMD_ENV_TOKEN_LENGTH="NOT_REPORTED"
  else
    DISCORD_SYSTEMD_ENV_TOKEN_PRESENT="NO"
    DISCORD_SYSTEMD_ENV_TOKEN_LENGTH="UNKNOWN"
  fi

  {
    echo "${TOKEN_ENV}=<REDACTED>"
    echo "scriptPresent=${DISCORD_SCRIPT_ENV_TOKEN_PRESENT}"
    echo "scriptLength=${DISCORD_SCRIPT_ENV_TOKEN_LENGTH}"
    echo "systemdPresent=${DISCORD_SYSTEMD_ENV_TOKEN_PRESENT}"
    echo "systemdLength=${DISCORD_SYSTEMD_ENV_TOKEN_LENGTH}"
  } | tee "$outfile"
}

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

run_openclaw_with_discord_env() {
  local label="$1"
  local outfile="$2"
  shift 2
  DISCORD_CLI_ENV_INJECTED_FOR_STATUS="YES"
  log "$label"
  {
    echo "## $label"
    echo "## Started: $(date -Iseconds)"
    echo "## Command: ${TOKEN_ENV}=<REDACTED> openclaw $*"
    echo
    env "${TOKEN_ENV}=${TOKEN_VALUE}" openclaw "$@"
    rc=$?
    echo
    echo "## Exit code: $rc"
    echo "## Finished: $(date -Iseconds)"
    return "$rc"
  } | tee "$outfile"
}

apply_openclaw_readonly_external_plugins_patch() {
  local helper="$SCRIPT_DIR/patch_openclaw_readonly_external_plugins_v1_7.sh"
  local outfile="$LOG_DIR/openclaw_readonly_external_plugins_patch.txt"
  if [[ ! -f "$helper" ]]; then
    OPENCLAW_READONLY_EXTERNAL_PLUGINS_PATCH_RESULT="missing-helper"
    die "Missing OpenClaw read-only external plugins compatibility helper: $helper"
  fi
  chmod +x "$helper" || true
  log "Applying OpenClaw read-only external channel plugin compatibility patch"
  if bash "$helper" --log-dir "$LOG_DIR" > "$outfile" 2>&1; then
    cat "$outfile"
    OPENCLAW_READONLY_EXTERNAL_PLUGINS_PATCH_RESULT="$(sed -n 's/^PATCH_RESULT=//p' "$outfile" | head -n 1)"
    OPENCLAW_READONLY_EXTERNAL_PLUGINS_PATCH_PROOF="$(sed -n 's/^FIX_v1_7_62_LIVE_PATCH_PROOF=//p' "$outfile" | head -n 1)"
    [[ -n "$OPENCLAW_READONLY_EXTERNAL_PLUGINS_PATCH_RESULT" ]] || OPENCLAW_READONLY_EXTERNAL_PLUGINS_PATCH_RESULT="unknown"
    [[ -n "$OPENCLAW_READONLY_EXTERNAL_PLUGINS_PATCH_PROOF" ]] || OPENCLAW_READONLY_EXTERNAL_PLUGINS_PATCH_PROOF="FAIL"
  else
    cat "$outfile" || true
    OPENCLAW_READONLY_EXTERNAL_PLUGINS_PATCH_RESULT="$(sed -n 's/^PATCH_RESULT=//p' "$outfile" 2>/dev/null | head -n 1)"
    [[ -n "$OPENCLAW_READONLY_EXTERNAL_PLUGINS_PATCH_RESULT" ]] || OPENCLAW_READONLY_EXTERNAL_PLUGINS_PATCH_RESULT="failed"
    die "OpenClaw read-only external channel plugin compatibility patch failed."
  fi
  if [[ "$OPENCLAW_READONLY_EXTERNAL_PLUGINS_PATCH_PROOF" != "PASS" ]]; then
    die "OpenClaw read-only external channel plugin compatibility patch proof failed."
  fi
}

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

write_discord_config_guard_markers() {
  write_marker "discordConfigModelGuardResult" "$DISCORD_CONFIG_MODEL_GUARD_RESULT"
  write_marker "discordConfigExpectedPrimaryModel" "$DISCORD_CONFIG_EXPECTED_PRIMARY_MODEL"
  write_marker "discordConfigModelTier" "$DISCORD_CONFIG_MODEL_TIER"
  write_marker "discordConfigFailureReason" "$DISCORD_CONFIG_FAILURE_REASON"
}

first_known_discord_account_count() {
  local candidate
  for candidate in "$DISCORD_PUBLIC_STATUS_ACCOUNTS_COUNT" "$DISCORD_ACCOUNTS_JSON_COUNT" "$DISCORD_CLI_ENV_INJECTED_ACCOUNTS_JSON_COUNT"; do
    if [[ "$candidate" =~ ^[0-9]+$ ]]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  printf 'UNKNOWN\n'
}

derive_discord_state_taxonomy() {
  local account_count

  case "$DISCORD_CHANNEL_INSTALLED" in
    installed) DISCORD_PLUGIN_INSTALLED="YES" ;;
    not-installed) DISCORD_PLUGIN_INSTALLED="NO" ;;
    *)
      case "$DISCORD_EXTERNAL_PLUGIN_INSTALL_RESULT" in
        PASS|NOT_REQUIRED) DISCORD_PLUGIN_INSTALLED="YES" ;;
        FAIL) DISCORD_PLUGIN_INSTALLED="NO" ;;
        *) DISCORD_PLUGIN_INSTALLED="UNKNOWN" ;;
      esac
      ;;
  esac

  if [[ "$DISCORD_SCRIPT_ENV_TOKEN_PRESENT" == "YES" || "$DISCORD_SYSTEMD_ENV_TOKEN_PRESENT" == "YES" || "$DISCORD_GATEWAY_ENV_TOKEN_PRESENT" == "YES" ]]; then
    DISCORD_ENV_TOKEN_PRESENT="YES"
  elif [[ "$DISCORD_SCRIPT_ENV_TOKEN_PRESENT" == "NO" && "$DISCORD_SYSTEMD_ENV_TOKEN_PRESENT" == "NO" && "$DISCORD_GATEWAY_ENV_TOKEN_PRESENT" == "NO" ]]; then
    DISCORD_ENV_TOKEN_PRESENT="NO"
  else
    DISCORD_ENV_TOKEN_PRESENT="UNKNOWN"
  fi

  if [[ "$DISCORD_LOADED_ADAPTER_PROOF_RESULT" == "PASS" && \
        "$DISCORD_LOADED_ADAPTER_CONFIGURED_ENV_ONLY" == "YES" && \
        "$DISCORD_LOADED_ADAPTER_TOKEN_SOURCE_ENV_ONLY" == "env" && \
        "$DISCORD_LOADED_ADAPTER_TOKEN_STATUS_ENV_ONLY" == "available" ]]; then
    DISCORD_ADAPTER_ENV_CONFIGURED_PLAUSIBLE="YES"
  elif [[ "$DISCORD_LOADED_ADAPTER_PROOF_ATTEMPTED" == "YES" ]]; then
    DISCORD_ADAPTER_ENV_CONFIGURED_PLAUSIBLE="NO"
  else
    DISCORD_ADAPTER_ENV_CONFIGURED_PLAUSIBLE="UNKNOWN"
  fi

  account_count="$(first_known_discord_account_count)"
  if [[ "$account_count" =~ ^[0-9]+$ && "$account_count" -gt 0 ]]; then
    DISCORD_PUBLIC_ACCOUNT_RECOGNIZED="YES"
  elif [[ "$account_count" == "0" ]]; then
    DISCORD_PUBLIC_ACCOUNT_RECOGNIZED="NO"
  else
    DISCORD_PUBLIC_ACCOUNT_RECOGNIZED="UNKNOWN"
  fi

  if discord_state_is_authoritative_pass "${DISCORD_CHANNEL_INSTALLED}|${DISCORD_CHANNEL_CONFIGURED}|${DISCORD_CHANNEL_ENABLED}"; then
    DISCORD_PUBLIC_STATUS_CONFIGURED_ENABLED="YES"
    DISCORD_VERIFIER_ALLOWED="YES"
  else
    DISCORD_VERIFIER_ALLOWED="NO"
    if [[ "$DISCORD_CHANNEL_INSTALLED" == "unknown" || "$DISCORD_CHANNEL_CONFIGURED" == "unknown" || "$DISCORD_CHANNEL_ENABLED" == "UNKNOWN" || "$DISCORD_CHANNEL_ENABLED" == "unknown" ]]; then
      DISCORD_PUBLIC_STATUS_CONFIGURED_ENABLED="UNKNOWN"
    else
      DISCORD_PUBLIC_STATUS_CONFIGURED_ENABLED="NO"
    fi
  fi

  case "$DISCORD_GATEWAY_PROVIDER_STARTUP_SEEN" in
    YES) DISCORD_PROVIDER_STARTUP_OBSERVED="YES" ;;
    NO) DISCORD_PROVIDER_STARTUP_OBSERVED="NO" ;;
    *) DISCORD_PROVIDER_STARTUP_OBSERVED="UNKNOWN" ;;
  esac
}

write_discord_channel_markers() {
  derive_discord_state_taxonomy

  write_marker "discordExternalPluginInstallRequired" "$DISCORD_EXTERNAL_PLUGIN_INSTALL_REQUIRED"
  write_marker "discordTokenSource" "$DISCORD_TOKEN_SOURCE"
  write_marker "discordTokenFileConfigured" "$DISCORD_TOKEN_FILE_CONFIGURED"
  write_marker "discordTokenFilePresent" "$DISCORD_TOKEN_FILE_PRESENT"
  write_marker "discordTokenFileNonEmpty" "$DISCORD_TOKEN_FILE_NON_EMPTY"
  write_marker "discordTokenReadResult" "$DISCORD_TOKEN_READ_RESULT"
  write_marker "discordTokenValueLogged" "$DISCORD_TOKEN_VALUE_LOGGED"
  write_marker "discordRuntimeSecretHandling" "$DISCORD_RUNTIME_SECRET_HANDLING"
  write_marker "discordRuntimeSecretPersistence" "$DISCORD_RUNTIME_SECRET_PERSISTENCE"
  write_marker "discordTokenDurableExposure" "$DISCORD_TOKEN_DURABLE_EXPOSURE"
  write_marker "discordTokenInstallConfigValueStored" "$DISCORD_TOKEN_INSTALL_CONFIG_VALUE_STORED"
  write_marker "discordExternalPluginInstallAttempted" "$DISCORD_EXTERNAL_PLUGIN_INSTALL_ATTEMPTED"
  write_marker "discordExternalPluginInstallResult" "$DISCORD_EXTERNAL_PLUGIN_INSTALL_RESULT"
  write_marker "openclawReadonlyExternalPluginsPatchResult" "$OPENCLAW_READONLY_EXTERNAL_PLUGINS_PATCH_RESULT"
  write_marker "openclawReadonlyExternalPluginsPatchProof" "$OPENCLAW_READONLY_EXTERNAL_PLUGINS_PATCH_PROOF"
  write_marker "discordNativeChannelAddAttempted" "$DISCORD_NATIVE_CHANNEL_ADD_ATTEMPTED"
  write_marker "discordNativeChannelAddMethodsTried" "$DISCORD_NATIVE_CHANNEL_ADD_METHODS_TRIED"
  write_marker "discordNativeChannelAddFinalMethod" "$DISCORD_NATIVE_CHANNEL_ADD_FINAL_METHOD"
  write_marker "discordNativeChannelAddCommandResult" "$DISCORD_NATIVE_CHANNEL_ADD_COMMAND_RESULT"
  write_marker "discordNativeChannelAddStateResult" "$DISCORD_NATIVE_CHANNEL_ADD_STATE_RESULT"
  write_marker "discordNativeChannelAddResult" "$DISCORD_NATIVE_CHANNEL_ADD_RESULT"
  write_marker "discordNativeChannelAddFailureReason" "$DISCORD_NATIVE_CHANNEL_ADD_FAILURE_REASON"
  write_marker "discordSetupMethod" "$DISCORD_SETUP_METHOD"
  write_marker "discordSecretRefConfigAttempted" "$DISCORD_SECRETREF_CONFIG_ATTEMPTED"
  write_marker "discordSecretRefConfigResult" "$DISCORD_SECRETREF_CONFIG_RESULT"
  write_marker "discordSecretRefConfigFailureReason" "$DISCORD_SECRETREF_CONFIG_FAILURE_REASON"
  write_marker "discordEnabledConfigResult" "$DISCORD_ENABLED_CONFIG_RESULT"
  write_marker "discordAccountScopedConfigAttempted" "$DISCORD_ACCOUNT_SCOPED_CONFIG_ATTEMPTED"
  write_marker "discordAccountScopedConfigResult" "$DISCORD_ACCOUNT_SCOPED_CONFIG_RESULT"
  write_marker "discordAccountScopedConfigFailureReason" "$DISCORD_ACCOUNT_SCOPED_CONFIG_FAILURE_REASON"
  write_marker "discordAccountScopedTokenResult" "$DISCORD_ACCOUNT_SCOPED_TOKEN_RESULT"
  write_marker "discordAccountScopedEnabledResult" "$DISCORD_ACCOUNT_SCOPED_ENABLED_RESULT"
  write_marker "discordEnvOnlyImplicitDefaultAttempted" "$DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_ATTEMPTED"
  write_marker "discordEnvOnlyImplicitDefaultResult" "$DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_RESULT"
  write_marker "discordEnvOnlyImplicitDefaultFailureReason" "$DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_FAILURE_REASON"
  write_marker "discordPluginEntryGateAttempted" "$DISCORD_PLUGIN_ENTRY_GATE_ATTEMPTED"
  write_marker "discordPluginEntryGateResult" "$DISCORD_PLUGIN_ENTRY_GATE_RESULT"
  write_marker "discordPluginEntryGateFailureReason" "$DISCORD_PLUGIN_ENTRY_GATE_FAILURE_REASON"
  write_marker "discordPluginEntryKeys" "$DISCORD_PLUGIN_ENTRY_KEYS"
  write_marker "discordPluginEntryDiscordPresent" "$DISCORD_PLUGIN_ENTRY_DISCORD_PRESENT"
  write_marker "discordPluginEntryDiscordEnabled" "$DISCORD_PLUGIN_ENTRY_DISCORD_ENABLED"
  write_marker "discordPluginEntryConfigValidateResult" "$DISCORD_PLUGIN_ENTRY_CONFIG_VALIDATE_RESULT"
  write_marker "discordDeepStatusGateResult" "$DISCORD_DEEP_STATUS_GATE_RESULT"
  write_marker "discordDeepStatusGateFailureReason" "$DISCORD_DEEP_STATUS_GATE_FAILURE_REASON"
  write_marker "discordDeepStatusHasDiscord" "$DISCORD_DEEP_STATUS_HAS_DISCORD"
  write_marker "discordDeepStatusNoChannelsConfigured" "$DISCORD_DEEP_STATUS_NO_CHANNELS_CONFIGURED"
  write_marker "discordTopLevelTokenRemovedForEnvOnly" "$DISCORD_TOP_LEVEL_TOKEN_REMOVED_FOR_ENV_ONLY"
  write_marker "discordAccountScopedTokenRemovedForEnvOnly" "$DISCORD_ACCOUNT_SCOPED_TOKEN_REMOVED_FOR_ENV_ONLY"
  write_marker "discordScriptEnvTokenPresent" "$DISCORD_SCRIPT_ENV_TOKEN_PRESENT"
  write_marker "discordScriptEnvTokenLength" "$DISCORD_SCRIPT_ENV_TOKEN_LENGTH"
  write_marker "discordSystemdEnvTokenPresent" "$DISCORD_SYSTEMD_ENV_TOKEN_PRESENT"
  write_marker "discordSystemdEnvTokenLength" "$DISCORD_SYSTEMD_ENV_TOKEN_LENGTH"
  write_marker "discordGatewayEnvTokenPresent" "$DISCORD_GATEWAY_ENV_TOKEN_PRESENT"
  write_marker "discordGatewayEnvTokenLength" "$DISCORD_GATEWAY_ENV_TOKEN_LENGTH"
  write_marker "discordCliEnvInjectedForStatus" "$DISCORD_CLI_ENV_INJECTED_FOR_STATUS"
  write_marker "discordCliEnvInjectedAccountsJsonCount" "$DISCORD_CLI_ENV_INJECTED_ACCOUNTS_JSON_COUNT"
  write_marker "discordCliEnvInjectedLine" "$DISCORD_CLI_ENV_INJECTED_LINE"
  write_marker "discordInactiveSurfaceWarningSeen" "$DISCORD_INACTIVE_SURFACE_WARNING_SEEN"
  write_marker "discordAccountsJsonCount" "$DISCORD_ACCOUNTS_JSON_COUNT"
  write_marker "discordLoadedAdapterProofAttempted" "$DISCORD_LOADED_ADAPTER_PROOF_ATTEMPTED"
  write_marker "discordLoadedAdapterProofResult" "$DISCORD_LOADED_ADAPTER_PROOF_RESULT"
  write_marker "discordLoadedAdapterProofFailureReason" "$DISCORD_LOADED_ADAPTER_PROOF_FAILURE_REASON"
  write_marker "discordLoadedAdapterIdsEnvOnly" "$DISCORD_LOADED_ADAPTER_IDS_ENV_ONLY"
  write_marker "discordLoadedAdapterDefaultAccountIdEnvOnly" "$DISCORD_LOADED_ADAPTER_DEFAULT_ACCOUNT_ID_ENV_ONLY"
  write_marker "discordLoadedAdapterConfiguredEnvOnly" "$DISCORD_LOADED_ADAPTER_CONFIGURED_ENV_ONLY"
  write_marker "discordLoadedAdapterTokenSourceEnvOnly" "$DISCORD_LOADED_ADAPTER_TOKEN_SOURCE_ENV_ONLY"
  write_marker "discordLoadedAdapterTokenStatusEnvOnly" "$DISCORD_LOADED_ADAPTER_TOKEN_STATUS_ENV_ONLY"
  write_marker "discordLoadedAdapterTokenLengthEnvOnly" "$DISCORD_LOADED_ADAPTER_TOKEN_LENGTH_ENV_ONLY"
  write_marker "discordLoadedAdapterIdsExplicitDefault" "$DISCORD_LOADED_ADAPTER_IDS_EXPLICIT_DEFAULT"
  write_marker "discordLoadedAdapterConfiguredExplicitDefault" "$DISCORD_LOADED_ADAPTER_CONFIGURED_EXPLICIT_DEFAULT"
  write_marker "discordLoadedAdapterProofGateMode" "$DISCORD_LOADED_ADAPTER_PROOF_GATE_MODE"
  write_marker "discordPublicStatusAccountsCount" "$DISCORD_PUBLIC_STATUS_ACCOUNTS_COUNT"
  write_marker "discordPublicEnvOnlyGateResult" "$DISCORD_PUBLIC_ENV_ONLY_GATE_RESULT"
  write_marker "discordPublicEnvOnlyGateFailureReason" "$DISCORD_PUBLIC_ENV_ONLY_GATE_FAILURE_REASON"
  write_marker "discordPublicEnvOnlyLineResult" "$DISCORD_PUBLIC_ENV_ONLY_LINE_RESULT"
  write_marker "discordPublicEnvOnlyLine" "$DISCORD_PUBLIC_ENV_ONLY_LINE"
  write_marker "discordPublicEnvOnlyJsonResult" "$DISCORD_PUBLIC_ENV_ONLY_JSON_RESULT"
  write_marker "discordPublicEnvOnlyJsonInstalled" "$DISCORD_PUBLIC_ENV_ONLY_JSON_INSTALLED"
  write_marker "discordPublicEnvOnlyJsonOrigin" "$DISCORD_PUBLIC_ENV_ONLY_JSON_ORIGIN"
  write_marker "discordPublicEnvOnlyJsonDefaultAccount" "$DISCORD_PUBLIC_ENV_ONLY_JSON_DEFAULT_ACCOUNT"
  write_marker "discordPublicEnvOnlyGatewayReachable" "$DISCORD_PUBLIC_ENV_ONLY_GATEWAY_REACHABLE"
  write_marker "discordPublicEnvOnlySystemdTokenRedacted" "$DISCORD_PUBLIC_ENV_ONLY_SYSTEMD_TOKEN_REDACTED"
  write_marker "discordPublicEnvOnlyConfigTokenFieldsAbsent" "$DISCORD_PUBLIC_ENV_ONLY_CONFIG_TOKEN_FIELDS_ABSENT"
  write_marker "discordPublicEnvOnlyConfigTokenFieldPaths" "$DISCORD_PUBLIC_ENV_ONLY_CONFIG_TOKEN_FIELD_PATHS"
  write_marker "discordStatusLayerLazyPluginBugSuspected" "$DISCORD_STATUS_LAYER_LAZY_PLUGIN_BUG_SUSPECTED"
  write_marker "discordFailureClass" "$DISCORD_FAILURE_CLASS"
  write_marker "discordRollbackDecision" "$DISCORD_ROLLBACK_DECISION"
  write_marker "discordRollbackReason" "$DISCORD_ROLLBACK_REASON"
  write_marker "discordEnvOnlyConfigPreserved" "$DISCORD_ENV_ONLY_CONFIG_PRESERVED"
  write_marker "discordKnownBadSecretRefRestoreSkipped" "$DISCORD_KNOWN_BAD_SECRETREF_RESTORE_SKIPPED"
  write_marker "discordPostFailureConfigHasTopLevelToken" "$DISCORD_POST_FAILURE_CONFIG_HAS_TOP_LEVEL_TOKEN"
  write_marker "discordPostFailureConfigShape" "$DISCORD_POST_FAILURE_CONFIG_SHAPE"
  write_marker "discordGatewayProviderStartupSeen" "$DISCORD_GATEWAY_PROVIDER_STARTUP_SEEN"
  write_marker "discordGatewayProviderStartupPattern" "$DISCORD_GATEWAY_PROVIDER_STARTUP_PATTERN"
  write_marker "discordGatewayGenericReadyOnly" "$DISCORD_GATEWAY_GENERIC_READY_ONLY"
  write_marker "discordGatewayProviderStartupDetectionResult" "$DISCORD_GATEWAY_PROVIDER_STARTUP_DETECTION_RESULT"
  write_marker "discordGatewayProviderStartupMatchedLine" "$DISCORD_GATEWAY_PROVIDER_STARTUP_MATCHED_LINE"
  write_marker "discordGatewayProviderStartupMatchedLineSha256" "$DISCORD_GATEWAY_PROVIDER_STARTUP_MATCHED_LINE_SHA256"
  write_marker "discordRuntimeMayStillWork" "$DISCORD_RUNTIME_MAY_STILL_WORK"
  write_marker "discordRepairAttempted" "$DISCORD_REPAIR_ATTEMPTED"
  write_marker "discordRepairMethod" "$DISCORD_REPAIR_METHOD"
  write_marker "discordRepairResult" "$DISCORD_REPAIR_RESULT"
  write_marker "discordRepairFailureReason" "$DISCORD_REPAIR_FAILURE_REASON"
  write_marker "discordLineBeforeNativeAdd" "$DISCORD_LINE_BEFORE_NATIVE_ADD"
  write_marker "discordLineAfterUseEnv" "$DISCORD_LINE_AFTER_USE_ENV"
  write_marker "discordLineAfterTokenFile" "$DISCORD_LINE_AFTER_TOKEN_FILE"
  write_marker "discordLineAfterBotToken" "$DISCORD_LINE_AFTER_BOT_TOKEN"
  write_marker "discordLineAfterNativeAdd" "$DISCORD_LINE_AFTER_NATIVE_ADD"
  write_marker "discordLineAfterSecretRefConfig" "$DISCORD_LINE_AFTER_SECRETREF_CONFIG"
  write_marker "discordLineAfterAccountScopedConfig" "$DISCORD_LINE_AFTER_ACCOUNT_SCOPED_CONFIG"
  write_marker "discordLineAfterEnvOnlyImplicitDefault" "$DISCORD_LINE_AFTER_ENV_ONLY_IMPLICIT_DEFAULT"
  write_marker "discordChannelStateParserResult" "$DISCORD_CHANNEL_STATE_PARSER_RESULT"
  write_marker "discordChannelStateBeforeRepair" "$DISCORD_CHANNEL_STATE_BEFORE_REPAIR"
  write_marker "discordChannelStateAfterRepair" "$DISCORD_CHANNEL_STATE_AFTER_REPAIR"
  write_marker "discordChannelInstalled" "$DISCORD_CHANNEL_INSTALLED"
  write_marker "discordChannelConfigured" "$DISCORD_CHANNEL_CONFIGURED"
  write_marker "discordChannelConfigResult" "$DISCORD_CHANNEL_CONFIG_RESULT"
  write_marker "discordChannelEnabled" "$DISCORD_CHANNEL_ENABLED"
  write_marker "discordChannelActivationResult" "$DISCORD_CHANNEL_ACTIVATION_RESULT"
  write_marker "discordConfigResult" "$DISCORD_CONFIG_RESULT"
  write_marker "discordConfigFailureReason" "$DISCORD_CONFIG_FAILURE_REASON"
  write_marker "discordPluginInstalled" "$DISCORD_PLUGIN_INSTALLED"
  write_marker "discordEnvTokenPresent" "$DISCORD_ENV_TOKEN_PRESENT"
  write_marker "discordAdapterEnvConfiguredPlausible" "$DISCORD_ADAPTER_ENV_CONFIGURED_PLAUSIBLE"
  write_marker "discordPublicAccountRecognized" "$DISCORD_PUBLIC_ACCOUNT_RECOGNIZED"
  write_marker "discordPublicStatusConfiguredEnabled" "$DISCORD_PUBLIC_STATUS_CONFIGURED_ENABLED"
  write_marker "discordProviderStartupObserved" "$DISCORD_PROVIDER_STARTUP_OBSERVED"
  write_marker "discordMessageProofCompleted" "$DISCORD_MESSAGE_PROOF_COMPLETED"
  write_marker "discordVerifierAllowed" "$DISCORD_VERIFIER_ALLOWED"
  write_marker "discordPublicAccountRecognitionSource" "$DISCORD_PUBLIC_ACCOUNT_RECOGNITION_SOURCE"
}

extract_discord_channel_line() {
  local source_file="$1"
  grep -iE '^- Discord([^:]*):' "$source_file" 2>/dev/null | head -n 1 || true
}

discord_public_line_is_env_only_ready() {
  local line="$1"
  local lower

  [[ -n "$line" ]] || return 1
  lower="$(printf '%s' "$line" | tr '[:upper:]' '[:lower:]')"
  [[ "$lower" == *"discord"* ]] || return 1
  [[ "$lower" != *"not installed"* && "$lower" == *"installed"* ]] || return 1
  [[ "$lower" != *"not configured"* && "$lower" == *"configured"* ]] || return 1
  [[ "$lower" != *"disabled"* && "$lower" == *"enabled"* ]] || return 1
  [[ "$lower" == *"token=env"* ]] || return 1
}

parse_discord_channel_line() {
  local line="$1"
  local lower installed configured enabled

  lower="$(printf '%s' "$line" | tr '[:upper:]' '[:lower:]')"
  installed="unknown"
  configured="unknown"
  enabled="unknown"

  if [[ -z "$line" ]]; then
    printf 'MISSING|%s|%s|%s\n' "$installed" "$configured" "$enabled"
    return 0
  fi

  if [[ "$lower" == *"not installed"* ]]; then
    installed="not-installed"
  elif [[ "$lower" == *"installed"* ]]; then
    installed="installed"
  fi

  if [[ "$lower" == *"not configured"* ]]; then
    configured="not-configured"
  elif [[ "$lower" == *"configured"* ]]; then
    configured="configured"
  fi

  if [[ "$lower" == *"disabled"* ]]; then
    enabled="disabled"
  elif [[ "$lower" == *"enabled"* ]]; then
    enabled="enabled"
  fi

  if [[ "$installed" == "unknown" && "$configured" == "unknown" && "$enabled" == "unknown" ]]; then
    printf 'FAIL|%s|%s|%s\n' "$installed" "$configured" "$enabled"
  else
    printf 'PASS|%s|%s|%s\n' "$installed" "$configured" "$enabled"
  fi
}

capture_discord_channel_state_summary() {
  local source_file="$1"
  local line parsed parser_result installed configured enabled
  line="$(extract_discord_channel_line "$source_file")"
  if [[ -z "$line" ]]; then
    DISCORD_CHANNEL_STATE_LINE="UNKNOWN"
    DISCORD_CHANNEL_STATE_PARSER_RESULT="MISSING"
    printf '%s|%s|%s\n' "unknown" "unknown" "unknown"
    return 0
  fi

  DISCORD_CHANNEL_STATE_LINE="$line"
  parsed="$(parse_discord_channel_line "$line")"
  IFS='|' read -r parser_result installed configured enabled <<<"$parsed"
  DISCORD_CHANNEL_STATE_PARSER_RESULT="$parser_result"
  if [[ "$parser_result" == "FAIL" ]]; then
    printf '%s|%s|%s\n' "unknown" "unknown" "unknown"
    return 0
  fi
  printf '%s|%s|%s\n' "$installed" "$configured" "$enabled"
}

is_discord_channel_configured_plugin_missing() {
  [[ "$1" == "not-installed|configured|disabled" ]]
}

discord_channel_activation_evidence_present() {
  local state_summary="$1"
  local journal_file="$2"
  local probe_file="${3:-}"
  local installed configured enabled

  IFS='|' read -r installed configured enabled <<<"$state_summary"

  if [[ "$installed" == "installed" && "$configured" == "configured" && "$enabled" == "enabled" ]]; then
    return 0
  fi

  if [[ -f "$journal_file" ]] && grep -qiE 'discord.*(ready|connected|login succeeded|login complete|logged in)' "$journal_file"; then
    return 0
  fi

  if [[ -n "$probe_file" ]] && [[ -f "$probe_file" ]] && grep -qiE 'discord.*(ready|connected|login succeeded|login complete|enabled)' "$probe_file"; then
    return 0
  fi

  return 1
}

discord_state_is_authoritative_pass() {
  [[ "$1" == "installed|configured|enabled" ]]
}

discord_state_failure_reason_for_summary() {
  local method="$1"
  local summary="$2"
  local installed configured enabled

  IFS='|' read -r installed configured enabled <<<"$summary"
  case "${installed}|${configured}|${enabled}" in
    "installed|configured|enabled")
      printf 'none\n'
      ;;
    "not-installed|configured|disabled")
      printf 'discord-state-not-installed-after-%s\n' "$method"
      ;;
    "not-installed|not-configured|disabled")
      printf 'discord-state-not-installed-not-configured-after-%s\n' "$method"
      ;;
    "installed|not-configured|disabled")
      printf 'discord-state-not-configured-after-%s\n' "$method"
      ;;
    "installed|configured|disabled")
      printf 'discord-state-disabled-after-%s\n' "$method"
      ;;
    *)
      printf 'discord-state-invalid-after-%s\n' "$method"
      ;;
  esac
}

discord_verifier_recommendation_allowed() {
  discord_state_is_authoritative_pass "$1"
}

log "Starting OpenClaw Discord configuration v1"
log "Log file: $LOG_FILE"
write_discord_channel_markers

require_cmd openclaw
require_cmd systemctl
require_cmd journalctl
require_cmd python3
require_cmd npm
require_cmd node

if [[ "$SKIP_BASELINE_CHECK" != "1" ]]; then
  log "Baseline guard: verifying bounded OpenClaw/Ollama surface"
  openclaw models list --provider ollama > "$LOG_DIR/openclaw_models_ollama.before.txt"
  cat "$LOG_DIR/openclaw_models_ollama.before.txt"
  default_model_json_raw="$LOG_DIR/openclaw_agents_defaults_model.before.raw.json"
  default_model_json_err="$LOG_DIR/openclaw_agents_defaults_model.before.raw.err"
  if ! openclaw config get agents.defaults.model --json > "$default_model_json_raw" 2> "$default_model_json_err"; then
    cat "$default_model_json_err" || true
    DISCORD_CONFIG_MODEL_GUARD_RESULT="FAIL"
    DISCORD_CONFIG_FAILURE_REASON="configured-primary-missing"
    write_discord_config_guard_markers
    die "Could not read agents.defaults.model JSON."
  fi
  [[ -s "$default_model_json_raw" ]] || {
    DISCORD_CONFIG_MODEL_GUARD_RESULT="FAIL"
    DISCORD_CONFIG_FAILURE_REASON="configured-primary-missing"
    write_discord_config_guard_markers
    die "agents.defaults.model JSON empty."
  }
  cat "$default_model_json_raw" | tee "$LOG_DIR/openclaw_agents_defaults_model.before.json"
  model_parse="$(python3 - "$default_model_json_raw" <<'PY'
import json,sys
doc=json.load(open(sys.argv[1],encoding='utf-8'))
primary=str(doc.get("primary",""))
fallbacks=doc.get("fallbacks",None)
if not isinstance(fallbacks,list) or not primary:
    print("status=fail")
    print("reason=configured-primary-missing")
    raise SystemExit(0)
safe_required={"ollama/qwen3.5:4b-4k","ollama/qwen3.5:2b-4k","ollama/qwen3:0.6b-4k"}
if primary=="ollama/qwen3:0.6b" and len(fallbacks)==0:
    print("status=ok")
    print("tier=minimal_wire")
elif primary=="ollama/qwen3.5:9b-4k" and safe_required.issubset(set(str(x) for x in fallbacks)):
    print("status=ok")
    print("tier=safe_full")
else:
    print("status=fail")
    print("reason=unsupported-primary-model")
    raise SystemExit(0)
print(f"primary={primary}")
PY
)"
  if ! grep -q '^status=ok$' <<<"$model_parse"; then
    DISCORD_CONFIG_MODEL_GUARD_RESULT="FAIL"
    DISCORD_CONFIG_FAILURE_REASON="$(awk -F= '/^reason=/{print $2}' <<<"$model_parse")"
    [[ -n "$DISCORD_CONFIG_FAILURE_REASON" ]] || DISCORD_CONFIG_FAILURE_REASON="unsupported-primary-model"
    write_discord_config_guard_markers
    die "Unsupported or missing configured primary model."
  fi
  DISCORD_CONFIG_MODEL_TIER="$(awk -F= '/^tier=/{print $2}' <<<"$model_parse")"
  DISCORD_CONFIG_EXPECTED_PRIMARY_MODEL="$(awk -F= '/^primary=/{print $2}' <<<"$model_parse")"
  run_shell_capture "systemd user environment before redacted" "$LOG_DIR/systemd_user_environment.before.txt" \
    "systemctl --user show-environment | grep -E 'OLLAMA|OPENCLAW|DISCORD|CUDA' | sed -E 's/^([^=]*(TOKEN|SECRET|PASSWORD|KEY)[^=]*)=.*/\\1=<REDACTED>/I' || true"

  awk -v model="$DISCORD_CONFIG_EXPECTED_PRIMARY_MODEL" '$1 == model { found = 1 } END { exit(found ? 0 : 1) }' "$LOG_DIR/openclaw_models_ollama.before.txt" || {
    DISCORD_CONFIG_MODEL_GUARD_RESULT="FAIL"
    DISCORD_CONFIG_FAILURE_REASON="openclaw-model-list-missing-primary"
    write_discord_config_guard_markers
    die "Configured primary model not found in OpenClaw Ollama model list: $DISCORD_CONFIG_EXPECTED_PRIMARY_MODEL"
  }
  if [[ "$DISCORD_CONFIG_MODEL_TIER" == "safe_full" ]]; then
    grep -q 'ollama/qwen3.5:4b-4k' "$LOG_DIR/openclaw_models_ollama.before.txt" || {
      DISCORD_CONFIG_MODEL_GUARD_RESULT="FAIL"
      DISCORD_CONFIG_FAILURE_REASON="openclaw-model-list-missing-primary"
      write_discord_config_guard_markers
      die "Full-safe fallback model missing: ollama/qwen3.5:4b-4k"
    }
    grep -q 'ollama/qwen3.5:2b-4k' "$LOG_DIR/openclaw_models_ollama.before.txt" || {
      DISCORD_CONFIG_MODEL_GUARD_RESULT="FAIL"
      DISCORD_CONFIG_FAILURE_REASON="openclaw-model-list-missing-primary"
      write_discord_config_guard_markers
      die "Full-safe fallback model missing: ollama/qwen3.5:2b-4k"
    }
    grep -q 'ollama/qwen3:0.6b-4k' "$LOG_DIR/openclaw_models_ollama.before.txt" || {
      DISCORD_CONFIG_MODEL_GUARD_RESULT="FAIL"
      DISCORD_CONFIG_FAILURE_REASON="openclaw-model-list-missing-primary"
      write_discord_config_guard_markers
      die "Full-safe fallback model missing: ollama/qwen3:0.6b-4k"
    }
  fi
  if [[ "$DISCORD_CONFIG_MODEL_TIER" == "safe_full" ]]; then
    grep -qiE '\b4k\b|4096' "$LOG_DIR/openclaw_models_ollama.before.txt" || die "OpenClaw safe-full model list does not show bounded 4k context."
  fi
  grep -q 'OLLAMA_API_KEY=<REDACTED>' "$LOG_DIR/systemd_user_environment.before.txt" || {
    DISCORD_CONFIG_MODEL_GUARD_RESULT="FAIL"
    DISCORD_CONFIG_FAILURE_REASON="missing-ollama-api-key"
    write_discord_config_guard_markers
    die "OLLAMA_API_KEY missing from systemd user environment."
  }
  DISCORD_CONFIG_MODEL_GUARD_RESULT="PASS"
  DISCORD_CONFIG_FAILURE_REASON="none"
  write_discord_config_guard_markers
fi

log "Collecting Discord token"
TOKEN_VALUE=""
if [[ -n "$TOKEN_FILE" ]]; then
  TOKEN_VALUE="$(load_secret_from_file "$TOKEN_FILE" || true)"
  if [[ -z "$TOKEN_VALUE" ]]; then
    [[ "$DISCORD_TOKEN_READ_RESULT" == "FAIL" ]] || DISCORD_TOKEN_READ_RESULT="FAIL"
    die "Discord token file is missing or empty: $TOKEN_FILE"
  fi
  DISCORD_TOKEN_SOURCE="file"
  log "Using Discord bot token from configured local secret file reference."
elif [[ "$REFRESH_TOKEN" == "1" ]]; then
  prompt_secret "Paste NEW Discord bot token for ${TOKEN_ENV}: " TOKEN_VALUE
  DISCORD_TOKEN_SOURCE="prompt"
else
  TOKEN_VALUE="$(load_existing_secret "$TOKEN_ENV" || true)"
  if [[ -n "$TOKEN_VALUE" ]]; then
    DISCORD_TOKEN_SOURCE="env"
    log "Using existing ${TOKEN_ENV} from shell/systemd/.openclaw env storage."
  else
    prompt_secret "Paste Discord bot token for ${TOKEN_ENV} (or rerun with --token-file <path>): " TOKEN_VALUE
    DISCORD_TOKEN_SOURCE="prompt"
  fi
fi
[[ -n "$TOKEN_VALUE" ]] || die "Discord token is empty. Use --refresh-token and paste a valid current Discord bot token."
if [[ "$DISCORD_TOKEN_SOURCE" == "unknown" ]]; then
  DISCORD_TOKEN_SOURCE="prompt"
fi
[[ "$DISCORD_TOKEN_FILE_CONFIGURED" == "YES" ]] || DISCORD_TOKEN_FILE_CONFIGURED="NO"
if [[ "$DISCORD_TOKEN_SOURCE" != "file" && "$DISCORD_TOKEN_FILE_PRESENT" == "UNKNOWN" ]]; then
  DISCORD_TOKEN_FILE_PRESENT="NO"
  DISCORD_TOKEN_FILE_NON_EMPTY="NO"
fi
if [[ "$DISCORD_TOKEN_SOURCE" != "file" && "$DISCORD_TOKEN_READ_RESULT" == "NOT_ATTEMPTED" ]]; then
  DISCORD_TOKEN_READ_RESULT="PASS"
fi
log "Token source resolved: ${DISCORD_TOKEN_SOURCE}; read result=${DISCORD_TOKEN_READ_RESULT}; token value not logged."

log "Persisting Discord token by environment variable name: $TOKEN_ENV"
mkdir -p "$HOME/.openclaw" "$HOME/.config/environment.d"
touch "$HOME/.openclaw/.env"
chmod 600 "$HOME/.openclaw/.env"

# Local runtime secret handling: OpenClaw Discord token=env operation requires
# env material. Keep it user-local/protected and never mirror the value to proofs.
tmp="$(mktemp)"
grep -v "^${TOKEN_ENV}=" "$HOME/.openclaw/.env" > "$tmp" 2>/dev/null || true
printf '%s=%s\n' "$TOKEN_ENV" "$TOKEN_VALUE" >> "$tmp"
cat "$tmp" > "$HOME/.openclaw/.env"
rm -f "$tmp"
chmod 600 "$HOME/.openclaw/.env"

cat > "$HOME/.config/environment.d/openclaw-discord.conf" <<EOF
${TOKEN_ENV}=${TOKEN_VALUE}
EOF
chmod 600 "$HOME/.config/environment.d/openclaw-discord.conf"

export "${TOKEN_ENV}=${TOKEN_VALUE}"
systemctl --user import-environment "$TOKEN_ENV" || true
redact_file "$HOME/.openclaw/.env" "$RED_DIR/openclaw.env.redacted"
capture_script_systemd_discord_env_proof
write_discord_channel_markers

log "Collecting Discord diagnostics and channel repair state"
run_capture "OpenClaw version" "$LOG_DIR/openclaw_version.txt" openclaw --version || true
run_capture "npm version" "$LOG_DIR/npm_version.txt" npm --version || true
run_capture "OpenClaw plugin list before (diagnostic only)" "$LOG_DIR/openclaw_plugins_list.before.txt" openclaw plugins list || true
python3 - <<'PY' > "$LOG_DIR/openclaw_plugins_allow.before.txt" 2>/dev/null || true
import json
from pathlib import Path
p=Path.home()/".openclaw"/"openclaw.json"
if p.exists():
    cfg=json.loads(p.read_text())
    print(json.dumps(cfg.get("plugins",{}).get("allow"), indent=2))
else:
    print("openclaw.json not found")
PY
DISCORD_EXTERNAL_PLUGIN_INSTALL_ATTEMPTED="NO"
DISCORD_EXTERNAL_PLUGIN_INSTALL_RESULT="NOT_REQUIRED"

OPENCLAW_CONFIG_PATH="$HOME/.openclaw/openclaw.json"
OPENCLAW_CONFIG_BACKUP="$LOG_DIR/openclaw.json.before_discord_mutation.bak"
OPENCLAW_CONFIG_PREEXISTED="NO"
if [[ -f "$OPENCLAW_CONFIG_PATH" ]]; then
  cp -a "$OPENCLAW_CONFIG_PATH" "$OPENCLAW_CONFIG_BACKUP"
  OPENCLAW_CONFIG_PREEXISTED="YES"
fi

apply_openclaw_readonly_external_plugins_patch
write_discord_channel_markers

restore_openclaw_config_backup() {
  if [[ "$OPENCLAW_CONFIG_PREEXISTED" == "YES" && -f "$OPENCLAW_CONFIG_BACKUP" ]]; then
    cp -a "$OPENCLAW_CONFIG_BACKUP" "$OPENCLAW_CONFIG_PATH"
  else
    rm -f "$OPENCLAW_CONFIG_PATH"
  fi
}

capture_post_failure_discord_config_shape() {
  local prefix="${1:-post_failure}"
  local shape_out="$LOG_DIR/openclaw_discord_config_shape.${prefix}.txt"
  local redacted_out="$LOG_DIR/openclaw_discord_config.${prefix}.redacted.json"

  python3 - "$OPENCLAW_CONFIG_PATH" "$redacted_out" > "$shape_out" <<'PY' 2>/dev/null || true
import json, os, sys
path, redacted_out = sys.argv[1], sys.argv[2]
has_top = "UNKNOWN"
shape = "unknown"

def redact(value):
    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            lower = str(key).lower()
            if any(s in lower for s in ("token", "secret", "password", "key")):
                if isinstance(item, dict) and set(item).issubset({"source", "provider", "id"}):
                    out[key] = dict(item)
                else:
                    out[key] = "<REDACTED>"
            else:
                out[key] = redact(item)
        return out
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value

try:
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    discord = ((doc.get("channels") or {}).get("discord") or {})
    accounts = discord.get("accounts") if isinstance(discord.get("accounts"), (dict, list)) else {}
    default = {}
    if isinstance(accounts, dict):
        candidate = accounts.get("default")
        default = candidate if isinstance(candidate, dict) else {}
    has_top = "YES" if "token" in discord else "NO"
    has_default_token = "YES" if "token" in default else "NO"
    if has_top == "YES":
        token = discord.get("token")
        if isinstance(token, dict) and token.get("source") == "env" and token.get("provider") == "default" and token.get("id") == "DISCORD_BOT_TOKEN":
            shape = "top-level-secretref"
        else:
            shape = "top-level-token"
    elif has_default_token == "YES":
        shape = "account-scoped"
    elif isinstance(discord, dict) and discord.get("enabled") is True and not discord.get("token"):
        shape = "env-only"
    else:
        shape = "unknown"
    with open(redacted_out, "w", encoding="utf-8") as fh:
        json.dump(redact(discord), fh, indent=2, sort_keys=True)
        fh.write("\n")
except Exception:
    pass

print(f"hasTopLevelToken={has_top}")
print(f"shape={shape}")
PY

  DISCORD_POST_FAILURE_CONFIG_HAS_TOP_LEVEL_TOKEN="$(sed -n 's/^hasTopLevelToken=//p' "$shape_out" | head -n 1)"
  DISCORD_POST_FAILURE_CONFIG_SHAPE="$(sed -n 's/^shape=//p' "$shape_out" | head -n 1)"
  [[ -n "$DISCORD_POST_FAILURE_CONFIG_HAS_TOP_LEVEL_TOKEN" ]] || DISCORD_POST_FAILURE_CONFIG_HAS_TOP_LEVEL_TOKEN="UNKNOWN"
  [[ -n "$DISCORD_POST_FAILURE_CONFIG_SHAPE" ]] || DISCORD_POST_FAILURE_CONFIG_SHAPE="unknown"
}

detect_discord_gateway_provider_startup() {
  local prefix="$1"
  local journal_file="$LOG_DIR/openclaw_gateway_journal.${prefix}.txt"
  local probe_file="$LOG_DIR/openclaw_channels_status_probe.${prefix}.txt"
  local discord_startup_regex generic_ready_regex harness_metadata_regex matched_line redacted_line matched_file
  DISCORD_GATEWAY_PROVIDER_STARTUP_SEEN="NO"
  DISCORD_GATEWAY_PROVIDER_STARTUP_PATTERN="none"
  DISCORD_GATEWAY_GENERIC_READY_ONLY="NO"
  DISCORD_GATEWAY_PROVIDER_STARTUP_DETECTION_RESULT="FAIL"
  DISCORD_GATEWAY_PROVIDER_STARTUP_MATCHED_LINE="none"
  DISCORD_GATEWAY_PROVIDER_STARTUP_MATCHED_LINE_SHA256="none"
  DISCORD_RUNTIME_MAY_STILL_WORK="UNKNOWN"

  # Discord-specific startup proof only. Generic gateway readiness, channel startup,
  # plugin registry lines, provider auth pre-warm, or unrelated plugin warnings must not count.
  discord_startup_regex='(^|[^[:alnum:]_])(\[discord\]|monitorDiscordProvider|discord[[:space:]-]+provider[[:space:]].*(start|startup|started|running)|starting[[:space:]]+provider.*discord|discord.*starting[[:space:]]+provider|discord.*(login|logged[[:space:]]+in|connected|ready)|default[[:space:]]+discord[[:space:]]+account[[:space:]]+startup|\[default\][[:space:]].*(starting[[:space:]]+provider.*discord|discord.*starting[[:space:]]+provider))([^[:alnum:]_]|$)'
  generic_ready_regex='\[gateway\].*(ready|http server listening|starting channels and sidecars)|\[plugins\].*\[ollama\]|starting channels and sidecars|provider auth state pre-warmed'
  harness_metadata_regex='^[[:space:]]*##[[:space:]]*(Command|Started|Finished|Exit code):|^[[:space:]]*##|journalctl[[:space:]].*openclaw-gateway|grep[[:space:]]+-[^[:space:]]*E|openclaw_gateway_journal|openclaw_channels_status_probe|discord_gateway_provider_startup_matched_line'
  matched_line="$(grep -hiE "$discord_startup_regex" "$journal_file" "$probe_file" 2>/dev/null | grep -viE "$harness_metadata_regex" | head -n 1 || true)"

  if [[ -n "$matched_line" ]]; then
    redacted_line="$(printf '%s' "$matched_line" | sed -E 's/([A-Za-z0-9_]*(TOKEN|SECRET|PASSWORD|KEY)[A-Za-z0-9_]*[=:][[:space:]]*)[^[:space:],;)}]+/\1<REDACTED>/Ig; s/(Bot[[:space:]]+)[A-Za-z0-9._-]+/\1<REDACTED>/Ig')"
    matched_file="$LOG_DIR/discord_gateway_provider_startup_matched_line.${prefix}.redacted.txt"
    printf '%s\n' "$redacted_line" > "$matched_file"
    DISCORD_GATEWAY_PROVIDER_STARTUP_SEEN="YES"
    DISCORD_GATEWAY_PROVIDER_STARTUP_PATTERN="discord-specific-provider-startup"
    DISCORD_GATEWAY_PROVIDER_STARTUP_DETECTION_RESULT="PASS"
    DISCORD_GATEWAY_PROVIDER_STARTUP_MATCHED_LINE="$redacted_line"
    DISCORD_GATEWAY_PROVIDER_STARTUP_MATCHED_LINE_SHA256="$(printf '%s' "$redacted_line" | sha256sum | awk '{print $1}')"
    DISCORD_RUNTIME_MAY_STILL_WORK="YES"
  elif grep -hiE "$generic_ready_regex" "$journal_file" "$probe_file" 2>/dev/null | grep -qviE "$harness_metadata_regex"; then
    DISCORD_GATEWAY_GENERIC_READY_ONLY="YES"
    DISCORD_GATEWAY_PROVIDER_STARTUP_DETECTION_RESULT="PASS"
  fi
}

should_preserve_env_only_adapter_valid_config() {
  [[ "$DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_ATTEMPTED" == "YES" ]] || return 1
  [[ "$DISCORD_LOADED_ADAPTER_PROOF_RESULT" == "PASS" ]] || return 1
  [[ "$DISCORD_LOADED_ADAPTER_CONFIGURED_ENV_ONLY" == "YES" ]] || return 1
  [[ "$DISCORD_LOADED_ADAPTER_TOKEN_SOURCE_ENV_ONLY" == "env" ]] || return 1
  [[ "$DISCORD_LOADED_ADAPTER_TOKEN_STATUS_ENV_ONLY" == "available" ]] || return 1
  [[ "$DISCORD_FAILURE_CLASS" == "status-layer-lazy-plugin-account-drop" ]] || return 1
  ! discord_state_is_authoritative_pass "${DISCORD_CHANNEL_INSTALLED}|${DISCORD_CHANNEL_CONFIGURED}|${DISCORD_CHANNEL_ENABLED}"
}

handle_failed_discord_config_rollback() {
  detect_discord_gateway_provider_startup "after_env_only_implicit_default"

  if should_preserve_env_only_adapter_valid_config; then
    DISCORD_ROLLBACK_DECISION="preserve-env-only"
    DISCORD_ROLLBACK_REASON="adapter-proof-pass-public-status-layer-lazy-plugin-account-drop"
    DISCORD_ENV_ONLY_CONFIG_PRESERVED="YES"
    DISCORD_KNOWN_BAD_SECRETREF_RESTORE_SKIPPED="YES"
  else
    DISCORD_ROLLBACK_DECISION="restore-backup"
    DISCORD_ROLLBACK_REASON="adapter-proof-or-failure-class-not-eligible"
    DISCORD_ENV_ONLY_CONFIG_PRESERVED="NO"
    DISCORD_KNOWN_BAD_SECRETREF_RESTORE_SKIPPED="NO"
    restore_openclaw_config_backup
    restart_openclaw_gateway
  fi

  capture_post_failure_discord_config_shape "post_failure"
  write_discord_channel_markers
}

restart_openclaw_gateway() {
  if [[ "$NO_RESTART" != "1" ]]; then
    systemctl --user daemon-reload || true
    systemctl --user restart openclaw-gateway.service
    sleep 8
  fi
  RESTART_SINCE="$(systemctl --user show openclaw-gateway.service -p ActiveEnterTimestamp --value || date '+%Y-%m-%d %H:%M:%S')"
}

capture_discord_state_files() {
  local prefix="$1"
  run_capture "OpenClaw gateway status ${prefix}" "$LOG_DIR/openclaw_gateway_status.${prefix}.txt" systemctl --user status openclaw-gateway.service --no-pager || true
  run_shell_capture "OpenClaw gateway journal ${prefix}" "$LOG_DIR/openclaw_gateway_journal.${prefix}.txt" \
    "journalctl --user -u openclaw-gateway.service --since '$RESTART_SINCE' --no-pager | grep -iE 'discord|gateway|plugin|ready|error|warn|owner|token|pair|channel|unknown|fail|login|connected|intent|unauthorized' || true"
  run_openclaw_with_discord_env "OpenClaw channels list --all ${prefix}" "$LOG_DIR/openclaw_channels_list_all.${prefix}.txt" channels list --all || true
  run_openclaw_with_discord_env "OpenClaw channels list --all --json ${prefix}" "$LOG_DIR/openclaw_channels_list_all_json.${prefix}.txt" channels list --all --json || true
  run_openclaw_with_discord_env "OpenClaw channels list ${prefix}" "$LOG_DIR/openclaw_channels_list.${prefix}.txt" channels list || true
  run_openclaw_with_discord_env "OpenClaw channels status --probe ${prefix}" "$LOG_DIR/openclaw_channels_status_probe.${prefix}.txt" channels status --probe || true
  run_openclaw_with_discord_env "OpenClaw status --deep ${prefix}" "$LOG_DIR/openclaw_status_deep.${prefix}.txt" status --deep || true
  run_shell_capture "systemd user environment ${prefix} redacted" "$LOG_DIR/systemd_user_environment.${prefix}.txt" \
    "systemctl --user show-environment | grep -E 'OLLAMA|OPENCLAW|DISCORD|CUDA' | sed -E 's/^([^=]*(TOKEN|SECRET|PASSWORD|KEY)[^=]*)=.*/\\1=<REDACTED>/I' || true"
}

refresh_discord_state() {
  local prefix="$1"
  local target="${2:-$1}"
  local summary
  summary="$(capture_discord_channel_state_summary "$LOG_DIR/openclaw_channels_list_all.${prefix}.txt")"
  if [[ "$summary" == "unknown|unknown|unknown" ]]; then
    summary="$(capture_discord_channel_state_summary "$LOG_DIR/openclaw_channels_list.${prefix}.txt")"
  fi
  if [[ "$target" == "before_repair" ]]; then
    DISCORD_CHANNEL_STATE_BEFORE_REPAIR="$summary"
  elif [[ "$target" == "after_repair" || "$target" == "after_native_add" ]]; then
    DISCORD_CHANNEL_STATE_AFTER_REPAIR="$summary"
  fi
  IFS='|' read -r DISCORD_CHANNEL_INSTALLED DISCORD_CHANNEL_CONFIGURED DISCORD_CHANNEL_ENABLED <<<"$summary"
  if [[ "$summary" == "unknown|unknown|unknown" ]]; then
    return 1
  fi
  return 0
}

run_capture_logged_command() {
  local label="$1"
  local outfile="$2"
  local logged_command="$3"
  shift 3
  log "$label"
  {
    echo "## $label"
    echo "## Started: $(date -Iseconds)"
    echo "## Command: $logged_command"
    echo
    "$@"
    rc=$?
    echo
    echo "## Exit code: $rc"
    echo "## Finished: $(date -Iseconds)"
    return "$rc"
  } | tee "$outfile"
}

discord_activation_proven() {
  local state_summary="$1"
  local journal_file="$2"
  local probe_file="$3"
  local installed configured enabled

  IFS='|' read -r installed configured enabled <<<"$state_summary"
  if [[ "$installed" == "installed" && "$configured" == "configured" && "$enabled" == "enabled" ]]; then
    return 0
  fi
  if [[ -f "$journal_file" ]] && grep -qiE 'discord.*(ready|connected|login succeeded|login complete|logged in)' "$journal_file"; then
    return 0
  fi
  if [[ -f "$probe_file" ]] && grep -qiE 'discord.*(ready|connected|login succeeded|login complete|enabled)' "$probe_file"; then
    return 0
  fi
  return 1
}

record_native_add_attempt_state() {
  local method="$1"
  local prefix="$2"
  local state_summary="$3"
  local command_result="$4"
  local state_result="$5"
  local failure_reason="$6"

  DISCORD_NATIVE_CHANNEL_ADD_COMMAND_RESULT="$command_result"
  DISCORD_NATIVE_CHANNEL_ADD_STATE_RESULT="$state_result"
  DISCORD_NATIVE_CHANNEL_ADD_FAILURE_REASON="$failure_reason"
  DISCORD_NATIVE_CHANNEL_ADD_FINAL_METHOD="$method"

  case "$prefix" in
    after_use_env) DISCORD_LINE_AFTER_USE_ENV="$DISCORD_CHANNEL_STATE_LINE" ;;
    after_token_file) DISCORD_LINE_AFTER_TOKEN_FILE="$DISCORD_CHANNEL_STATE_LINE" ;;
    after_bot_token) DISCORD_LINE_AFTER_BOT_TOKEN="$DISCORD_CHANNEL_STATE_LINE" ;;
    after_native_add) DISCORD_LINE_AFTER_NATIVE_ADD="$DISCORD_CHANNEL_STATE_LINE" ;;
  esac
  DISCORD_LINE_AFTER_NATIVE_ADD="$DISCORD_CHANNEL_STATE_LINE"

  if [[ "$state_summary" != "unknown|unknown|unknown" ]]; then
    IFS='|' read -r DISCORD_CHANNEL_INSTALLED DISCORD_CHANNEL_CONFIGURED DISCORD_CHANNEL_ENABLED <<<"$state_summary"
    DISCORD_CHANNEL_STATE_AFTER_REPAIR="$state_summary"
  fi

  write_discord_channel_markers
}

attempt_native_add_method() {
  local method="$1"
  local prefix="$2"
  local output_file="$3"
  local logged_command="$4"
  local state_summary state_result failure_reason command_result validation_file validation_result
  shift 4

  DISCORD_NATIVE_CHANNEL_ADD_ATTEMPTED="YES"
  if [[ "$DISCORD_NATIVE_CHANNEL_ADD_METHODS_TRIED" == "none" ]]; then
    DISCORD_NATIVE_CHANNEL_ADD_METHODS_TRIED="$method"
  else
    DISCORD_NATIVE_CHANNEL_ADD_METHODS_TRIED="${DISCORD_NATIVE_CHANNEL_ADD_METHODS_TRIED},${method}"
  fi
  write_discord_channel_markers

  if run_capture_logged_command "$logged_command" "$output_file" "$logged_command" "$@"; then
    command_result="PASS"
  else
    command_result="FAIL"
  fi

  validation_file="$LOG_DIR/openclaw_config_validate.${method}.txt"
  validation_result="PASS"
  if [[ "$command_result" == "PASS" ]]; then
    if ! openclaw config validate > "$validation_file" 2>&1; then
      validation_result="FAIL"
      failure_reason="config-validation-failed-after-${method}"
      cat "$validation_file"
    fi
  fi

  restart_openclaw_gateway
  RESTART_SINCE="$(systemctl --user show openclaw-gateway.service -p ActiveEnterTimestamp --value || date '+%Y-%m-%d %H:%M:%S')"
  capture_discord_state_files "$prefix"

  case "$prefix" in
    after_use_env)
      DISCORD_LINE_AFTER_USE_ENV="$(extract_discord_channel_line "$LOG_DIR/openclaw_channels_list_all.${prefix}.txt")"
      ;;
    after_token_file)
      DISCORD_LINE_AFTER_TOKEN_FILE="$(extract_discord_channel_line "$LOG_DIR/openclaw_channels_list_all.${prefix}.txt")"
      ;;
    after_bot_token)
      DISCORD_LINE_AFTER_BOT_TOKEN="$(extract_discord_channel_line "$LOG_DIR/openclaw_channels_list_all.${prefix}.txt")"
      ;;
    after_native_add)
      DISCORD_LINE_AFTER_NATIVE_ADD="$(extract_discord_channel_line "$LOG_DIR/openclaw_channels_list_all.${prefix}.txt")"
      ;;
  esac
  case "$prefix" in
    after_use_env) [[ -z "$DISCORD_LINE_AFTER_USE_ENV" ]] && DISCORD_LINE_AFTER_USE_ENV="$(extract_discord_channel_line "$LOG_DIR/openclaw_channels_list.${prefix}.txt")" ;;
    after_token_file) [[ -z "$DISCORD_LINE_AFTER_TOKEN_FILE" ]] && DISCORD_LINE_AFTER_TOKEN_FILE="$(extract_discord_channel_line "$LOG_DIR/openclaw_channels_list.${prefix}.txt")" ;;
    after_bot_token) [[ -z "$DISCORD_LINE_AFTER_BOT_TOKEN" ]] && DISCORD_LINE_AFTER_BOT_TOKEN="$(extract_discord_channel_line "$LOG_DIR/openclaw_channels_list.${prefix}.txt")" ;;
    after_native_add) [[ -z "$DISCORD_LINE_AFTER_NATIVE_ADD" ]] && DISCORD_LINE_AFTER_NATIVE_ADD="$(extract_discord_channel_line "$LOG_DIR/openclaw_channels_list.${prefix}.txt")" ;;
  esac

  state_summary="$(capture_discord_channel_state_summary "$LOG_DIR/openclaw_channels_list_all.${prefix}.txt")"
  if [[ "$state_summary" == "unknown|unknown|unknown" ]]; then
    state_summary="$(capture_discord_channel_state_summary "$LOG_DIR/openclaw_channels_list.${prefix}.txt")"
  fi

  if [[ "$validation_result" == "PASS" ]] && discord_state_is_authoritative_pass "$state_summary"; then
    state_result="PASS"
    failure_reason="none"
  else
    state_result="FAIL"
    if [[ "$validation_result" == "FAIL" ]]; then
      failure_reason="config-validation-failed-after-${method}"
    elif [[ "$DISCORD_CHANNEL_STATE_PARSER_RESULT" == "MISSING" ]]; then
      failure_reason="discord-line-missing-after-${method}"
    elif [[ "$DISCORD_CHANNEL_STATE_PARSER_RESULT" == "FAIL" || "$state_summary" == "unknown|unknown|unknown" ]]; then
      failure_reason="discord-line-missing-after-${method}"
    else
      failure_reason="$(discord_state_failure_reason_for_summary "$method" "$state_summary")"
    fi
  fi

  record_native_add_attempt_state "$method" "$prefix" "$state_summary" "$command_result" "$state_result" "$failure_reason"

  if [[ "$state_result" == "PASS" ]]; then
    DISCORD_NATIVE_CHANNEL_ADD_RESULT="PASS"
    DISCORD_NATIVE_CHANNEL_ADD_FAILURE_REASON="none"
    return 0
  fi

  restore_openclaw_config_backup
  restart_openclaw_gateway
  DISCORD_NATIVE_CHANNEL_ADD_RESULT="FAIL"
  return 1
}

capture_redacted_discord_config_snapshot() {
  local prefix="$1"
  python3 - "$prefix" <<'PY' > "$LOG_DIR/openclaw_discord_config.${prefix}.redacted.json" 2>/dev/null || true
import json, os, sys
prefix = sys.argv[1]
path = os.path.expanduser("~/.openclaw/openclaw.json")
if not os.path.exists(path):
    print("{}")
    raise SystemExit(0)
doc = json.load(open(path, encoding="utf-8"))
discord = ((doc.get("channels") or {}).get("discord") or {})
def redact(value):
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            if any(s in k.lower() for s in ["token", "secret", "password", "key"]):
                if isinstance(v, dict) and set(v).issubset({"source", "provider", "id"}):
                    out[k] = redact(v)
                else:
                    out[k] = "<REDACTED>"
            else:
                out[k] = redact(v)
        return out
    if isinstance(value, list):
        return [redact(v) for v in value]
    return value
print(json.dumps({"snapshot": prefix, "discord": redact(discord)}, indent=2, sort_keys=True))
PY
}

count_discord_accounts_from_json_capture() {
  local file="$1"
  python3 - "$file" <<'PY' 2>/dev/null || printf 'UNKNOWN\n'
import json, sys
path = sys.argv[1]
text = open(path, encoding="utf-8", errors="replace").read()
start = text.find("{")
end = text.rfind("}")
if start < 0 or end < start:
    print("UNKNOWN")
    raise SystemExit(0)
doc = json.loads(text[start:end + 1])
count = None
for candidate in (
    ((doc.get("channels") or {}).get("discord") or {}).get("accounts"),
    ((doc.get("channelAccounts") or {}).get("discord")),
    (doc.get("discord") or {}).get("accounts") if isinstance(doc.get("discord"), dict) else None,
):
    if isinstance(candidate, list):
        count = len(candidate)
        break
    if isinstance(candidate, dict):
        count = len(candidate)
        break
if count is None:
    chat_discord = (doc.get("chat") or {}).get("discord")
    if isinstance(chat_discord, dict):
        accounts = chat_discord.get("accounts")
        if isinstance(accounts, list):
            count = len(accounts)
        elif isinstance(accounts, dict):
            count = len(accounts)
    elif isinstance(chat_discord, list):
        count = len(chat_discord)
print(count if count is not None else "UNKNOWN")
PY
}

capture_discord_public_env_only_json_gate() {
  local prefix="$1"
  local json_file="$LOG_DIR/openclaw_channels_list_all_json.${prefix}.txt"
  local parse_out="$LOG_DIR/discord_public_env_only_json_gate.${prefix}.markers"

  python3 - "$json_file" > "$parse_out" <<'PY' 2>/dev/null || true
import json, sys

path = sys.argv[1]
try:
    text = open(path, encoding="utf-8", errors="replace").read()
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end < start:
        raise ValueError("json object not found")
    doc = json.loads(text[start:end + 1])
except Exception:
    print("result=FAIL")
    print("installed=UNKNOWN")
    print("origin=UNKNOWN")
    print("defaultAccount=UNKNOWN")
    raise SystemExit(0)

def get_path(root, path_items):
    current = root
    for item in path_items:
        if not isinstance(current, dict):
            return None
        current = current.get(item)
    return current

discord = None
for path_items in (
    ("chat", "discord"),
    ("channels", "discord"),
    ("discord",),
):
    candidate = get_path(doc, path_items)
    if isinstance(candidate, dict):
        discord = candidate
        break

accounts = discord.get("accounts") if isinstance(discord, dict) else None
if isinstance(accounts, list):
    default_account = "YES" if "default" in [str(item) for item in accounts] else "NO"
elif isinstance(accounts, dict):
    default_account = "YES" if "default" in accounts else "NO"
else:
    default_account = "NO"

installed = "YES" if isinstance(discord, dict) and discord.get("installed") is True else "NO"
origin = str(discord.get("origin") if isinstance(discord, dict) and discord.get("origin") is not None else "UNKNOWN")
ok = installed == "YES" and origin == "configured" and default_account == "YES"

print(f"result={'PASS' if ok else 'FAIL'}")
print(f"installed={installed}")
print(f"origin={origin}")
print(f"defaultAccount={default_account}")
PY

  DISCORD_PUBLIC_ENV_ONLY_JSON_RESULT="$(awk -F= '/^result=/{print $2}' "$parse_out" | head -n 1)"
  DISCORD_PUBLIC_ENV_ONLY_JSON_INSTALLED="$(awk -F= '/^installed=/{print $2}' "$parse_out" | head -n 1)"
  DISCORD_PUBLIC_ENV_ONLY_JSON_ORIGIN="$(awk -F= '/^origin=/{print $2}' "$parse_out" | head -n 1)"
  DISCORD_PUBLIC_ENV_ONLY_JSON_DEFAULT_ACCOUNT="$(awk -F= '/^defaultAccount=/{print $2}' "$parse_out" | head -n 1)"
  [[ -n "$DISCORD_PUBLIC_ENV_ONLY_JSON_RESULT" ]] || DISCORD_PUBLIC_ENV_ONLY_JSON_RESULT="FAIL"
  [[ -n "$DISCORD_PUBLIC_ENV_ONLY_JSON_INSTALLED" ]] || DISCORD_PUBLIC_ENV_ONLY_JSON_INSTALLED="UNKNOWN"
  [[ -n "$DISCORD_PUBLIC_ENV_ONLY_JSON_ORIGIN" ]] || DISCORD_PUBLIC_ENV_ONLY_JSON_ORIGIN="UNKNOWN"
  [[ -n "$DISCORD_PUBLIC_ENV_ONLY_JSON_DEFAULT_ACCOUNT" ]] || DISCORD_PUBLIC_ENV_ONLY_JSON_DEFAULT_ACCOUNT="UNKNOWN"
}

capture_discord_public_env_only_config_token_field_gate() {
  local prefix="$1"
  local parse_out="$LOG_DIR/discord_public_env_only_config_token_field_gate.${prefix}.markers"

  python3 - "$OPENCLAW_CONFIG_PATH" > "$parse_out" <<'PY' 2>/dev/null || true
import json, sys

path = sys.argv[1]
found = []
parse_ok = True

try:
    doc = json.load(open(path, encoding="utf-8"))
    discord = ((doc.get("channels") or {}).get("discord") or {})
except Exception:
    parse_ok = False
    discord = {}

def walk(value, path_items):
    if isinstance(value, dict):
        for key, item in value.items():
            next_path = path_items + [str(key)]
            if str(key).lower() == "token":
                found.append(".".join(next_path))
            walk(item, next_path)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            walk(item, path_items + [str(index)])

walk(discord, ["channels", "discord"])
if not parse_ok:
    print("tokenFieldsAbsent=UNKNOWN")
    print("tokenFieldPaths=config-read-failed")
else:
    print(f"tokenFieldsAbsent={'YES' if not found else 'NO'}")
    print(f"tokenFieldPaths={';'.join(found) if found else 'none'}")
PY

  DISCORD_PUBLIC_ENV_ONLY_CONFIG_TOKEN_FIELDS_ABSENT="$(awk -F= '/^tokenFieldsAbsent=/{print $2}' "$parse_out" | head -n 1)"
  DISCORD_PUBLIC_ENV_ONLY_CONFIG_TOKEN_FIELD_PATHS="$(awk -F= '/^tokenFieldPaths=/{print $2}' "$parse_out" | head -n 1)"
  [[ -n "$DISCORD_PUBLIC_ENV_ONLY_CONFIG_TOKEN_FIELDS_ABSENT" ]] || DISCORD_PUBLIC_ENV_ONLY_CONFIG_TOKEN_FIELDS_ABSENT="UNKNOWN"
  [[ -n "$DISCORD_PUBLIC_ENV_ONLY_CONFIG_TOKEN_FIELD_PATHS" ]] || DISCORD_PUBLIC_ENV_ONLY_CONFIG_TOKEN_FIELD_PATHS="UNKNOWN"
}

discord_public_env_only_readiness_gate() {
  local prefix="$1"
  local list_all_file="$LOG_DIR/openclaw_channels_list_all.${prefix}.txt"
  local list_file="$LOG_DIR/openclaw_channels_list.${prefix}.txt"
  local probe_file="$LOG_DIR/openclaw_channels_status_probe.${prefix}.txt"
  local systemd_env_file="$LOG_DIR/systemd_user_environment.${prefix}.txt"
  local line

  DISCORD_PUBLIC_ENV_ONLY_GATE_RESULT="FAIL"
  DISCORD_PUBLIC_ENV_ONLY_GATE_FAILURE_REASON="unknown"

  line="$(extract_discord_channel_line "$list_all_file")"
  if [[ -z "$line" ]]; then
    line="$(extract_discord_channel_line "$list_file")"
  fi
  DISCORD_PUBLIC_ENV_ONLY_LINE="${line:-UNKNOWN}"

  if discord_public_line_is_env_only_ready "$line"; then
    DISCORD_PUBLIC_ENV_ONLY_LINE_RESULT="PASS"
  else
    DISCORD_PUBLIC_ENV_ONLY_LINE_RESULT="FAIL"
    DISCORD_PUBLIC_ENV_ONLY_GATE_FAILURE_REASON="public-discord-line-not-installed-configured-enabled-token-env"
    write_discord_channel_markers
    return 1
  fi

  capture_discord_public_env_only_json_gate "$prefix"
  if [[ "$DISCORD_PUBLIC_ENV_ONLY_JSON_RESULT" != "PASS" ]]; then
    DISCORD_PUBLIC_ENV_ONLY_GATE_FAILURE_REASON="public-discord-json-not-installed-configured-default"
    write_discord_channel_markers
    return 1
  fi

  if grep -qi 'Gateway reachable' "$probe_file" 2>/dev/null; then
    DISCORD_PUBLIC_ENV_ONLY_GATEWAY_REACHABLE="YES"
  else
    DISCORD_PUBLIC_ENV_ONLY_GATEWAY_REACHABLE="NO"
    DISCORD_PUBLIC_ENV_ONLY_GATE_FAILURE_REASON="public-discord-gateway-probe-not-reachable"
    write_discord_channel_markers
    return 1
  fi

  if [[ "$DISCORD_SYSTEMD_ENV_TOKEN_PRESENT" == "YES" ]] && grep -Fq "${TOKEN_ENV}=<REDACTED>" "$systemd_env_file" 2>/dev/null; then
    DISCORD_PUBLIC_ENV_ONLY_SYSTEMD_TOKEN_REDACTED="YES"
  else
    DISCORD_PUBLIC_ENV_ONLY_SYSTEMD_TOKEN_REDACTED="NO"
    DISCORD_PUBLIC_ENV_ONLY_GATE_FAILURE_REASON="systemd-discord-token-not-present-redacted"
    write_discord_channel_markers
    return 1
  fi

  capture_discord_public_env_only_config_token_field_gate "$prefix"
  if [[ "$DISCORD_PUBLIC_ENV_ONLY_CONFIG_TOKEN_FIELDS_ABSENT" != "YES" ]]; then
    DISCORD_PUBLIC_ENV_ONLY_GATE_FAILURE_REASON="discord-token-field-persisted-in-config"
    write_discord_channel_markers
    return 1
  fi

  if [[ "$DISCORD_TOKEN_VALUE_LOGGED" != "NO" ]]; then
    DISCORD_PUBLIC_ENV_ONLY_GATE_FAILURE_REASON="discord-token-value-logged-marker-not-no"
    write_discord_channel_markers
    return 1
  fi

  if [[ "$DISCORD_TOKEN_DURABLE_EXPOSURE" != "NO" || "$DISCORD_TOKEN_INSTALL_CONFIG_VALUE_STORED" != "NO" ]]; then
    DISCORD_PUBLIC_ENV_ONLY_GATE_FAILURE_REASON="discord-token-durable-exposure-marker-not-no"
    write_discord_channel_markers
    return 1
  fi

  DISCORD_PUBLIC_ENV_ONLY_GATE_RESULT="PASS"
  DISCORD_PUBLIC_ENV_ONLY_GATE_FAILURE_REASON="none"
  write_discord_channel_markers
  return 0
}

capture_discord_loaded_adapter_proof() {
  local outfile="$LOG_DIR/discord_loaded_adapter_proof.json"
  local parse_out="$LOG_DIR/discord_loaded_adapter_proof.markers"
  local dist_dir=""

  DISCORD_LOADED_ADAPTER_PROOF_ATTEMPTED="YES"
  DISCORD_LOADED_ADAPTER_PROOF_RESULT="FAIL"
  DISCORD_LOADED_ADAPTER_PROOF_FAILURE_REASON="unknown"
  DISCORD_PUBLIC_STATUS_ACCOUNTS_COUNT="$DISCORD_ACCOUNTS_JSON_COUNT"

  if [[ -d "$HOME/.openclaw/npm/projects" ]]; then
    dist_dir="$(find "$HOME/.openclaw/npm/projects" -path '*/node_modules/@openclaw/discord/dist' -type d 2>/dev/null | sort | tail -n 1 || true)"
  fi
  if [[ -z "$dist_dir" || ! -f "$dist_dir/index.js" ]]; then
    DISCORD_LOADED_ADAPTER_PROOF_FAILURE_REASON="discord-plugin-dist-not-found"
    write_discord_channel_markers
    return 1
  fi

  log "Capturing Discord loaded adapter proof"
  if ! DISCORD_PLUGIN_DIST="$dist_dir" DISCORD_BOT_TOKEN="$TOKEN_VALUE" node --input-type=module > "$outfile" <<'NODE'
import fs from "node:fs";
import { pathToFileURL } from "node:url";

function clone(value) {
  return JSON.parse(JSON.stringify(value ?? {}));
}

function normalizeStatus(account) {
  const raw = account?.tokenStatus;
  if (raw === "available" || raw === "configured_unavailable" || raw === "missing") return raw;
  if (typeof account?.token === "string" && account.token.length > 0) return "available";
  return "missing";
}

async function summarize(plugin, cfg) {
  const ids = plugin.config?.listAccountIds?.(cfg) ?? [];
  const defaultAccountId = plugin.config?.defaultAccountId?.(cfg) ?? "UNKNOWN";
  const account = plugin.config?.resolveAccount?.(cfg, "default");
  let configured = false;
  if (plugin.config?.isConfigured) configured = Boolean(await plugin.config.isConfigured(account, cfg));
  else configured = Boolean(account?.configured || account?.token);
  return {
    ids,
    defaultAccountId,
    configured,
    tokenSource: account?.tokenSource ?? "UNKNOWN",
    tokenStatus: normalizeStatus(account),
    tokenStatusEvidence: normalizeStatus(account)
  };
}

const dist = process.env.DISCORD_PLUGIN_DIST;
const cfgPath = `${process.env.HOME}/.openclaw/openclaw.json`;
const cfg = fs.existsSync(cfgPath) ? JSON.parse(fs.readFileSync(cfgPath, "utf8")) : {};
const currentDiscord = clone(cfg.channels?.discord);
const safeTopLevelToken = currentDiscord.token && typeof currentDiscord.token === "object" ? currentDiscord.token : undefined;
const entryModule = await import(pathToFileURL(`${dist}/index.js`).href);
const entry = entryModule.default ?? entryModule;
const plugin = await entry.loadChannelPlugin();

const baseChannels = clone(cfg.channels);
const scenarios = {
  current: cfg,
  envOnlyNoToken: {
    ...clone(cfg),
    channels: {
      ...baseChannels,
      discord: { enabled: true }
    }
  },
  explicitDefaultEnabledNoToken: {
    ...clone(cfg),
    channels: {
      ...baseChannels,
      discord: { enabled: true, accounts: { default: { enabled: true } } }
    }
  },
  explicitDefaultPolicyNoToken: {
    ...clone(cfg),
    channels: {
      ...baseChannels,
      discord: {
        enabled: true,
        name: "Discord",
        groupPolicy: "allowlist",
        allowFrom: Array.isArray(currentDiscord.allowFrom) ? currentDiscord.allowFrom.map(String) : [],
        accounts: { default: { enabled: true, name: "Discord" } }
      }
    }
  },
  topLevelSecretRefIfPresent: {
    ...clone(cfg),
    channels: {
      ...baseChannels,
      discord: { enabled: true, ...(safeTopLevelToken ? { token: safeTopLevelToken } : {}) }
    }
  }
};

const result = {
  descriptorLoaded: Boolean(entry?.loadChannelPlugin),
  loadedPluginHasConfig: Boolean(plugin?.config),
  configKeys: Object.keys(plugin?.config ?? {}).sort(),
  scenarios: {}
};
for (const [name, scenarioCfg] of Object.entries(scenarios)) {
  result.scenarios[name] = await summarize(plugin, scenarioCfg);
}
console.log(JSON.stringify(result, null, 2));
NODE
  then
    DISCORD_LOADED_ADAPTER_PROOF_FAILURE_REASON="node-loaded-adapter-proof-failed"
    write_discord_channel_markers
    return 1
  fi

  python3 - "$outfile" > "$parse_out" <<'PY' 2>/dev/null || true
import json, sys
path = sys.argv[1]
try:
    doc = json.load(open(path, encoding="utf-8"))
except Exception:
    print("result=FAIL")
    print("reason=adapter-proof-json-parse-failed")
    raise SystemExit(0)

def scenario(name):
    value = (doc.get("scenarios") or {}).get(name) or {}
    ids = value.get("ids")
    ids_s = ",".join(str(item) for item in ids) if isinstance(ids, list) and ids else "UNKNOWN"
    configured = "YES" if value.get("configured") is True else "NO" if value.get("configured") is False else "UNKNOWN"
    return {
        "ids": ids_s,
        "default": str(value.get("defaultAccountId") or "UNKNOWN"),
        "configured": configured,
        "tokenSource": str(value.get("tokenSource") or "UNKNOWN"),
        "tokenStatus": str(value.get("tokenStatus") or "UNKNOWN"),
        "tokenLength": "NOT_REPORTED",
    }

env = scenario("envOnlyNoToken")
explicit = scenario("explicitDefaultEnabledNoToken")
ok = (
    doc.get("descriptorLoaded") is True and
    doc.get("loadedPluginHasConfig") is True and
    env["ids"] != "UNKNOWN" and
    env["default"] == "default" and
    env["configured"] == "YES" and
    env["tokenSource"] == "env" and
    env["tokenStatus"] == "available"
)
print(f"result={'PASS' if ok else 'FAIL'}")
print(f"reason={'none' if ok else 'env-only-loaded-adapter-not-configured'}")
print(f"idsEnvOnly={env['ids']}")
print(f"defaultEnvOnly={env['default']}")
print(f"configuredEnvOnly={env['configured']}")
print(f"tokenSourceEnvOnly={env['tokenSource']}")
print(f"tokenStatusEnvOnly={env['tokenStatus']}")
print("tokenLengthEnvOnly=NOT_REPORTED")
print(f"idsExplicitDefault={explicit['ids']}")
print(f"configuredExplicitDefault={explicit['configured']}")
PY

  DISCORD_LOADED_ADAPTER_PROOF_RESULT="$(awk -F= '/^result=/{print $2}' "$parse_out" | head -n 1)"
  DISCORD_LOADED_ADAPTER_PROOF_FAILURE_REASON="$(awk -F= '/^reason=/{print $2}' "$parse_out" | head -n 1)"
  DISCORD_LOADED_ADAPTER_IDS_ENV_ONLY="$(awk -F= '/^idsEnvOnly=/{print $2}' "$parse_out" | head -n 1)"
  DISCORD_LOADED_ADAPTER_DEFAULT_ACCOUNT_ID_ENV_ONLY="$(awk -F= '/^defaultEnvOnly=/{print $2}' "$parse_out" | head -n 1)"
  DISCORD_LOADED_ADAPTER_CONFIGURED_ENV_ONLY="$(awk -F= '/^configuredEnvOnly=/{print $2}' "$parse_out" | head -n 1)"
  DISCORD_LOADED_ADAPTER_TOKEN_SOURCE_ENV_ONLY="$(awk -F= '/^tokenSourceEnvOnly=/{print $2}' "$parse_out" | head -n 1)"
  DISCORD_LOADED_ADAPTER_TOKEN_STATUS_ENV_ONLY="$(awk -F= '/^tokenStatusEnvOnly=/{print $2}' "$parse_out" | head -n 1)"
  DISCORD_LOADED_ADAPTER_TOKEN_LENGTH_ENV_ONLY="$(awk -F= '/^tokenLengthEnvOnly=/{print $2}' "$parse_out" | head -n 1)"
  DISCORD_LOADED_ADAPTER_IDS_EXPLICIT_DEFAULT="$(awk -F= '/^idsExplicitDefault=/{print $2}' "$parse_out" | head -n 1)"
  DISCORD_LOADED_ADAPTER_CONFIGURED_EXPLICIT_DEFAULT="$(awk -F= '/^configuredExplicitDefault=/{print $2}' "$parse_out" | head -n 1)"
  [[ -n "$DISCORD_LOADED_ADAPTER_PROOF_RESULT" ]] || DISCORD_LOADED_ADAPTER_PROOF_RESULT="FAIL"
  [[ -n "$DISCORD_LOADED_ADAPTER_PROOF_FAILURE_REASON" ]] || DISCORD_LOADED_ADAPTER_PROOF_FAILURE_REASON="adapter-proof-parse-failed"

  if [[ "$DISCORD_LOADED_ADAPTER_PROOF_RESULT" == "PASS" ]] && \
     ! discord_state_is_authoritative_pass "${DISCORD_CHANNEL_INSTALLED}|${DISCORD_CHANNEL_CONFIGURED}|${DISCORD_CHANNEL_ENABLED}"; then
    DISCORD_STATUS_LAYER_LAZY_PLUGIN_BUG_SUSPECTED="YES"
    DISCORD_FAILURE_CLASS="status-layer-lazy-plugin-account-drop"
    DISCORD_CHANNEL_CONFIG_RESULT="FAIL"
    DISCORD_CHANNEL_ACTIVATION_RESULT="FAIL"
    DISCORD_CONFIG_RESULT="FAIL"
  elif [[ "$DISCORD_LOADED_ADAPTER_PROOF_RESULT" == "PASS" ]]; then
    DISCORD_STATUS_LAYER_LAZY_PLUGIN_BUG_SUSPECTED="NO"
    DISCORD_FAILURE_CLASS="none"
  elif [[ "$DISCORD_LOADED_ADAPTER_TOKEN_STATUS_ENV_ONLY" == "missing" || "$DISCORD_LOADED_ADAPTER_TOKEN_STATUS_ENV_ONLY" == "configured_unavailable" ]]; then
    DISCORD_STATUS_LAYER_LAZY_PLUGIN_BUG_SUSPECTED="NO"
    DISCORD_FAILURE_CLASS="token-unavailable"
  elif [[ "$DISCORD_LOADED_ADAPTER_IDS_ENV_ONLY" == "UNKNOWN" ]]; then
    DISCORD_STATUS_LAYER_LAZY_PLUGIN_BUG_SUSPECTED="NO"
    DISCORD_FAILURE_CLASS="config-shape"
  else
    DISCORD_STATUS_LAYER_LAZY_PLUGIN_BUG_SUSPECTED="NO"
    DISCORD_FAILURE_CLASS="unknown"
  fi
  write_discord_channel_markers
  [[ "$DISCORD_LOADED_ADAPTER_PROOF_RESULT" == "PASS" ]]
}

derive_discord_allow_from_json() {
  python3 - "$OWNER_ID" <<'PY' 2>/dev/null || printf '["%s"]\n' "$OWNER_ID"
import json, os, sys
owner = sys.argv[1]
path = os.path.expanduser("~/.openclaw/openclaw.json")
entries = []
try:
    doc = json.load(open(path, encoding="utf-8"))
    raw = (((doc.get("channels") or {}).get("discord") or {}).get("allowFrom") or [])
    if isinstance(raw, list):
        entries = [str(item) for item in raw if str(item)]
except Exception:
    entries = []
if owner not in entries:
    entries.append(owner)
print(json.dumps(entries))
PY
}

capture_gateway_discord_env_proof() {
  local outfile="$LOG_DIR/openclaw_gateway_discord_env.after_env_only_implicit_default.txt"
  local pid
  pid="$(systemctl --user show openclaw-gateway.service -p MainPID --value 2>/dev/null || true)"
  python3 - "$pid" "$TOKEN_ENV" > "$outfile" <<'PY' 2>/dev/null || true
import os, sys
pid, name = sys.argv[1], sys.argv[2]
present = "NO"
length = "UNKNOWN"
try:
    if pid and pid != "0":
        data = open(f"/proc/{pid}/environ", "rb").read().split(b"\0")
        prefix = (name + "=").encode()
        for item in data:
            if item.startswith(prefix):
                value = item[len(prefix):]
                present = "YES"
                length = "NOT_REPORTED"
                break
except Exception:
    pass
print(f"pid={pid or 'UNKNOWN'}")
print(f"{name}=<REDACTED>")
print(f"present={present}")
print(f"length={length}")
PY
  DISCORD_GATEWAY_ENV_TOKEN_PRESENT="$(sed -n 's/^present=//p' "$outfile" | head -n 1)"
  DISCORD_GATEWAY_ENV_TOKEN_LENGTH="$(sed -n 's/^length=//p' "$outfile" | head -n 1)"
  [[ -n "$DISCORD_GATEWAY_ENV_TOKEN_PRESENT" ]] || DISCORD_GATEWAY_ENV_TOKEN_PRESENT="UNKNOWN"
  [[ -n "$DISCORD_GATEWAY_ENV_TOKEN_LENGTH" ]] || DISCORD_GATEWAY_ENV_TOKEN_LENGTH="UNKNOWN"
  cat "$outfile"
}

detect_discord_inactive_surface_warning() {
  local prefix="$1"
  if grep -qiE 'SECRETS_REF_IGNORED_INACTIVE_SURFACE|inactive[- ]surface|no enabled account inherits this top-level Discord token' \
    "$LOG_DIR/openclaw_gateway_journal.${prefix}.txt" \
    "$LOG_DIR/openclaw_channels_status_probe.${prefix}.txt" \
    "$LOG_DIR/openclaw_channels_list_all_json.${prefix}.txt" 2>/dev/null; then
    DISCORD_INACTIVE_SURFACE_WARNING_SEEN="YES"
  else
    DISCORD_INACTIVE_SURFACE_WARNING_SEEN="NO"
  fi
}


ensure_discord_plugin_entry_runtime_gate() {
  DISCORD_PLUGIN_ENTRY_GATE_ATTEMPTED="YES"
  DISCORD_PLUGIN_ENTRY_GATE_RESULT="UNKNOWN"
  DISCORD_PLUGIN_ENTRY_GATE_FAILURE_REASON="unknown"
  DISCORD_PLUGIN_ENTRY_KEYS="UNKNOWN"
  DISCORD_PLUGIN_ENTRY_DISCORD_PRESENT="UNKNOWN"
  DISCORD_PLUGIN_ENTRY_DISCORD_ENABLED="UNKNOWN"
  DISCORD_PLUGIN_ENTRY_CONFIG_VALIDATE_RESULT="UNKNOWN"

  local config_path="${HOME}/.openclaw/openclaw.json"
  local proof_file="$LOG_DIR/openclaw_plugin_entry_runtime_gate.txt"
  mkdir -p "$(dirname "$config_path")"

  if python3 - "$config_path" "$proof_file" <<'PY'
import json, os, sys, tempfile
config_path, proof_file = sys.argv[1], sys.argv[2]

def write_proof(**items):
    with open(proof_file, "w", encoding="utf-8") as f:
        for key, value in items.items():
            f.write(f"{key}={value}\n")

def fail(reason):
    write_proof(
        PLUGIN_ENTRY_GATE_RESULT="FAIL",
        PLUGIN_ENTRY_GATE_FAILURE_REASON=reason,
        PLUGIN_ENTRY_KEYS="UNKNOWN",
        PLUGIN_ENTRY_DISCORD_PRESENT="UNKNOWN",
        PLUGIN_ENTRY_DISCORD_ENABLED="UNKNOWN",
    )
    raise SystemExit(1)

if os.path.exists(config_path):
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        fail("invalid-openclaw-json")
else:
    data = {}

if not isinstance(data, dict):
    fail("root-non-object")

plugins = data.get("plugins")
if plugins is None:
    plugins = {}
elif not isinstance(plugins, dict):
    fail("plugins-non-object")
data["plugins"] = plugins

entries = plugins.get("entries")
if entries is None:
    entries = {}
elif not isinstance(entries, dict):
    fail("plugins-entries-non-object")
plugins["entries"] = entries

discord = entries.get("discord")
if discord is None:
    discord = {}
elif not isinstance(discord, dict):
    fail("plugins-entries-discord-non-object")
entries["discord"] = discord
discord["enabled"] = True

parent = os.path.dirname(config_path) or "."
fd, tmp_path = tempfile.mkstemp(prefix="openclaw.json.", suffix=".tmp", dir=parent, text=True)
try:
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(tmp_path, config_path)
finally:
    try:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
    except Exception:
        pass

keys = ",".join(sorted(str(k) for k in entries.keys()))
write_proof(
    PLUGIN_ENTRY_GATE_RESULT="PASS",
    PLUGIN_ENTRY_GATE_FAILURE_REASON="none",
    PLUGIN_ENTRY_KEYS=keys,
    PLUGIN_ENTRY_DISCORD_PRESENT="YES",
    PLUGIN_ENTRY_DISCORD_ENABLED="True",
)
PY
  then
    DISCORD_PLUGIN_ENTRY_GATE_RESULT="$(sed -n 's/^PLUGIN_ENTRY_GATE_RESULT=//p' "$proof_file" | head -n 1)"
    DISCORD_PLUGIN_ENTRY_GATE_FAILURE_REASON="$(sed -n 's/^PLUGIN_ENTRY_GATE_FAILURE_REASON=//p' "$proof_file" | head -n 1)"
    DISCORD_PLUGIN_ENTRY_KEYS="$(sed -n 's/^PLUGIN_ENTRY_KEYS=//p' "$proof_file" | head -n 1)"
    DISCORD_PLUGIN_ENTRY_DISCORD_PRESENT="$(sed -n 's/^PLUGIN_ENTRY_DISCORD_PRESENT=//p' "$proof_file" | head -n 1)"
    DISCORD_PLUGIN_ENTRY_DISCORD_ENABLED="$(sed -n 's/^PLUGIN_ENTRY_DISCORD_ENABLED=//p' "$proof_file" | head -n 1)"
  else
    DISCORD_PLUGIN_ENTRY_GATE_RESULT="$(sed -n 's/^PLUGIN_ENTRY_GATE_RESULT=//p' "$proof_file" 2>/dev/null | head -n 1)"
    DISCORD_PLUGIN_ENTRY_GATE_FAILURE_REASON="$(sed -n 's/^PLUGIN_ENTRY_GATE_FAILURE_REASON=//p' "$proof_file" 2>/dev/null | head -n 1)"
    DISCORD_PLUGIN_ENTRY_KEYS="$(sed -n 's/^PLUGIN_ENTRY_KEYS=//p' "$proof_file" 2>/dev/null | head -n 1)"
    DISCORD_PLUGIN_ENTRY_DISCORD_PRESENT="$(sed -n 's/^PLUGIN_ENTRY_DISCORD_PRESENT=//p' "$proof_file" 2>/dev/null | head -n 1)"
    DISCORD_PLUGIN_ENTRY_DISCORD_ENABLED="$(sed -n 's/^PLUGIN_ENTRY_DISCORD_ENABLED=//p' "$proof_file" 2>/dev/null | head -n 1)"
    [[ -n "$DISCORD_PLUGIN_ENTRY_GATE_RESULT" ]] || DISCORD_PLUGIN_ENTRY_GATE_RESULT="FAIL"
    [[ -n "$DISCORD_PLUGIN_ENTRY_GATE_FAILURE_REASON" ]] || DISCORD_PLUGIN_ENTRY_GATE_FAILURE_REASON="plugin-entry-gate-python-failed"
    return 1
  fi

  [[ -n "$DISCORD_PLUGIN_ENTRY_GATE_RESULT" ]] || DISCORD_PLUGIN_ENTRY_GATE_RESULT="UNKNOWN"
  [[ -n "$DISCORD_PLUGIN_ENTRY_GATE_FAILURE_REASON" ]] || DISCORD_PLUGIN_ENTRY_GATE_FAILURE_REASON="unknown"
  [[ -n "$DISCORD_PLUGIN_ENTRY_KEYS" ]] || DISCORD_PLUGIN_ENTRY_KEYS="UNKNOWN"
  [[ -n "$DISCORD_PLUGIN_ENTRY_DISCORD_PRESENT" ]] || DISCORD_PLUGIN_ENTRY_DISCORD_PRESENT="UNKNOWN"
  [[ -n "$DISCORD_PLUGIN_ENTRY_DISCORD_ENABLED" ]] || DISCORD_PLUGIN_ENTRY_DISCORD_ENABLED="UNKNOWN"

  if run_capture "OpenClaw config validate after Discord plugin-entry runtime gate" "$LOG_DIR/openclaw_config_validate.after_discord_plugin_entry_gate.txt" openclaw config validate; then
    DISCORD_PLUGIN_ENTRY_CONFIG_VALIDATE_RESULT="PASS"
  else
    DISCORD_PLUGIN_ENTRY_CONFIG_VALIDATE_RESULT="FAIL"
    DISCORD_PLUGIN_ENTRY_GATE_RESULT="FAIL"
    DISCORD_PLUGIN_ENTRY_GATE_FAILURE_REASON="config-validation-failed-after-plugin-entry-gate"
    return 1
  fi

  [[ "$DISCORD_PLUGIN_ENTRY_GATE_RESULT" == "PASS" ]]
}

evaluate_discord_deep_status_gate() {
  local prefix="$1"
  local file="$LOG_DIR/openclaw_status_deep.${prefix}.txt"

  DISCORD_DEEP_STATUS_HAS_DISCORD="UNKNOWN"
  DISCORD_DEEP_STATUS_NO_CHANNELS_CONFIGURED="UNKNOWN"
  DISCORD_DEEP_STATUS_GATE_RESULT="UNKNOWN"
  DISCORD_DEEP_STATUS_GATE_FAILURE_REASON="unknown"

  if [[ ! -f "$file" ]]; then
    DISCORD_DEEP_STATUS_GATE_RESULT="FAIL"
    DISCORD_DEEP_STATUS_GATE_FAILURE_REASON="deep-status-output-missing"
    return 1
  fi

  if grep -qi 'discord' "$file"; then
    DISCORD_DEEP_STATUS_HAS_DISCORD="YES"
  else
    DISCORD_DEEP_STATUS_HAS_DISCORD="NO"
  fi

  if grep -qi 'No channels configured' "$file"; then
    DISCORD_DEEP_STATUS_NO_CHANNELS_CONFIGURED="YES"
  else
    DISCORD_DEEP_STATUS_NO_CHANNELS_CONFIGURED="NO"
  fi

  if [[ "$DISCORD_DEEP_STATUS_HAS_DISCORD" == "YES" && "$DISCORD_DEEP_STATUS_NO_CHANNELS_CONFIGURED" == "NO" ]]; then
    DISCORD_DEEP_STATUS_GATE_RESULT="PASS"
    DISCORD_DEEP_STATUS_GATE_FAILURE_REASON="none"
    return 0
  fi

  DISCORD_DEEP_STATUS_GATE_RESULT="FAIL"
  if [[ "$DISCORD_DEEP_STATUS_HAS_DISCORD" != "YES" ]]; then
    DISCORD_DEEP_STATUS_GATE_FAILURE_REASON="deep-status-discord-missing"
  elif [[ "$DISCORD_DEEP_STATUS_NO_CHANNELS_CONFIGURED" == "YES" ]]; then
    DISCORD_DEEP_STATUS_GATE_FAILURE_REASON="deep-status-no-channels-configured"
  else
    DISCORD_DEEP_STATUS_GATE_FAILURE_REASON="deep-status-unknown-failure"
  fi
  return 1
}

run_discord_env_only_implicit_default_contract() {
  DISCORD_SETUP_METHOD="env-only-implicit-default"
  DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_ATTEMPTED="YES"
  DISCORD_SECRETREF_CONFIG_ATTEMPTED="NO"
  DISCORD_SECRETREF_CONFIG_RESULT="NOT_USED"
  DISCORD_SECRETREF_CONFIG_FAILURE_REASON="env-only-implicit-default"
  DISCORD_ACCOUNT_SCOPED_CONFIG_ATTEMPTED="NO"
  DISCORD_ACCOUNT_SCOPED_CONFIG_RESULT="NOT_USED"
  DISCORD_ACCOUNT_SCOPED_CONFIG_FAILURE_REASON="env-only-implicit-default"
  DISCORD_ACCOUNT_SCOPED_TOKEN_RESULT="NOT_USED"
  DISCORD_ACCOUNT_SCOPED_ENABLED_RESULT="NOT_USED"
  DISCORD_NATIVE_CHANNEL_ADD_ATTEMPTED="YES"
  DISCORD_NATIVE_CHANNEL_ADD_METHODS_TRIED="env-only-implicit-default"
  DISCORD_NATIVE_CHANNEL_ADD_FINAL_METHOD="env-only-implicit-default"
  write_discord_channel_markers

  run_capture "OpenClaw config unset channels.discord.token for env-only implicit default" "$LOG_DIR/openclaw_config_unset.discord_token.txt" \
    openclaw config unset channels.discord.token || true
  if grep -q 'Removed channels.discord.token' "$LOG_DIR/openclaw_config_unset.discord_token.txt"; then
    DISCORD_TOP_LEVEL_TOKEN_REMOVED_FOR_ENV_ONLY="YES"
  else
    DISCORD_TOP_LEVEL_TOKEN_REMOVED_FOR_ENV_ONLY="NO"
  fi

  run_capture "OpenClaw config unset channels.discord.accounts.default.token for env-only implicit default" "$LOG_DIR/openclaw_config_unset.discord_accounts_default_token.txt" \
    openclaw config unset channels.discord.accounts.default.token || true
  if grep -q 'Removed channels.discord.accounts.default.token' "$LOG_DIR/openclaw_config_unset.discord_accounts_default_token.txt"; then
    DISCORD_ACCOUNT_SCOPED_TOKEN_REMOVED_FOR_ENV_ONLY="YES"
  else
    DISCORD_ACCOUNT_SCOPED_TOKEN_REMOVED_FOR_ENV_ONLY="NO"
  fi

  if ! systemctl --user show-environment 2>/dev/null | grep -q "^${TOKEN_ENV}="; then
    DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_RESULT="FAIL"
    DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_FAILURE_REASON="systemd-user-env-missing-discord-token"
    DISCORD_NATIVE_CHANNEL_ADD_COMMAND_RESULT="FAIL"
    DISCORD_NATIVE_CHANNEL_ADD_STATE_RESULT="FAIL"
    DISCORD_NATIVE_CHANNEL_ADD_RESULT="FAIL"
    DISCORD_NATIVE_CHANNEL_ADD_FAILURE_REASON="$DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_FAILURE_REASON"
    DISCORD_CHANNEL_CONFIG_RESULT="FAIL"
    DISCORD_CHANNEL_ACTIVATION_RESULT="FAIL"
    DISCORD_CONFIG_RESULT="FAIL"
    DISCORD_CONFIG_FAILURE_REASON="$DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_FAILURE_REASON"
    write_discord_channel_markers
    return 1
  fi

  local allow_from_json
  allow_from_json="$(derive_discord_allow_from_json)"

  run_capture "OpenClaw config set channels.discord.enabled true" "$LOG_DIR/openclaw_config_set.discord_enabled.txt" \
    openclaw config set channels.discord.enabled true --strict-json || true
  if grep -q 'Updated channels.discord.enabled' "$LOG_DIR/openclaw_config_set.discord_enabled.txt"; then
    DISCORD_ENABLED_CONFIG_RESULT="PASS"
  else
    DISCORD_ENABLED_CONFIG_RESULT="FAIL"
    DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_RESULT="FAIL"
    DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_FAILURE_REASON="channels-discord-enabled-config-failed"
    DISCORD_NATIVE_CHANNEL_ADD_COMMAND_RESULT="FAIL"
    DISCORD_NATIVE_CHANNEL_ADD_STATE_RESULT="FAIL"
    DISCORD_NATIVE_CHANNEL_ADD_RESULT="FAIL"
    DISCORD_NATIVE_CHANNEL_ADD_FAILURE_REASON="$DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_FAILURE_REASON"
    DISCORD_CHANNEL_CONFIG_RESULT="FAIL"
    DISCORD_CHANNEL_ACTIVATION_RESULT="FAIL"
    DISCORD_CONFIG_RESULT="FAIL"
    DISCORD_CONFIG_FAILURE_REASON="$DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_FAILURE_REASON"
    write_discord_channel_markers
    return 1
  fi

  run_capture "OpenClaw config set channels.discord.groupPolicy allowlist" "$LOG_DIR/openclaw_config_set.discord_group_policy.txt" \
    openclaw config set channels.discord.groupPolicy '"allowlist"' --strict-json || true
  run_capture "OpenClaw config set channels.discord.allowFrom owner" "$LOG_DIR/openclaw_config_set.discord_allow_from.txt" \
    openclaw config set channels.discord.allowFrom "$allow_from_json" --strict-json || true
  run_capture "OpenClaw config set channels.discord.name Discord" "$LOG_DIR/openclaw_config_set.discord_name.txt" \
    openclaw config set channels.discord.name '"Discord"' --strict-json || true

  if ! ensure_discord_plugin_entry_runtime_gate; then
    DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_RESULT="FAIL"
    DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_FAILURE_REASON="$DISCORD_PLUGIN_ENTRY_GATE_FAILURE_REASON"
    DISCORD_NATIVE_CHANNEL_ADD_COMMAND_RESULT="FAIL"
    DISCORD_NATIVE_CHANNEL_ADD_STATE_RESULT="FAIL"
    DISCORD_NATIVE_CHANNEL_ADD_RESULT="FAIL"
    DISCORD_NATIVE_CHANNEL_ADD_FAILURE_REASON="$DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_FAILURE_REASON"
    DISCORD_CHANNEL_CONFIG_RESULT="FAIL"
    DISCORD_CHANNEL_ACTIVATION_RESULT="FAIL"
    DISCORD_CONFIG_RESULT="FAIL"
    DISCORD_CONFIG_FAILURE_REASON="$DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_FAILURE_REASON"
    write_discord_channel_markers
    return 1
  fi

  DISCORD_NATIVE_CHANNEL_ADD_COMMAND_RESULT="PASS"
  DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_FAILURE_REASON="none"
  capture_redacted_discord_config_snapshot "after_env_only_implicit_default_write"
  run_shell_capture "OpenClaw config get channels.discord --json after env-only implicit default" "$LOG_DIR/openclaw_config_get.discord.after_env_only_implicit_default.redacted.json" \
    "openclaw config get channels.discord --json | python3 -c 'import json,sys; data=json.load(sys.stdin); print(json.dumps(data, indent=2, sort_keys=True))' | sed -E 's/(\"[^\" ]*(token|secret|password|key)[^\" ]*\"[[:space:]]*:[[:space:]]*)\"[^\"]*\"/\\1\"<REDACTED>\"/Ig' || true"

  restart_openclaw_gateway
  RESTART_SINCE="$(systemctl --user show openclaw-gateway.service -p ActiveEnterTimestamp --value || date '+%Y-%m-%d %H:%M:%S')"
  capture_gateway_discord_env_proof
  capture_discord_state_files "after_env_only_implicit_default"
  evaluate_discord_deep_status_gate "after_env_only_implicit_default" || true
  detect_discord_gateway_provider_startup "after_env_only_implicit_default"
  DISCORD_CLI_ENV_INJECTED_ACCOUNTS_JSON_COUNT="$(count_discord_accounts_from_json_capture "$LOG_DIR/openclaw_channels_list_all_json.after_env_only_implicit_default.txt")"
  DISCORD_ACCOUNTS_JSON_COUNT="$DISCORD_CLI_ENV_INJECTED_ACCOUNTS_JSON_COUNT"
  detect_discord_inactive_surface_warning "after_env_only_implicit_default"
  DISCORD_LINE_AFTER_ENV_ONLY_IMPLICIT_DEFAULT="$(extract_discord_channel_line "$LOG_DIR/openclaw_channels_list_all.after_env_only_implicit_default.txt")"
  if [[ -z "$DISCORD_LINE_AFTER_ENV_ONLY_IMPLICIT_DEFAULT" ]]; then
    DISCORD_LINE_AFTER_ENV_ONLY_IMPLICIT_DEFAULT="$(extract_discord_channel_line "$LOG_DIR/openclaw_channels_list.after_env_only_implicit_default.txt")"
  fi
  DISCORD_CLI_ENV_INJECTED_LINE="$DISCORD_LINE_AFTER_ENV_ONLY_IMPLICIT_DEFAULT"
  DISCORD_LINE_AFTER_NATIVE_ADD="$DISCORD_LINE_AFTER_ENV_ONLY_IMPLICIT_DEFAULT"

  local state_summary
  state_summary="$(capture_discord_channel_state_summary "$LOG_DIR/openclaw_channels_list_all.after_env_only_implicit_default.txt")"
  if [[ "$state_summary" == "unknown|unknown|unknown" ]]; then
    state_summary="$(capture_discord_channel_state_summary "$LOG_DIR/openclaw_channels_list.after_env_only_implicit_default.txt")"
  fi
  if [[ "$state_summary" != "unknown|unknown|unknown" ]]; then
    IFS='|' read -r DISCORD_CHANNEL_INSTALLED DISCORD_CHANNEL_CONFIGURED DISCORD_CHANNEL_ENABLED <<<"$state_summary"
    DISCORD_CHANNEL_STATE_AFTER_REPAIR="$state_summary"
  fi

  capture_discord_loaded_adapter_proof || true

  if discord_public_env_only_readiness_gate "after_env_only_implicit_default"; then
    if [[ "$DISCORD_DEEP_STATUS_GATE_RESULT" != "PASS" ]]; then
      DISCORD_NATIVE_CHANNEL_ADD_STATE_RESULT="FAIL"
      DISCORD_NATIVE_CHANNEL_ADD_RESULT="FAIL"
      DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_RESULT="FAIL"
      DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_FAILURE_REASON="$DISCORD_DEEP_STATUS_GATE_FAILURE_REASON"
      DISCORD_NATIVE_CHANNEL_ADD_FAILURE_REASON="$DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_FAILURE_REASON"
      DISCORD_CHANNEL_CONFIG_RESULT="FAIL"
      DISCORD_CHANNEL_ACTIVATION_RESULT="FAIL"
      DISCORD_CONFIG_RESULT="FAIL"
      DISCORD_CONFIG_FAILURE_REASON="$DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_FAILURE_REASON"
      write_discord_channel_markers
      return 1
    fi
    DISCORD_NATIVE_CHANNEL_ADD_STATE_RESULT="PASS"
    DISCORD_NATIVE_CHANNEL_ADD_RESULT="PASS"
    DISCORD_NATIVE_CHANNEL_ADD_FAILURE_REASON="none"
    DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_RESULT="PASS"
    DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_FAILURE_REASON="none"
    DISCORD_CHANNEL_CONFIG_RESULT="PASS"
    DISCORD_CHANNEL_ACTIVATION_RESULT="PASS"
    DISCORD_CONFIG_RESULT="PASS"
    DISCORD_CONFIG_FAILURE_REASON="none"
    DISCORD_ROLLBACK_DECISION="not-needed"
    DISCORD_ROLLBACK_REASON="public-env-only-discord-readiness-pass"
    DISCORD_ENV_ONLY_CONFIG_PRESERVED="YES"
    DISCORD_KNOWN_BAD_SECRETREF_RESTORE_SKIPPED="YES"
    DISCORD_LOADED_ADAPTER_PROOF_GATE_MODE="advisory-public-env-only-pass"
    if [[ "$DISCORD_LOADED_ADAPTER_PROOF_RESULT" == "PASS" ]]; then
      DISCORD_FAILURE_CLASS="none"
    else
      DISCORD_FAILURE_CLASS="public-env-only-pass-loaded-adapter-review"
    fi
    capture_post_failure_discord_config_shape "success"
    write_discord_channel_markers
    return 0
  fi

  DISCORD_NATIVE_CHANNEL_ADD_STATE_RESULT="FAIL"
  DISCORD_NATIVE_CHANNEL_ADD_RESULT="FAIL"
  DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_RESULT="FAIL"
  if [[ "$DISCORD_PUBLIC_ENV_ONLY_GATE_FAILURE_REASON" != "unknown" && "$DISCORD_PUBLIC_ENV_ONLY_GATE_FAILURE_REASON" != "none" ]]; then
    DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_FAILURE_REASON="$DISCORD_PUBLIC_ENV_ONLY_GATE_FAILURE_REASON"
  else
    DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_FAILURE_REASON="$(discord_state_failure_reason_for_summary "env-only-implicit-default" "${DISCORD_CHANNEL_INSTALLED}|${DISCORD_CHANNEL_CONFIGURED}|${DISCORD_CHANNEL_ENABLED}")"
  fi
  DISCORD_NATIVE_CHANNEL_ADD_FAILURE_REASON="$DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_FAILURE_REASON"
  DISCORD_CHANNEL_CONFIG_RESULT="FAIL"
  DISCORD_CHANNEL_ACTIVATION_RESULT="FAIL"
  DISCORD_CONFIG_RESULT="FAIL"
  DISCORD_CONFIG_FAILURE_REASON="$DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_FAILURE_REASON"
  write_discord_channel_markers
  return 1
}

RESTART_SINCE="$(date '+%Y-%m-%d %H:%M:%S')"
run_shell_capture "OpenClaw doctor --help" "$LOG_DIR/openclaw_doctor_help.txt" openclaw doctor --help || true
capture_discord_state_files "before_repair"
refresh_discord_state "before_repair" || true

if [[ "$DISCORD_CHANNEL_INSTALLED" == "not-installed" ]]; then
  DISCORD_REPAIR_ATTEMPTED="YES"
  DISCORD_REPAIR_METHOD="doctor-fix"
  DISCORD_REPAIR_RESULT="IN_PROGRESS"
  DISCORD_REPAIR_FAILURE_REASON="discord-channel-not-installed"
  write_discord_channel_markers
  log "Discord channel is not installed; running openclaw doctor --fix"
  run_capture "OpenClaw doctor --fix" "$LOG_DIR/openclaw_doctor_fix.txt" openclaw doctor --fix || true
  restart_openclaw_gateway
  RESTART_SINCE="$(systemctl --user show openclaw-gateway.service -p ActiveEnterTimestamp --value || date '+%Y-%m-%d %H:%M:%S')"
  capture_discord_state_files "after_repair"
  refresh_discord_state "after_repair" || true
  if [[ "$DISCORD_CHANNEL_INSTALLED" == "not-installed" ]]; then
    DISCORD_REPAIR_RESULT="FAIL"
    DISCORD_REPAIR_FAILURE_REASON="discord-channel-still-not-installed-after-doctor-fix"
  else
    DISCORD_REPAIR_RESULT="PASS"
    DISCORD_REPAIR_FAILURE_REASON="none"
  fi
else
  DISCORD_REPAIR_ATTEMPTED="NO"
  DISCORD_REPAIR_METHOD="not-required"
  DISCORD_REPAIR_RESULT="PASS"
  DISCORD_REPAIR_FAILURE_REASON="none"
fi

if [[ "$DISCORD_REPAIR_RESULT" == "FAIL" ]]; then
  DISCORD_NATIVE_CHANNEL_ADD_RESULT="FAIL"
  DISCORD_CONFIG_RESULT="FAIL"
  DISCORD_CONFIG_FAILURE_REASON="$DISCORD_REPAIR_FAILURE_REASON"
  write_discord_channel_markers
  restore_openclaw_config_backup
  die "Discord plugin repair did not produce an installed channel state."
fi

if [[ "$NO_RESTART" != "1" ]]; then
  RESTART_SINCE="$(date '+%Y-%m-%d %H:%M:%S')"
fi

log "Capturing redacted OpenClaw config"
python3 - <<'PY' > "$RED_DIR/openclaw.redacted.json" 2>/dev/null || true
import json, os
p=os.path.expanduser("~/.openclaw/openclaw.json")
if not os.path.exists(p):
    print("{}")
    raise SystemExit(0)
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

run_capture "OpenClaw gateway status before Discord config" "$LOG_DIR/openclaw_gateway_status.before_native_add.txt" systemctl --user status openclaw-gateway.service --no-pager || true
run_shell_capture "OpenClaw gateway journal before Discord config" "$LOG_DIR/openclaw_gateway_journal.before_native_add.txt" \
  "journalctl --user -u openclaw-gateway.service --since '$RESTART_SINCE' --no-pager | grep -iE 'discord|gateway|plugin|ready|error|warn|owner|token|pair|channel|unknown|fail|login|connected|intent|unauthorized' || true"
run_openclaw_with_discord_env "OpenClaw channels list --all before Discord config" "$LOG_DIR/openclaw_channels_list_all.before_native_add.txt" channels list --all || true
run_openclaw_with_discord_env "OpenClaw channels list --all --json before Discord config" "$LOG_DIR/openclaw_channels_list_all_json.before_native_add.txt" channels list --all --json || true
run_openclaw_with_discord_env "OpenClaw channels list before Discord config" "$LOG_DIR/openclaw_channels_list.before_native_add.txt" channels list || true
run_openclaw_with_discord_env "OpenClaw channels status --probe before Discord config" "$LOG_DIR/openclaw_channels_status_probe.before_native_add.txt" channels status --probe || true
run_shell_capture "systemd user environment before Discord config redacted" "$LOG_DIR/systemd_user_environment.before_native_add.txt" \
  "systemctl --user show-environment | grep -E 'OLLAMA|OPENCLAW|DISCORD|CUDA' | sed -E 's/^([^=]*(TOKEN|SECRET|PASSWORD|KEY)[^=]*)=.*/\\1=<REDACTED>/I' || true"
DISCORD_LINE_BEFORE_NATIVE_ADD="$(extract_discord_channel_line "$LOG_DIR/openclaw_channels_list_all.before_native_add.txt")"
if [[ -z "$DISCORD_LINE_BEFORE_NATIVE_ADD" ]]; then
  DISCORD_LINE_BEFORE_NATIVE_ADD="$(extract_discord_channel_line "$LOG_DIR/openclaw_channels_list.before_native_add.txt")"
fi

log "Preparing Discord env-only implicit default config contract"
if [[ -f "$OPENCLAW_CONFIG_PATH" ]]; then
  log "Backed up existing OpenClaw config before Discord mutation: $OPENCLAW_CONFIG_BACKUP"
fi

DISCORD_NATIVE_CHANNEL_ADD_RESULT="FAIL"
DISCORD_NATIVE_CHANNEL_ADD_FAILURE_REASON="not-attempted"
DISCORD_SETUP_METHOD="env-only-implicit-default"
DISCORD_LINE_AFTER_USE_ENV="NOT_USED"
DISCORD_LINE_AFTER_TOKEN_FILE="NOT_SUPPORTED_FOR_DISCORD"
DISCORD_LINE_AFTER_BOT_TOKEN="NOT_SUPPORTED_FOR_DISCORD"

run_discord_env_only_implicit_default_contract || true

if [[ "$DISCORD_NATIVE_CHANNEL_ADD_RESULT" != "PASS" ]]; then
  handle_failed_discord_config_rollback
  DISCORD_CHANNEL_CONFIG_RESULT="FAIL"
  DISCORD_CHANNEL_ACTIVATION_RESULT="FAIL"
  DISCORD_CONFIG_RESULT="FAIL"
  DISCORD_CONFIG_FAILURE_REASON="${DISCORD_NATIVE_CHANNEL_ADD_FAILURE_REASON}"
  write_discord_channel_markers
  die "Discord env-only implicit default config did not produce an installed/configured/enabled Discord channel."
fi

DISCORD_CHANNEL_CONFIG_RESULT="PASS"
DISCORD_CHANNEL_ACTIVATION_RESULT="PASS"
DISCORD_CONFIG_RESULT="PASS"
DISCORD_CONFIG_FAILURE_REASON="none"
DISCORD_NATIVE_CHANNEL_ADD_STATE_RESULT="PASS"
if [[ "$DISCORD_LINE_AFTER_NATIVE_ADD" == "UNKNOWN" ]]; then
  DISCORD_LINE_AFTER_NATIVE_ADD="$(extract_discord_channel_line "$LOG_DIR/openclaw_channels_list_all.after_native_add.txt")"
fi
if [[ "$DISCORD_PUBLIC_ENV_ONLY_GATE_RESULT" != "PASS" ]] && \
   ! discord_state_is_authoritative_pass "${DISCORD_CHANNEL_INSTALLED}|${DISCORD_CHANNEL_CONFIGURED}|${DISCORD_CHANNEL_ENABLED}"; then
  DISCORD_NATIVE_CHANNEL_ADD_STATE_RESULT="FAIL"
  DISCORD_CHANNEL_CONFIG_RESULT="FAIL"
  DISCORD_CHANNEL_ACTIVATION_RESULT="FAIL"
  DISCORD_CONFIG_RESULT="FAIL"
  DISCORD_CONFIG_FAILURE_REASON="$(discord_state_failure_reason_for_summary "final" "${DISCORD_CHANNEL_INSTALLED}|${DISCORD_CHANNEL_CONFIGURED}|${DISCORD_CHANNEL_ENABLED}")"
  write_discord_channel_markers
  die "Discord authoritative channel state is not installed/configured/enabled after native add."
fi
write_discord_channel_markers

log "Writing report"
{
  echo "# OpenClaw Discord Configuration Report v1"
  echo
  echo "Created: $(date -Iseconds)"
  echo "Host: $(hostname)"
  echo "User: $(whoami)"
  echo "Owner: discord:$OWNER_ID"
  echo "Token env var: $TOKEN_ENV"
  echo "Token source: ${DISCORD_TOKEN_SOURCE}"
  echo "Token read result: ${DISCORD_TOKEN_READ_RESULT}"
  echo "Token value logged: ${DISCORD_TOKEN_VALUE_LOGGED}"
  echo "Runtime secret handling: ${DISCORD_RUNTIME_SECRET_HANDLING}"
  echo "Runtime secret persistence: ${DISCORD_RUNTIME_SECRET_PERSISTENCE}"
  echo "Durable token exposure: ${DISCORD_TOKEN_DURABLE_EXPOSURE}"
  echo "install_config token value stored: ${DISCORD_TOKEN_INSTALL_CONFIG_VALUE_STORED}"
  echo "Log directory: $LOG_DIR"
  echo
  echo "## Result"
  echo
  echo "- Discord channel state before repair: ${DISCORD_CHANNEL_STATE_BEFORE_REPAIR}"
  echo "- Discord repair attempted: ${DISCORD_REPAIR_ATTEMPTED}"
  echo "- Discord repair method: ${DISCORD_REPAIR_METHOD}"
  echo "- Discord repair result: ${DISCORD_REPAIR_RESULT}"
  echo "- Discord repair failure reason: ${DISCORD_REPAIR_FAILURE_REASON}"
  echo "- OpenClaw read-only external plugins patch result: ${OPENCLAW_READONLY_EXTERNAL_PLUGINS_PATCH_RESULT}"
  echo "- OpenClaw read-only external plugins patch proof: ${OPENCLAW_READONLY_EXTERNAL_PLUGINS_PATCH_PROOF}"
  echo "- Discord native channel add attempted: ${DISCORD_NATIVE_CHANNEL_ADD_ATTEMPTED}"
  echo "- Discord native channel add methods tried: ${DISCORD_NATIVE_CHANNEL_ADD_METHODS_TRIED}"
  echo "- Discord native channel add final method: ${DISCORD_NATIVE_CHANNEL_ADD_FINAL_METHOD}"
  echo "- Discord native channel add command result: ${DISCORD_NATIVE_CHANNEL_ADD_COMMAND_RESULT}"
  echo "- Discord native channel add state result: ${DISCORD_NATIVE_CHANNEL_ADD_STATE_RESULT}"
  echo "- Discord native channel add result: ${DISCORD_NATIVE_CHANNEL_ADD_RESULT}"
  echo "- Discord native channel add failure reason: ${DISCORD_NATIVE_CHANNEL_ADD_FAILURE_REASON}"
  echo "- Discord line before native add: ${DISCORD_LINE_BEFORE_NATIVE_ADD}"
  echo "- Discord line after use-env: ${DISCORD_LINE_AFTER_USE_ENV}"
  echo "- Discord line after token-file: ${DISCORD_LINE_AFTER_TOKEN_FILE}"
  echo "- Discord line after bot-token: ${DISCORD_LINE_AFTER_BOT_TOKEN}"
  echo "- Discord line after native add: ${DISCORD_LINE_AFTER_NATIVE_ADD}"
  echo "- Discord setup method: ${DISCORD_SETUP_METHOD}"
  echo "- Discord SecretRef config attempted: ${DISCORD_SECRETREF_CONFIG_ATTEMPTED}"
  echo "- Discord SecretRef config result: ${DISCORD_SECRETREF_CONFIG_RESULT}"
  echo "- Discord SecretRef config failure reason: ${DISCORD_SECRETREF_CONFIG_FAILURE_REASON}"
  echo "- Discord enabled config result: ${DISCORD_ENABLED_CONFIG_RESULT}"
  echo "- Discord account-scoped config attempted: ${DISCORD_ACCOUNT_SCOPED_CONFIG_ATTEMPTED}"
  echo "- Discord account-scoped config result: ${DISCORD_ACCOUNT_SCOPED_CONFIG_RESULT}"
  echo "- Discord account-scoped config failure reason: ${DISCORD_ACCOUNT_SCOPED_CONFIG_FAILURE_REASON}"
  echo "- Discord account-scoped token result: ${DISCORD_ACCOUNT_SCOPED_TOKEN_RESULT}"
  echo "- Discord account-scoped enabled result: ${DISCORD_ACCOUNT_SCOPED_ENABLED_RESULT}"
  echo "- Discord env-only implicit default attempted: ${DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_ATTEMPTED}"
  echo "- Discord env-only implicit default result: ${DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_RESULT}"
  echo "- Discord env-only implicit default failure reason: ${DISCORD_ENV_ONLY_IMPLICIT_DEFAULT_FAILURE_REASON}"
  echo "- Discord top-level token removed for env-only: ${DISCORD_TOP_LEVEL_TOKEN_REMOVED_FOR_ENV_ONLY}"
  echo "- Discord account-scoped token removed for env-only: ${DISCORD_ACCOUNT_SCOPED_TOKEN_REMOVED_FOR_ENV_ONLY}"
  echo "- Discord script env token present: ${DISCORD_SCRIPT_ENV_TOKEN_PRESENT}"
  echo "- Discord script env token length: ${DISCORD_SCRIPT_ENV_TOKEN_LENGTH}"
  echo "- Discord systemd env token present: ${DISCORD_SYSTEMD_ENV_TOKEN_PRESENT}"
  echo "- Discord systemd env token length: ${DISCORD_SYSTEMD_ENV_TOKEN_LENGTH}"
  echo "- Discord gateway env token present: ${DISCORD_GATEWAY_ENV_TOKEN_PRESENT}"
  echo "- Discord gateway env token length: ${DISCORD_GATEWAY_ENV_TOKEN_LENGTH}"
  echo "- Discord CLI env injected for status: ${DISCORD_CLI_ENV_INJECTED_FOR_STATUS}"
  echo "- Discord CLI env injected accounts JSON count: ${DISCORD_CLI_ENV_INJECTED_ACCOUNTS_JSON_COUNT}"
  echo "- Discord CLI env injected line: ${DISCORD_CLI_ENV_INJECTED_LINE}"
  echo "- Discord inactive surface warning seen: ${DISCORD_INACTIVE_SURFACE_WARNING_SEEN}"
  echo "- Discord accounts JSON count: ${DISCORD_ACCOUNTS_JSON_COUNT}"
  echo "- Discord loaded adapter proof attempted: ${DISCORD_LOADED_ADAPTER_PROOF_ATTEMPTED}"
  echo "- Discord loaded adapter proof result: ${DISCORD_LOADED_ADAPTER_PROOF_RESULT}"
  echo "- Discord loaded adapter proof failure reason: ${DISCORD_LOADED_ADAPTER_PROOF_FAILURE_REASON}"
  echo "- Discord loaded adapter ids env-only: ${DISCORD_LOADED_ADAPTER_IDS_ENV_ONLY}"
  echo "- Discord loaded adapter default account id env-only: ${DISCORD_LOADED_ADAPTER_DEFAULT_ACCOUNT_ID_ENV_ONLY}"
  echo "- Discord loaded adapter configured env-only: ${DISCORD_LOADED_ADAPTER_CONFIGURED_ENV_ONLY}"
  echo "- Discord loaded adapter token source env-only: ${DISCORD_LOADED_ADAPTER_TOKEN_SOURCE_ENV_ONLY}"
  echo "- Discord loaded adapter token status env-only: ${DISCORD_LOADED_ADAPTER_TOKEN_STATUS_ENV_ONLY}"
  echo "- Discord loaded adapter token length env-only: ${DISCORD_LOADED_ADAPTER_TOKEN_LENGTH_ENV_ONLY}"
  echo "- Discord loaded adapter ids explicit default: ${DISCORD_LOADED_ADAPTER_IDS_EXPLICIT_DEFAULT}"
  echo "- Discord loaded adapter configured explicit default: ${DISCORD_LOADED_ADAPTER_CONFIGURED_EXPLICIT_DEFAULT}"
  echo "- Discord loaded adapter proof gate mode: ${DISCORD_LOADED_ADAPTER_PROOF_GATE_MODE}"
  echo "- Discord public status accounts count: ${DISCORD_PUBLIC_STATUS_ACCOUNTS_COUNT}"
  echo "- Discord public env-only gate result: ${DISCORD_PUBLIC_ENV_ONLY_GATE_RESULT}"
  echo "- Discord public env-only gate failure reason: ${DISCORD_PUBLIC_ENV_ONLY_GATE_FAILURE_REASON}"
  echo "- Discord public env-only line result: ${DISCORD_PUBLIC_ENV_ONLY_LINE_RESULT}"
  echo "- Discord public env-only line: ${DISCORD_PUBLIC_ENV_ONLY_LINE}"
  echo "- Discord public env-only JSON result: ${DISCORD_PUBLIC_ENV_ONLY_JSON_RESULT}"
  echo "- Discord public env-only JSON installed: ${DISCORD_PUBLIC_ENV_ONLY_JSON_INSTALLED}"
  echo "- Discord public env-only JSON origin: ${DISCORD_PUBLIC_ENV_ONLY_JSON_ORIGIN}"
  echo "- Discord public env-only JSON default account: ${DISCORD_PUBLIC_ENV_ONLY_JSON_DEFAULT_ACCOUNT}"
  echo "- Discord public env-only gateway reachable: ${DISCORD_PUBLIC_ENV_ONLY_GATEWAY_REACHABLE}"
  echo "- Discord public env-only systemd token redacted: ${DISCORD_PUBLIC_ENV_ONLY_SYSTEMD_TOKEN_REDACTED}"
  echo "- Discord public env-only config token fields absent: ${DISCORD_PUBLIC_ENV_ONLY_CONFIG_TOKEN_FIELDS_ABSENT}"
  echo "- Discord public env-only config token field paths: ${DISCORD_PUBLIC_ENV_ONLY_CONFIG_TOKEN_FIELD_PATHS}"
  echo "- Discord status-layer lazy plugin bug suspected: ${DISCORD_STATUS_LAYER_LAZY_PLUGIN_BUG_SUSPECTED}"
  echo "- Discord failure class: ${DISCORD_FAILURE_CLASS}"
  echo
  echo "## Discord State Taxonomy"
  echo
  echo "- Discord plugin installed: ${DISCORD_PLUGIN_INSTALLED}"
  echo "- Discord env token present: ${DISCORD_ENV_TOKEN_PRESENT}"
  echo "- Discord adapter env configured plausible: ${DISCORD_ADAPTER_ENV_CONFIGURED_PLAUSIBLE}"
  echo "- Discord public account recognized: ${DISCORD_PUBLIC_ACCOUNT_RECOGNIZED}"
  echo "- Discord public account recognition source: ${DISCORD_PUBLIC_ACCOUNT_RECOGNITION_SOURCE}"
  echo "- Discord public status configured/enabled: ${DISCORD_PUBLIC_STATUS_CONFIGURED_ENABLED}"
  echo "- Discord provider startup observed: ${DISCORD_PROVIDER_STARTUP_OBSERVED}"
  echo "- Discord message proof completed: ${DISCORD_MESSAGE_PROOF_COMPLETED}"
  echo "- Discord verifier allowed: ${DISCORD_VERIFIER_ALLOWED}"
  echo "- Discord taxonomy note: plugin installed plus env token present does not imply public account recognition, provider startup, or message proof."
  echo "- Discord rollback decision: ${DISCORD_ROLLBACK_DECISION}"
  echo "- Discord rollback reason: ${DISCORD_ROLLBACK_REASON}"
  echo "- Discord env-only config preserved: ${DISCORD_ENV_ONLY_CONFIG_PRESERVED}"
  echo "- Discord known-bad SecretRef restore skipped: ${DISCORD_KNOWN_BAD_SECRETREF_RESTORE_SKIPPED}"
  echo "- Discord post-failure config has top-level token: ${DISCORD_POST_FAILURE_CONFIG_HAS_TOP_LEVEL_TOKEN}"
  echo "- Discord post-failure config shape: ${DISCORD_POST_FAILURE_CONFIG_SHAPE}"
  echo "- Discord gateway provider startup seen: ${DISCORD_GATEWAY_PROVIDER_STARTUP_SEEN}"
  echo "- Discord gateway provider startup pattern: ${DISCORD_GATEWAY_PROVIDER_STARTUP_PATTERN}"
  echo "- Discord gateway generic ready only: ${DISCORD_GATEWAY_GENERIC_READY_ONLY}"
  echo "- Discord gateway provider startup detection result: ${DISCORD_GATEWAY_PROVIDER_STARTUP_DETECTION_RESULT}"
  echo "- Discord gateway provider startup matched line: ${DISCORD_GATEWAY_PROVIDER_STARTUP_MATCHED_LINE}"
  echo "- Discord gateway provider startup matched line SHA-256: ${DISCORD_GATEWAY_PROVIDER_STARTUP_MATCHED_LINE_SHA256}"
  echo "- Discord runtime may still work: ${DISCORD_RUNTIME_MAY_STILL_WORK}"
  echo "- Discord line after SecretRef config: ${DISCORD_LINE_AFTER_SECRETREF_CONFIG}"
  echo "- Discord line after account-scoped config: ${DISCORD_LINE_AFTER_ACCOUNT_SCOPED_CONFIG}"
  echo "- Discord line after env-only implicit default: ${DISCORD_LINE_AFTER_ENV_ONLY_IMPLICIT_DEFAULT}"
  echo "- Discord channel state parser result: ${DISCORD_CHANNEL_STATE_PARSER_RESULT}"
  echo "- Discord channel state after repair: ${DISCORD_CHANNEL_STATE_AFTER_REPAIR}"
  echo "- Discord channel installed: ${DISCORD_CHANNEL_INSTALLED}"
  echo "- Discord channel configured: ${DISCORD_CHANNEL_CONFIGURED}"
  echo "- Discord channel enabled: ${DISCORD_CHANNEL_ENABLED}"
  echo "- Discord external plugin install required: ${DISCORD_EXTERNAL_PLUGIN_INSTALL_REQUIRED}"
  echo "- Discord external plugin install attempted: ${DISCORD_EXTERNAL_PLUGIN_INSTALL_ATTEMPTED}"
  echo "- Discord external plugin install result: ${DISCORD_EXTERNAL_PLUGIN_INSTALL_RESULT}"
  echo "- Discord channel config result: ${DISCORD_CHANNEL_CONFIG_RESULT}"
  echo "- Discord channel activation result: ${DISCORD_CHANNEL_ACTIVATION_RESULT}"
  echo "- Discord config result: ${DISCORD_CONFIG_RESULT}"
  echo "- Token refresh requested: $REFRESH_TOKEN"
  echo "- Discord token storage: ~/.openclaw/.env, ~/.config/environment.d/openclaw-discord.conf, and imported user environment"
  echo "- Discord setup path: OpenClaw env-only implicit default"
  echo "- Gateway active after restart: yes"
  if discord_verifier_recommendation_allowed "${DISCORD_CHANNEL_INSTALLED}|${DISCORD_CHANNEL_CONFIGURED}|${DISCORD_CHANNEL_ENABLED}"; then
    echo
    echo "## Next"
    echo
    echo "Run:"
    echo
    echo "  bash verify_openclaw_discord_v1.sh --owner-id $OWNER_ID"
  else
    echo
    echo "## Next"
    echo
    echo "- Verifier suppressed because authoritative Discord state is not installed/configured/enabled."
  fi
} | tee "$REPORT_FILE"

log "Creating Discord add-on evidence archive"
ARCHIVE="$HOME/openclaw_discord_config_v1_${STAMP}.tar.gz"
tar -czf "$ARCHIVE" -C "$LOG_ROOT" "$STAMP"

EXPORT_DIR=""
for d in "/mnt/c/Users/${WINUSER:-}" /mnt/c/Users/accou /mnt/c/Users/*; do
  [[ -n "$d" && -d "$d/Downloads" && -w "$d/Downloads" ]] || continue
  case "$d" in *"Default User"*|*"All Users"*|*"Public"*) continue ;; esac
  EXPORT_DIR="$d/Downloads"
  break
done

if [[ -n "$EXPORT_DIR" ]]; then
  cp "$ARCHIVE" "$EXPORT_DIR/" || true
  log "Evidence archive copied to: $EXPORT_DIR/$(basename "$ARCHIVE")"
fi

log "Discord configuration v1 complete"
cat "$REPORT_FILE"

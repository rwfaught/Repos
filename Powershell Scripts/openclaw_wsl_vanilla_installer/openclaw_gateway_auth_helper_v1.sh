#!/usr/bin/env bash
set -Eeuo pipefail
set +x

RESET_TOKEN=0
COPY_AUTH_URL=0
OPEN_DASHBOARD=0
COPIED="NO"
OPENED="NO"
AUTH_URL_FILE_WRITTEN="NO"
HELPER_RESULT="UNKNOWN"
WINDOWS_POWERSHELL=""
WINDOWS_POWERSHELL_CMD=()
WINDOWS_CLIP=""
WINDOWS_EXPLORER=""
WINDOWS_CMD=""

print_status_lines() {
  echo "Dashboard authenticated URL copied to clipboard: ${COPIED}"
  echo "Dashboard browser opened: ${OPENED}"
  echo "Dashboard auth URL file written: ${AUTH_URL_FILE_WRITTEN}"
  echo "Dashboard token printed: NO"
  echo "Dashboard helper result: ${HELPER_RESULT}"
}

fail_helper() {
  local message="$1"
  HELPER_RESULT="FAIL"
  print_status_lines
  echo "$message" >&2
  exit 1
}

usage() {
  cat <<'USAGE'
Usage:
  bash openclaw_gateway_auth_helper_v1.sh [--reset-token] [--copy-auth-url] [--open-dashboard]
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --reset-token) RESET_TOKEN=1; shift ;;
    --copy-auth-url) COPY_AUTH_URL=1; shift ;;
    --open-dashboard) OPEN_DASHBOARD=1; shift ;;
    --help|-h) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

resolve_windows_powershell() {
  local candidate=""

  if candidate="$(command -v powershell.exe 2>/dev/null)" && [[ -n "$candidate" ]]; then
    :
  elif [[ -x "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe" ]]; then
    candidate="/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
  elif candidate="$(command -v pwsh.exe 2>/dev/null)" && [[ -n "$candidate" ]]; then
    :
  elif [[ -x "/mnt/c/Program Files/PowerShell/7/pwsh.exe" ]]; then
    candidate="/mnt/c/Program Files/PowerShell/7/pwsh.exe"
  else
    return 1
  fi

  WINDOWS_POWERSHELL="$candidate"
  WINDOWS_POWERSHELL_CMD=("$candidate")
}

resolve_windows_clip() {
  local candidate=""

  if candidate="$(command -v clip.exe 2>/dev/null)" && [[ -n "$candidate" ]]; then
    :
  elif [[ -x "/mnt/c/Windows/System32/clip.exe" ]]; then
    candidate="/mnt/c/Windows/System32/clip.exe"
  else
    return 1
  fi

  WINDOWS_CLIP="$candidate"
}

resolve_windows_explorer() {
  local candidate=""

  if candidate="$(command -v explorer.exe 2>/dev/null)" && [[ -n "$candidate" ]]; then
    :
  elif [[ -x "/mnt/c/Windows/explorer.exe" ]]; then
    candidate="/mnt/c/Windows/explorer.exe"
  else
    return 1
  fi

  WINDOWS_EXPLORER="$candidate"
}

resolve_windows_cmd() {
  local candidate=""

  if candidate="$(command -v cmd.exe 2>/dev/null)" && [[ -n "$candidate" ]]; then
    :
  elif [[ -x "/mnt/c/Windows/System32/cmd.exe" ]]; then
    candidate="/mnt/c/Windows/System32/cmd.exe"
  else
    return 1
  fi

  WINDOWS_CMD="$candidate"
}

log_action_failure() {
  local action="$1"
  local rc="$2"

  printf 'Dashboard helper action failed: %s rc=%s\n' "$action" "$rc" >&2
}

copy_authenticated_url() {
  local rc=0

  if resolve_windows_powershell; then
    if printf '%s' "$AUTH_URL" |
      "${WINDOWS_POWERSHELL_CMD[@]}" -NoProfile -ExecutionPolicy Bypass \
        -Command '$ErrorActionPreference = "Stop"; $input | Set-Clipboard' >/dev/null 2>&1; then
      return 0
    else
      rc=$?
      log_action_failure "clipboard PowerShell Set-Clipboard" "$rc"
    fi
  else
    log_action_failure "clipboard PowerShell resolver" "127"
  fi

  if resolve_windows_clip; then
    if printf '%s' "$AUTH_URL" | "$WINDOWS_CLIP" >/dev/null 2>&1; then
      return 0
    else
      rc=$?
      log_action_failure "clipboard clip.exe" "$rc"
    fi
  else
    log_action_failure "clipboard clip.exe resolver" "127"
  fi

  return 1
}

open_authenticated_dashboard() {
  local rc=0

  if resolve_windows_powershell; then
    if printf '%s' "$AUTH_URL" |
      "${WINDOWS_POWERSHELL_CMD[@]}" -NoProfile -ExecutionPolicy Bypass \
        -Command '$ErrorActionPreference = "Stop"; $input | ForEach-Object { Start-Process -FilePath $_ -ErrorAction Stop }' >/dev/null 2>&1; then
      return 0
    else
      rc=$?
      log_action_failure "browser PowerShell Start-Process" "$rc"
    fi
  else
    log_action_failure "browser PowerShell resolver" "127"
  fi

  if resolve_windows_explorer; then
    if "$WINDOWS_EXPLORER" "$AUTH_URL" >/dev/null 2>&1; then
      return 0
    else
      rc=$?
      log_action_failure "browser explorer.exe" "$rc"
    fi
  else
    log_action_failure "browser explorer.exe resolver" "127"
  fi

  if resolve_windows_cmd; then
    if "$WINDOWS_CMD" /c start "" "$AUTH_URL" >/dev/null 2>&1; then
      return 0
    else
      rc=$?
      log_action_failure "browser cmd.exe start" "$rc"
    fi
  else
    log_action_failure "browser cmd.exe resolver" "127"
  fi

  return 1
}

write_authenticated_url_file() {
  local target="$1"
  local parent=""
  local temp_file=""
  local rc=0

  if parent="$(dirname -- "$target")"; then
    :
  else
    rc=$?
    log_action_failure "auth URL file parent resolution" "$rc"
    return 1
  fi

  if mkdir -p -- "$parent" >/dev/null 2>&1; then
    :
  else
    rc=$?
    log_action_failure "auth URL file parent creation" "$rc"
    return 1
  fi

  if temp_file="$(umask 077; mktemp -- "${target}.tmp.XXXXXX")"; then
    :
  else
    rc=$?
    log_action_failure "auth URL temporary file creation" "$rc"
    return 1
  fi

  if printf '%s' "$AUTH_URL" >"$temp_file"; then
    :
  else
    rc=$?
    rm -f -- "$temp_file" >/dev/null 2>&1 || true
    log_action_failure "auth URL temporary file write" "$rc"
    return 1
  fi

  chmod 600 -- "$temp_file" >/dev/null 2>&1 || true
  if mv -f -- "$temp_file" "$target" >/dev/null 2>&1; then
    :
  else
    rc=$?
    rm -f -- "$temp_file" >/dev/null 2>&1 || true
    log_action_failure "auth URL file publish" "$rc"
    return 1
  fi

  chmod 600 -- "$target" >/dev/null 2>&1 || true
  return 0
}

get_token_from_config_linux() {
  local config_path=""
  local token_value=""

  [[ -n "${HOME:-}" ]] || return 1
  config_path="${HOME}/.openclaw/openclaw.json"
  [[ -f "$config_path" ]] || return 1

  if command -v python3 >/dev/null 2>&1; then
    token_value="$(
      python3 - "$config_path" 2>/dev/null <<'PY'
import json
import sys

try:
    with open(sys.argv[1], encoding="utf-8") as config_file:
        config = json.load(config_file)
    token = config.get("gateway", {}).get("auth", {}).get("token", "")
except (AttributeError, json.JSONDecodeError, OSError, TypeError):
    raise SystemExit(1)

if not isinstance(token, str) or not token.strip():
    raise SystemExit(1)

sys.stdout.write(token)
PY
    )" || return 1
  elif command -v node >/dev/null 2>&1; then
    token_value="$(
      node - "$config_path" 2>/dev/null <<'NODE'
const fs = require("fs");

let config;
try {
  config = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
} catch {
  process.exit(1);
}

const token = config?.gateway?.auth?.token;
if (typeof token !== "string" || token.trim() === "") {
  process.exit(1);
}

process.stdout.write(token);
NODE
    )" || return 1
  else
    return 1
  fi

  TOKEN="$token_value"
  [[ -n "$TOKEN" ]]
}

TOKEN_SOURCE=""
TOKEN="${OPENCLAW_GATEWAY_TOKEN:-}"
if [[ -n "$TOKEN" ]]; then
  TOKEN_SOURCE="env"
else
  TOKEN=""
  if get_token_from_config_linux; then
    TOKEN_SOURCE="config"
  fi
fi

if [[ "$RESET_TOKEN" == "1" ]]; then
  command -v openssl >/dev/null 2>&1 || fail_helper "openssl not found"
  TOKEN="$(openssl rand -hex 32)"
  openclaw config set gateway.auth.token "$TOKEN" || fail_helper "failed to persist refreshed gateway token"
  systemctl --user restart openclaw-gateway.service || fail_helper "failed to restart openclaw-gateway.service"
  TOKEN_SOURCE="rotated"
fi

[[ -n "$TOKEN" ]] || fail_helper "Gateway token not found in env or config."
AUTH_URL="http://127.0.0.1:18789/#token=${TOKEN}"
ACTION_FAILED=0
AUTH_URL_FILE_FAILED=0

if [[ -n "${OPENCLAW_DASHBOARD_AUTH_URL_FILE:-}" ]]; then
  if write_authenticated_url_file "$OPENCLAW_DASHBOARD_AUTH_URL_FILE"; then
    AUTH_URL_FILE_WRITTEN="YES"
  else
    AUTH_URL_FILE_WRITTEN="NO"
    AUTH_URL_FILE_FAILED=1
  fi
fi

if [[ "$COPY_AUTH_URL" == "1" ]]; then
  if copy_authenticated_url; then
    COPIED="YES"
  else
    COPIED="NO"
    ACTION_FAILED=1
  fi
else
  COPIED="NO"
fi

if [[ "$OPEN_DASHBOARD" == "1" ]]; then
  if open_authenticated_dashboard; then
    OPENED="YES"
  else
    OPENED="NO"
    ACTION_FAILED=1
  fi
else
  OPENED="NO"
fi

if [[ "$AUTH_URL_FILE_FAILED" == "1" ]] ||
  [[ "$ACTION_FAILED" == "1" && "$AUTH_URL_FILE_WRITTEN" != "YES" ]]; then
  HELPER_RESULT="FAIL"
  print_status_lines
  exit 1
fi

HELPER_RESULT="PASS"
print_status_lines

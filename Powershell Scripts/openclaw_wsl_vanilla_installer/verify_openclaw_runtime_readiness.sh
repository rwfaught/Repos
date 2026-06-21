#!/usr/bin/env bash
set -Eeuo pipefail

MARKER_DIR="${WIRE_MARKER_DIR:-}"
MAX_ATTEMPTS="${OPENCLAW_RUNTIME_READY_ATTEMPTS:-30}"
DELAY_SECONDS="${OPENCLAW_RUNTIME_READY_DELAY_SECONDS:-2}"

write_marker() {
  local key="$1" value="$2"
  [[ -n "$MARKER_DIR" ]] || return 0
  mkdir -p "$MARKER_DIR"
  cat >"${MARKER_DIR}/${key}.marker" <<EOF
key=${key}
value=${value}
timestamp=$(date -Iseconds)
EOF
}

discord_probe_ready() {
  local probe_file="$1"
  local line lower
  while IFS= read -r line; do
    lower="$(printf '%s' "$line" | tr '[:upper:]' '[:lower:]')"
    [[ "$lower" == *"discord"* ]] || continue
    if [[ "$lower" == *"running"* && ( "$lower" == *"connected"* || "$lower" == *"works"* ) ]]; then
      return 0
    fi
  done < "$probe_file"
  return 1
}

probe_file="$(mktemp)"
trap 'rm -f "$probe_file"' EXIT

write_marker "postInstallRuntimeReadiness" "IN_PROGRESS"
write_marker "finalGatewayStatus" "UNKNOWN"
write_marker "finalDiscordStatus" "UNKNOWN"

systemctl --user daemon-reload
systemctl --user enable openclaw-gateway.service >/dev/null 2>&1 || true
systemctl --user restart openclaw-gateway.service

for ((attempt=1; attempt<=MAX_ATTEMPTS; attempt++)); do
  openclaw channels status --probe > "$probe_file" 2>&1 || true
  if systemctl --user is-active --quiet openclaw-gateway.service && discord_probe_ready "$probe_file"; then
    cat "$probe_file"
    write_marker "finalGatewayStatus" "ACTIVE"
    write_marker "finalDiscordStatus" "RUNNING_CONNECTED_WORKS"
    write_marker "postInstallRuntimeReadiness" "PASS"
    echo "Post-install runtime readiness: PASS"
    exit 0
  fi
  sleep "$DELAY_SECONDS"
done

cat "$probe_file"
write_marker "finalGatewayStatus" "NOT_ACTIVE_OR_UNREADY"
write_marker "finalDiscordStatus" "NOT_RUNNING_CONNECTED_WORKS"
write_marker "postInstallRuntimeReadiness" "FAIL"
echo "Post-install runtime readiness: FAIL" >&2
exit 1

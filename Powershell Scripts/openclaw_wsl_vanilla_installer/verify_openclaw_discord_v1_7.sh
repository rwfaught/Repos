#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_NAME="$(basename "$0")"
STAMP="$(date +%Y%m%d_%H%M%S)"
LOG_ROOT="${HOME}/openclaw_discord_addon_logs"
LOG_DIR="${LOG_ROOT}/verify_v1_7_${STAMP}"
LOG_FILE="${LOG_DIR}/verify.log"
REPORT_FILE="${LOG_DIR}/REPORT.md"
OWNER_ID=""
TOKEN_PROVIDED="UNKNOWN"
REFRESH_TOKEN_REQUESTED="UNKNOWN"
MARKER_DIR="${WIRE_MARKER_DIR:-}"
EXPECTED_MODEL="qwen3:0.6b"
EXPECTED_CONTEXT="32768"
EXPECTED_CONTEXT_MODE="minimum"
DISCORD_PLUGIN_INSTALLED="UNKNOWN"
DISCORD_PUBLIC_STATUS_CONFIGURED_ENABLED="UNKNOWN"
DISCORD_PROVIDER_STARTUP_OBSERVED="UNKNOWN"
DISCORD_MESSAGE_PROOF_COMPLETED="REQUIRED"
DISCORD_VERIFIER_ALLOWED="NO"
DISCORD_READINESS_ATTEMPTS="${DISCORD_READINESS_ATTEMPTS:-30}"
DISCORD_READINESS_DELAY_SECONDS="${DISCORD_READINESS_DELAY_SECONDS:-2}"
SELF_TEST_PARSER=0

# Initialize all verifier bookkeeping before any readiness helper can emit markers.
discord_line=""
parsed_discord_line="MISSING|unknown|unknown|unknown"
discord_parser_result="MISSING"
discord_installed="unknown"
discord_configured="unknown"
discord_enabled="unknown"
discord_transport="UNKNOWN"
discord_message_proof="REQUIRED"
manual_discord_message_test="REQUIRED"
discord_pairing_approved="NOT_REQUIRED"
discord_failure_reason="none"
pairing_gate="$discord_pairing_approved"
manual_test_result="$manual_discord_message_test"

mkdir -p "$LOG_DIR"
exec > >(tee -a "$LOG_FILE") 2>&1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --owner-id) OWNER_ID="${2:-}"; shift 2 ;;
    --token-provided) TOKEN_PROVIDED="${2:-}"; shift 2 ;;
    --refresh-token-requested) REFRESH_TOKEN_REQUESTED="${2:-}"; shift 2 ;;
    --self-test-parser) SELF_TEST_PARSER=1; shift ;;
    --help|-h) exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done
if [[ "$SELF_TEST_PARSER" != "1" ]]; then
  [[ -n "$OWNER_ID" ]] || { echo "--owner-id is required" >&2; exit 1; }
fi

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

write_marker "discord_token_provided" "$TOKEN_PROVIDED"
write_marker "discord_refresh_token_requested" "$REFRESH_TOKEN_REQUESTED"
write_marker "discord_prompt_sent" "NO"
write_marker "discord_pairing_approved" "NOT_REQUIRED"
write_marker "discordMessageProofCompleted" "$DISCORD_MESSAGE_PROOF_COMPLETED"
write_marker "discordManualMessageProof" "REQUIRED"
write_marker "discordTransportProof" "UNKNOWN"
write_marker "discordVerifierAllowed" "$DISCORD_VERIFIER_ALLOWED"

extract_discord_channel_line() {
  local source_file="$1"
  grep -iE '^[[:space:]]*-[[:space:]]*Discord([[:space:]][^:]*)?:[[:space:]]*' "$source_file" 2>/dev/null | head -n 1 || true
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

  if [[ "$installed" == "unknown" || "$configured" == "unknown" || "$enabled" == "unknown" ]]; then
    printf 'FAIL|%s|%s|%s\n' "$installed" "$configured" "$enabled"
  else
    printf 'PASS|%s|%s|%s\n' "$installed" "$configured" "$enabled"
  fi
}

run_parser_self_test() {
  local failures=0 parsed result installed configured enabled line display_line expected_result expected_state tmpfile extracted
  local fixture_rows=(
    "PASS|installed|configured|enabled|- Discord: installed, configured, enabled"
    "PASS|installed|configured|enabled|- Discord default (Discord): installed, configured, enabled, token=env"
    "PASS|installed|configured|disabled|- Discord default (Discord): installed, configured, disabled, token=env"
    "PASS|installed|not-configured|disabled|- Discord: installed, not configured, disabled"
    "PASS|not-installed|configured|disabled|- Discord: not installed, configured, disabled"
    "PASS|not-installed|not-configured|disabled|- Discord: not installed, not configured, disabled"
    "FAIL|installed|configured|unknown|- Discord default (Discord): installed, configured, token=env"
    "MISSING|unknown|unknown|unknown|"
  )

  tmpfile="$(mktemp)"
  printf 'noise\n- Discord default (Discord): installed, configured, enabled, token=env\n' > "$tmpfile"
  extracted="$(extract_discord_channel_line "$tmpfile")"
  rm -f "$tmpfile"
  if [[ "$extracted" != "- Discord default (Discord): installed, configured, enabled, token=env" ]]; then
    printf 'PARSER_FIXTURE extract_current_status FAIL got=%s\n' "$extracted"
    failures=$((failures + 1))
  else
    printf 'PARSER_FIXTURE extract_current_status PASS\n'
  fi

  for row in "${fixture_rows[@]}"; do
    IFS='|' read -r expected_result installed configured enabled line <<<"$row"
    expected_state="${expected_result}|${installed}|${configured}|${enabled}"
    parsed="$(parse_discord_channel_line "$line")"
    IFS='|' read -r result _ _ _ <<<"$parsed"
    display_line="$line"
    [[ -n "$display_line" ]] || display_line="<empty>"
    if [[ "$parsed" == "$expected_state" ]]; then
      printf 'PARSER_FIXTURE %s PASS\n' "$display_line"
    else
      printf 'PARSER_FIXTURE %s FAIL expected=%s got=%s\n' "$display_line" "$expected_state" "$parsed"
      failures=$((failures + 1))
    fi
  done

  if [[ "$failures" == "0" ]]; then
    printf 'PARSER_FIXTURE_GATE=PASS\n'
    return 0
  fi
  printf 'PARSER_FIXTURE_GATE=FAIL\n'
  return 1
}

if [[ "$SELF_TEST_PARSER" == "1" ]]; then
  run_parser_self_test
  exit $?
fi

write_discord_verifier_taxonomy_markers() {
  case "$discord_installed" in
    installed) DISCORD_PLUGIN_INSTALLED="YES" ;;
    not-installed) DISCORD_PLUGIN_INSTALLED="NO" ;;
    *) DISCORD_PLUGIN_INSTALLED="UNKNOWN" ;;
  esac

  if [[ "$discord_installed" == "installed" && "$discord_configured" == "configured" && "$discord_enabled" == "enabled" ]]; then
    DISCORD_PUBLIC_STATUS_CONFIGURED_ENABLED="YES"
  else
    DISCORD_PUBLIC_STATUS_CONFIGURED_ENABLED="NO"
    DISCORD_VERIFIER_ALLOWED="NO"
  fi

  if [[ "$DISCORD_PUBLIC_STATUS_CONFIGURED_ENABLED" == "YES" && "$DISCORD_PROVIDER_STARTUP_OBSERVED" == "YES" && "$DISCORD_MESSAGE_PROOF_COMPLETED" == "YES" ]]; then
    DISCORD_VERIFIER_ALLOWED="YES"
  else
    DISCORD_VERIFIER_ALLOWED="NO"
  fi

  write_marker "discordPluginInstalled" "$DISCORD_PLUGIN_INSTALLED"
  write_marker "discordPublicStatusConfiguredEnabled" "$DISCORD_PUBLIC_STATUS_CONFIGURED_ENABLED"
  write_marker "discordProviderStartupObserved" "$DISCORD_PROVIDER_STARTUP_OBSERVED"
  write_marker "discordMessageProofCompleted" "$DISCORD_MESSAGE_PROOF_COMPLETED"
  write_marker "discordVerifierAllowed" "$DISCORD_VERIFIER_ALLOWED"
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

wait_for_discord_ready() {
  local attempt
  systemctl --user daemon-reload
  systemctl --user restart openclaw-gateway.service
  for ((attempt=1; attempt<=DISCORD_READINESS_ATTEMPTS; attempt++)); do
    systemctl --user is-active --quiet openclaw-gateway.service || true
    openclaw channels status --probe > "$LOG_DIR/openclaw_channels_status_probe.txt" 2>&1 || true
    if systemctl --user is-active --quiet openclaw-gateway.service && discord_probe_ready "$LOG_DIR/openclaw_channels_status_probe.txt"; then
      DISCORD_PROVIDER_STARTUP_OBSERVED="YES"
      write_discord_verifier_taxonomy_markers
      return 0
    fi
    sleep "$DISCORD_READINESS_DELAY_SECONDS"
  done
  DISCORD_PROVIDER_STARTUP_OBSERVED="NO"
  DISCORD_VERIFIER_ALLOWED="NO"
  write_discord_verifier_taxonomy_markers
  return 1
}

BOUNDARY="$(date '+%Y-%m-%d %H:%M:%S')"
openclaw models list --provider ollama | tee "$LOG_DIR/openclaw_models_ollama.txt"
openclaw config get agents.defaults.model --json | tee "$LOG_DIR/openclaw_agents_defaults_model.json"
EXPECTED_MODEL="$(python3 - "$LOG_DIR/openclaw_agents_defaults_model.json" <<'PY'
import json,sys
doc=json.load(open(sys.argv[1],encoding='utf-8'))
print(str(doc.get('primary','ollama/qwen3:0.6b')).replace('ollama/','',1))
PY
)"
if [[ "$EXPECTED_MODEL" == "qwen3:0.6b" ]]; then
  EXPECTED_CONTEXT="32768"
  EXPECTED_CONTEXT_MODE="minimum"
fi
wait_for_discord_ready || die "Discord did not reach running/connected/works readiness after gateway restart"
discord_transport="PASS"
write_marker "discordTransportProof" "PASS"
cat "$LOG_DIR/openclaw_channels_status_probe.txt"
openclaw channels list --all | tee "$LOG_DIR/openclaw_channels_list_all.txt" || true
openclaw channels list | tee "$LOG_DIR/openclaw_channels_list.txt" || true

discord_line="$(extract_discord_channel_line "$LOG_DIR/openclaw_channels_list_all.txt")"
if [[ -z "$discord_line" ]]; then
  discord_line="$(extract_discord_channel_line "$LOG_DIR/openclaw_channels_list.txt")"
fi
parsed_discord_line="$(parse_discord_channel_line "$discord_line")"
IFS='|' read -r discord_parser_result discord_installed discord_configured discord_enabled <<<"$parsed_discord_line"
write_marker "discordChannelStateParserResult" "$discord_parser_result"
write_marker "discordChannelInstalled" "$discord_installed"
write_marker "discordChannelConfigured" "$discord_configured"
write_marker "discordChannelEnabled" "$discord_enabled"
write_discord_verifier_taxonomy_markers

if [[ "$discord_parser_result" == "FAIL" || -z "$discord_line" ]]; then
  write_marker "discord_prompt_sent" "NO"
  die "discord-channel-state-parse-failed"
fi
if [[ "$discord_installed" == "not-installed" ]]; then
  write_marker "discord_prompt_sent" "NO"
  die "discord-channel-not-installed"
fi
if [[ "$discord_installed" == "not-installed" && "$discord_configured" == "configured" && "$discord_enabled" == "disabled" ]]; then
  write_marker "discord_prompt_sent" "NO"
  die "discord-channel-not-installed"
fi
if [[ "$discord_installed" == "installed" && "$discord_configured" == "not-configured" && "$discord_enabled" == "disabled" ]]; then
  write_marker "discord_prompt_sent" "NO"
  die "discord-channel-not-configured"
fi
if [[ "$discord_installed" == "installed" && "$discord_configured" == "configured" && "$discord_enabled" == "disabled" ]]; then
  write_marker "discord_prompt_sent" "NO"
  die "discord-channel-disabled"
fi
if [[ "$discord_installed" != "installed" || "$discord_configured" != "configured" || "$discord_enabled" != "enabled" ]]; then
  write_marker "discord_prompt_sent" "NO"
  die "discord-channel-not-active"
fi

journalctl --user -u openclaw-gateway.service --since "$BOUNDARY" --no-pager > "$LOG_DIR/openclaw_gateway_logs_since_discord.txt" || true
ollama ps | tee "$LOG_DIR/ollama_ps_after_discord.txt"

pairing_gate="$discord_pairing_approved"
manual_test_result="$manual_discord_message_test"
cat <<'PROMPT'
DM the configured Discord bot exactly: Reply with DISCORD_SMOKE_OK only.
After the bot replies with DISCORD_SMOKE_OK, return to this installer.
If Discord first gives a pairing command, paste that complete command at the prompt below.
PROMPT
write_marker "discord_prompt_sent" "YES"

while true; do
  read -r -p "Type DISCORD_SMOKE_OK after the bot replied, or paste the pairing approval command: " proof_input
  if [[ "$proof_input" == "DISCORD_SMOKE_OK" ]]; then
    break
  fi
  if [[ "$proof_input" =~ ^openclaw[[:space:]]+pairing[[:space:]]+approve[[:space:]]+discord[[:space:]]+([A-Za-z0-9_-]+)$ ]]; then
    code="${BASH_REMATCH[1]}"
    openclaw pairing approve discord "$code" | tee "$LOG_DIR/pairing_approval.txt"
    discord_pairing_approved="YES"
    pairing_gate="YES"
    write_marker "discord_pairing_approved" "YES"
    echo "Pairing approved. DM the configured Discord bot again exactly: Reply with DISCORD_SMOKE_OK only."
    continue
  fi
  DISCORD_MESSAGE_PROOF_COMPLETED="NO"
  discord_message_proof="FAIL"
  manual_discord_message_test="FAIL"
  discord_failure_reason="manual-proof-not-confirmed"
  DISCORD_VERIFIER_ALLOWED="NO"
  write_discord_verifier_taxonomy_markers
  write_marker "discordManualMessageProof" "FAIL"
  die "Manual Discord proof not confirmed. Expected DISCORD_SMOKE_OK or a valid pairing approval command."
done

DISCORD_MESSAGE_PROOF_COMPLETED="YES"
discord_message_proof="PASS"
manual_discord_message_test="PASS"
discord_failure_reason="none"
DISCORD_VERIFIER_ALLOWED="YES"
write_discord_verifier_taxonomy_markers
write_marker "discordManualMessageProof" "PASS"
write_marker "discord_token_provided" "$TOKEN_PROVIDED"
write_marker "discord_refresh_token_requested" "$REFRESH_TOKEN_REQUESTED"
manual_test_result="$manual_discord_message_test"

if grep -qiE '401|unauthorized|invalid token|missing intents|intent.*missing|unknown model|All models failed|FailoverError' "$LOG_DIR/openclaw_gateway_logs_since_discord.txt"; then
  die "Discord/provider failure found in fresh logs"
fi
if awk -v model="$EXPECTED_MODEL" '$1 == model { found = 1 } END { exit(found ? 0 : 1) }' "$LOG_DIR/ollama_ps_after_discord.txt"; then
  awk -v model="$EXPECTED_MODEL" -v expected="$EXPECTED_CONTEXT" -v mode="$EXPECTED_CONTEXT_MODE" '
    $1 == model && index($0, "100% GPU") {
      for (i = 1; i <= NF; i++) {
        if ($i ~ /^[0-9]+$/ && ((mode == "exact" && $i == expected) || (mode == "minimum" && $i >= expected))) {
          found = 1
        }
      }
    }
    END { exit(found ? 0 : 1) }
  ' "$LOG_DIR/ollama_ps_after_discord.txt" || die "model loaded but expected GPU/context policy was not observed"
fi

{
  echo "# Discord Verification Report v1.7"
  echo
  echo "- Discord parsed line: ${discord_line:-<missing>}"
  echo "- Discord parser result: ${discord_parser_result}"
  echo "- Discord state: ${discord_installed}, ${discord_configured}, ${discord_enabled}"
  echo "- Discord plugin installed: ${DISCORD_PLUGIN_INSTALLED}"
  echo "- Discord public status configured/enabled: ${DISCORD_PUBLIC_STATUS_CONFIGURED_ENABLED}"
  echo "- Discord provider startup observed: ${DISCORD_PROVIDER_STARTUP_OBSERVED}"
  echo "- Discord message proof completed: ${DISCORD_MESSAGE_PROOF_COMPLETED}"
  echo "- Discord verifier allowed: ${DISCORD_VERIFIER_ALLOWED}"
  echo "- Manual Discord message test: ${manual_test_result}"
  echo "- Discord pairing approved: ${pairing_gate}"
  echo "- Discord transport proof: PASS"
  echo "- Discord manual message proof: PASS"
  echo "- Discord failure reason: ${discord_failure_reason}"
  echo "- Evidence dir: $LOG_DIR"
} | tee "$REPORT_FILE"

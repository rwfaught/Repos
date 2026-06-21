#!/usr/bin/env bash
set -u

PROJECT_ROOT="/home/roger/codex/projects"
LOG_ROOT="$PROJECT_ROOT/test_logs"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="$LOG_ROOT/acceptance_$TIMESTAMP"
SUMMARY="$RUN_DIR/summary.txt"

OLLAMA_URL="http://127.0.0.1:11434"
OLLAMA_MODEL="qwen2.5-coder:14b"
OLLAMA_LOG="/tmp/ollama_acceptance_${TIMESTAMP}.log"

mkdir -p "$RUN_DIR"

log() {
  printf '%s\n' "$*" | tee -a "$SUMMARY"
}

section() {
  printf '\n==================================================\n' | tee -a "$SUMMARY"
  printf '%s\n' "$*" | tee -a "$SUMMARY"
  printf '==================================================\n' | tee -a "$SUMMARY"
}

capture_file() {
  local label="$1"
  local path="$2"
  {
    echo
    echo "--- $label: $path ---"
    if [[ -f "$path" ]]; then
      cat "$path"
    else
      echo "(missing)"
    fi
  } >> "$SUMMARY"
}

latest_file() {
  local dir="$1"
  if [[ -d "$dir" ]]; then
    ls -1t "$dir" 2>/dev/null | head -n 1
  fi
}

run_cmd() {
  local label="$1"
  shift
  local outfile="$RUN_DIR/${label}.out"
  {
    echo "\$ $*"
    "$@"
  } >"$outfile" 2>&1
  local rc=$?
  local status="PASS"
  if [[ $rc -ne 0 ]]; then
    status="FAIL"
  fi
  {
    echo
    echo "--- COMMAND: $label ---"
    echo "--- RESULT: $status ---"
    cat "$outfile"
    echo "--- EXIT CODE: $rc ---"
  } >> "$SUMMARY"
  return "$rc"
}

write_task() {
  local task_id="$1"
  local run_id="$2"
  local title="$3"
  local role="$4"
  local file_in_scope="$5"

  cat > "$PROJECT_ROOT/data/tasks/${task_id}.json" <<EOF
{
  "id": "$task_id",
  "run_id": "$run_id",
  "title": "$title",
  "role": "$role",
  "status": "queued",
  "dependencies": [],
  "success_criteria": [
    "Return a bounded response"
  ],
  "files_in_scope": [
    "$file_in_scope"
  ],
  "retry_count": 0
}
EOF
}

read_active_run_id() {
  python3 - <<'PY'
import json
from pathlib import Path
p = Path("/home/roger/codex/projects/data/state/workspace_state.json")
data = json.loads(p.read_text(encoding="utf-8"))
print(data.get("active_run_id", ""))
PY
}

capture_execution_artifacts() {
  local task_id="$1"
  local latest_artifact latest_verifier
  latest_artifact="$(latest_file "$PROJECT_ROOT/data/artifacts")"
  latest_verifier="$(latest_file "$PROJECT_ROOT/data/verifier_results")"

  capture_file "TASK JSON" "$PROJECT_ROOT/data/tasks/${task_id}.json"

  if [[ -n "${latest_artifact:-}" ]]; then
    capture_file "LATEST ARTIFACT" "$PROJECT_ROOT/data/artifacts/$latest_artifact"
  fi

  if [[ -n "${latest_verifier:-}" ]]; then
    capture_file "LATEST VERIFIER RESULT" "$PROJECT_ROOT/data/verifier_results/$latest_verifier"
  fi
}

ollama_running() {
  curl -fsS "$OLLAMA_URL/api/tags" >/dev/null 2>&1
}

ensure_ollama_running() {
  section "Ollama Preflight"

  if ollama_running; then
    log "Ollama API already reachable at $OLLAMA_URL"
    return 0
  fi

  log "Ollama API not reachable. Starting ollama serve ..."
  nohup ollama serve >"$OLLAMA_LOG" 2>&1 &
  local pid=$!
  log "Started ollama serve with PID $pid"
  log "Ollama log: $OLLAMA_LOG"

  local tries=0
  until ollama_running; do
    tries=$((tries + 1))
    if [[ $tries -ge 30 ]]; then
      log "Ollama did not become ready in time."
      return 1
    fi
    sleep 1
  done

  log "Ollama API is now reachable."
}

ensure_ollama_model() {
  section "Ollama Model Check"

  if ! command -v ollama >/dev/null 2>&1; then
    log "ollama command not found."
    return 1
  fi

  if ollama list 2>/dev/null | awk '{print $1}' | grep -Fxq "$OLLAMA_MODEL"; then
    log "Model already present: $OLLAMA_MODEL"
    return 0
  fi

  log "Model not found locally. Pulling: $OLLAMA_MODEL"
  run_cmd "ollama_pull_model" ollama pull "$OLLAMA_MODEL"
  log "Model pull attempted for: $OLLAMA_MODEL"
}

section "Acceptance Test Run"
log "Project root: $PROJECT_ROOT"
log "Log dir: $RUN_DIR"

cd "$PROJECT_ROOT" || exit 1

section "Test 1 - Workspace Initialization"
run_cmd "test01_init" python3 main.py init
capture_file "WORKSPACE STATE" "$PROJECT_ROOT/data/state/workspace_state.json"

section "Test 2 - Stable Path Handling From Outside Project Root"
run_cmd "test02_status_outside_root" bash -lc "cd /tmp && python3 $PROJECT_ROOT/main.py status"

section "Test 3 - Run Creation and Active Run Tracking"
run_cmd "test03_new_run" python3 main.py new-run "Acceptance test run"
ACTIVE_RUN_ID="$(read_active_run_id)"
log "Active run id: $ACTIVE_RUN_ID"
capture_file "WORKSPACE STATE" "$PROJECT_ROOT/data/state/workspace_state.json"

section "Test 4 - Mock Provider Happy Path"
write_task "task_test_mock_pass" "$ACTIVE_RUN_ID" "Mock provider success test" "coder" "main.py"
run_cmd "test04_mock_pass" python3 main.py next
capture_execution_artifacts "task_test_mock_pass"

section "Test 5 - Verification Failure Path"
write_task "task_test_verification_fail" "$ACTIVE_RUN_ID" "Mock provider verification fail test" "coder" "does_not_exist.txt"
run_cmd "test05_verification_fail" python3 main.py next
capture_execution_artifacts "task_test_verification_fail"

section "Test 6 - Execution Failure Path"
write_task "task_test_execution_fail" "$ACTIVE_RUN_ID" "Unknown provider execution failure test" "coder" "main.py"
run_cmd "test06_execution_fail" python3 main.py next --provider no_such_provider
capture_execution_artifacts "task_test_execution_fail"

ensure_ollama_running || log "Ollama start step failed; proceeding to capture behavior anyway."
ensure_ollama_model || log "Ollama model check/pull failed; proceeding to capture behavior anyway."

section "Test 7 - Real Ollama Provider Path"
write_task "task_test_ollama" "$ACTIVE_RUN_ID" "Ollama provider test" "reviewer" "main.py"
run_cmd "test07_ollama" bash -lc "cd $PROJECT_ROOT && OLLAMA_MODEL=$OLLAMA_MODEL python3 main.py next --provider ollama"
capture_execution_artifacts "task_test_ollama"

section "Test 8 - Stable Execution From Outside Project Root"
write_task "task_test_outside_root" "$ACTIVE_RUN_ID" "Outside root execution test" "coder" "main.py"
run_cmd "test08_next_outside_root" bash -lc "cd /tmp && python3 $PROJECT_ROOT/main.py next"
capture_execution_artifacts "task_test_outside_root"

section "Done"
log "Acceptance test run complete."
log "Summary file: $SUMMARY"

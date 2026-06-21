#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S %Z')"
LOG_STAMP="$(date '+%Y%m%dT%H%M%S%z')"
LOG_DIR="${REPO_ROOT}/test_logs"
LOG_FILE="${LOG_DIR}/phase_51_local_${LOG_STAMP}.log"

REQUIRED_FILES=(
  "tests/test_phase_51_current_success_validation.py"
  "tests/test_phase_50_recommendation_accept.py"
  "tests/test_phase_49_archival_aware_surfaces.py"
  "tests/test_phase_47_recommendation_resolution.py"
  "tests/test_phase_46_recommendation_outcomes.py"
  "tests/test_phase_44_recommendation_drafts.py"
  "tests/test_phase_43_recommendation_actions.py"
  "tests/test_phase_42_recommendation_summary.py"
  "tests/test_phase_41_recommendations_visibility.py"
  "tests/test_phase_28_recommendation_lifecycle.py"
)

UNITTEST_MODULES=(
  "tests.test_phase_51_current_success_validation"
  "tests.test_phase_50_recommendation_accept"
  "tests.test_phase_49_archival_aware_surfaces"
  "tests.test_phase_47_recommendation_resolution"
  "tests.test_phase_46_recommendation_outcomes"
  "tests.test_phase_44_recommendation_drafts"
  "tests.test_phase_43_recommendation_actions"
  "tests.test_phase_42_recommendation_summary"
  "tests.test_phase_41_recommendations_visibility"
  "tests.test_phase_28_recommendation_lifecycle"
)

compile_status="NOT RUN"
unittest_status="NOT RUN"

print_step() {
  printf '\n[%s] %s\n' "$(date '+%H:%M:%S')" "$1"
}

fail() {
  printf 'ERROR: %s\n' "$1" >&2
  exit 1
}

mkdir -p "${LOG_DIR}"
exec > >(tee -a "${LOG_FILE}") 2>&1

printf '=== Phase 51 Local Validation ===\n'
printf 'Repo root: %s\n' "${REPO_ROOT}"
printf 'Timestamp: %s\n' "${TIMESTAMP}"

print_step "Preflight: checking python3"
command -v python3 >/dev/null 2>&1 || fail "python3 is not available on PATH"
PYTHON_BIN="$(command -v python3)"
printf 'Python executable: %s\n' "${PYTHON_BIN}"
printf 'Python version: %s\n' "$(python3 --version 2>&1)"
printf 'Log file: %s\n' "${LOG_FILE}"

print_step "Resolving and entering repo root"
cd "${REPO_ROOT}"

print_step "Preflight: checking expected directories"
[[ -d "tests" ]] || fail "Required directory missing: tests"

print_step "Preflight: checking required test files"
for relpath in "${REQUIRED_FILES[@]}"; do
  [[ -f "${relpath}" ]] || fail "Required file missing: ${relpath}"
  printf 'Found: %s\n' "${relpath}"
done

print_step "Running py_compile validation"
COMPILE_CMD=(python3 -m py_compile tests/test_phase_51_current_success_validation.py)
printf 'Command: '
printf '%q ' "${COMPILE_CMD[@]}"
printf '\n'

if "${COMPILE_CMD[@]}"; then
  compile_status="PASSED"
  printf 'py_compile step: PASSED\n'
else
  compile_status="FAILED"
  printf 'py_compile step: FAILED\n'
  exit 1
fi

print_step "Running unittest validation"
UNITTEST_CMD=(python3 -m unittest "${UNITTEST_MODULES[@]}")
printf 'Command: '
printf '%q ' "${UNITTEST_CMD[@]}"
printf '\n'

if "${UNITTEST_CMD[@]}"; then
  unittest_status="PASSED"
  printf 'unittest step: PASSED\n'
else
  unittest_status="FAILED"
  printf 'unittest step: FAILED\n'
  exit 1
fi

print_step "Final summary"
printf 'py_compile: %s\n' "${compile_status}"
printf 'unittest: %s\n' "${unittest_status}"
printf 'Overall result: SUCCESS\n'

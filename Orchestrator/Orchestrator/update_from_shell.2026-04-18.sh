#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./update_from_shell.2026-04-18.sh
# or
#   PROJECT_ROOT="$HOME/codex/projects" ./update_from_shell.2026-04-18.sh

if [[ -n "${PROJECT_ROOT:-}" ]]; then
  case "$PROJECT_ROOT" in
    "~") PROJECT_ROOT="$HOME" ;;
    "~/"*) PROJECT_ROOT="$HOME/${PROJECT_ROOT#~/}" ;;
  esac
else
  PROJECT_ROOT="$(pwd)"
fi

PROJECT_ROOT="$(cd "$PROJECT_ROOT" && pwd)"

DOCS_DIR="$PROJECT_ROOT/docs"
BUILD_RULES="$DOCS_DIR/BUILD_RULES.md"
PHASE_INDEX="$DOCS_DIR/PHASE_INDEX.md"
PROJECT_CONTEXT="$DOCS_DIR/PROJECT_CONTEXT.md"
ACTION_LOG="$DOCS_DIR/ACTION_LOG.md"
PROCESS_PROTOCOL="$DOCS_DIR/PROCESS_PROTOCOL.md"

mkdir -p "$DOCS_DIR"
mkdir -p "$PROJECT_ROOT/scripts"

for f in "$BUILD_RULES" "$PHASE_INDEX" "$PROJECT_CONTEXT" "$ACTION_LOG"; do
  if [[ ! -f "$f" ]]; then
    echo "Missing required file: $f" >&2
    exit 1
  fi
done

cp "$BUILD_RULES" "$BUILD_RULES.bak"
cp "$PHASE_INDEX" "$PHASE_INDEX.bak"
cp "$PROJECT_CONTEXT" "$PROJECT_CONTEXT.bak"
cp "$ACTION_LOG" "$ACTION_LOG.bak"

cat > "$PROCESS_PROTOCOL" <<'EOF'
# PROCESS_PROTOCOL.md

## Purpose

This document defines the operating protocol for phase-governed execution, defect handling, audit handling, and process closure.

It exists to keep the build process explicit, synchronized, and bounded as the project becomes more capable.

This document is about **how work is governed**, not about adding product behavior.

---

## Core Process Rules

### 1. Verify Before Fix

A suspected defect must not become a fix document solely because it appears in:
- an audit report
- a conversational suspicion
- a stale snapshot

Before opening a fix, classify the issue as one of:

- confirmed in latest inspected snapshot
- confirmed in latest Codex implementation report
- not confirmed
- downgraded to future hardening
- downgraded to watchlist

A fix should be opened only for a **confirmed defect** or a **confirmed control-surface inconsistency**.

---

### 2. Evidence Precedence

When sources disagree, resolve them in this order:

1. latest directly inspected snapshot
2. latest Codex implementation report
3. latest auditor report
4. conversational memory / assumptions

This precedence should be used explicitly when deciding whether an issue is real, stale, or already resolved.

---

### 3. Intervention Classification

Before drafting work, classify the proposed intervention as one of:

- feature phase
- hardening phase
- code fix
- docs/control-surface fix
- validation-only correction
- watchlist only (no immediate action)

Do not draft a phase or fix until the intended intervention class is clear.

---

### 4. Audit Handling

Auditor output is triage input, not defect truth.

Auditor findings should be used to:
- sharpen attention
- rank pressure points
- distinguish likely fix-now vs hardening vs watchlist

Auditor findings should not automatically create new fixes or phases without confirmation.

---

### 5. Closure Check After Every Phase or Fix

After every implemented phase or fix, check whether the change introduced any of the following:

- stale operator-facing wording
- stale docs/control surfaces
- provenance ambiguity
- weakened boundedness
- hidden routing behavior
- hidden automation creep
- missing regression coverage for the new ladder rung
- newly implied sibling response path or sibling hardening obligation

This closure check should happen before resuming forward growth.

---

### 6. Open-Threads Discipline

The project should maintain a compact live understanding of:

- confirmed open fixes
- confirmed future hardening items
- watchlist items
- pinned next-forward move

This state may be mirrored in conversation, but repo governance should not rely on conversation memory alone.

---

### 7. Snapshot Freshness Discipline

If there has been a meaningful series of changes, prefer:
- a fresh snapshot
- or a fresh Codex implementation report

over older assumptions or older audit conclusions.

Do not let stale evidence drive current decisions.

---

## Issue State Categories

When discussing findings, prefer these categories explicitly:

- suspected issue
- confirmed defect
- docs/control-surface inconsistency
- future hardening candidate
- watchlist item
- resolved / closed

This keeps urgency proportional and reduces accidental overreaction.

---

## Process Principle

The project should harden its process in the same way it hardens its code:

- explicit over implicit
- confirmed over assumed
- bounded over sprawling
- synchronized over stale
- inspectable over conversationally improvised
EOF

export PROJECT_ROOT

python3 <<'PY'
import os
from pathlib import Path

project_root = Path(os.environ["PROJECT_ROOT"]).resolve()
docs = project_root / "docs"

def ensure_block(path: Path, marker: str, block: str, append: bool = True):
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return
    if append:
        if not text.endswith("\n"):
            text += "\n"
        text += "\n" + block.strip() + "\n"
    else:
        text = block.strip() + "\n\n" + text
    path.write_text(text, encoding="utf-8")

build_rules_block = """
## Process Protocol Rules

Codex must also follow `docs/PROCESS_PROTOCOL.md` as governing process behavior.

Additional required rules:

1. Do not open or implement a fix from an audit claim alone.
   First confirm whether the issue is:
   - confirmed in the latest inspected snapshot
   - confirmed in the latest Codex implementation report
   - not confirmed
   - future hardening
   - watchlist

2. Before drafting work, classify the intervention explicitly as one of:
   - feature phase
   - hardening phase
   - code fix
   - docs/control-surface fix
   - validation-only correction

3. Treat auditor findings as triage input, not as automatic defect truth.

4. After every completed phase or fix, perform a closure check for:
   - stale operator-facing wording
   - stale docs/control surfaces
   - provenance ambiguity
   - weakened boundedness
   - hidden routing behavior
   - hidden automation creep
   - missing regression coverage
   - newly implied sibling obligations

5. When evidence sources disagree, prefer:
   1. latest inspected snapshot
   2. latest Codex implementation report
   3. latest auditor report
   4. conversational memory
"""

project_context_block = """
## Process Discipline

This project now requires explicit process discipline in addition to bounded implementation discipline.

That means:

- suspected issues should be confirmed before becoming fixes
- audit findings should be treated as triage input, not automatic truth
- source disagreement should be resolved by evidence precedence
- every completed phase or fix should receive a closure check for stale wording, provenance ambiguity, boundedness drift, hidden routing, hidden automation, and missing regression protection

See:
- `docs/PROCESS_PROTOCOL.md`
"""

phase_index_block = """
## Process Protocol Reference

In addition to this file and `BUILD_RULES.md`, process handling is governed by:

- `docs/PROCESS_PROTOCOL.md`

That protocol defines:
- verify-before-fix discipline
- evidence precedence when sources disagree
- intervention classification
- audit handling rules
- closure checks after every phase or fix
- open-thread discipline
"""

ensure_block(docs / "BUILD_RULES.md", "## Process Protocol Rules", build_rules_block, append=True)
ensure_block(docs / "PROJECT_CONTEXT.md", "## Process Discipline", project_context_block, append=True)
ensure_block(docs / "PHASE_INDEX.md", "## Process Protocol Reference", phase_index_block, append=True)
PY

STAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
ENTRY="- ${STAMP} — Process protocol hardening applied: added docs/PROCESS_PROTOCOL.md and updated BUILD_RULES.md, PHASE_INDEX.md, and PROJECT_CONTEXT.md to codify verify-before-fix, evidence precedence, intervention classification, audit handling, closure checks, and open-thread discipline."

if ! grep -Fq "Process protocol hardening applied" "$ACTION_LOG"; then
  printf '\n%s\n' "$ENTRY" >> "$ACTION_LOG"
fi

echo "Process protocol hardening applied."
echo "Created:  $PROCESS_PROTOCOL"
echo "Updated:  $BUILD_RULES"
echo "Updated:  $PHASE_INDEX"
echo "Updated:  $PROJECT_CONTEXT"
echo "Updated:  $ACTION_LOG"
echo
echo "Backups created with .bak suffix."

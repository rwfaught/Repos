# GPT-5.6 Experimental Fork Status

## Boundary and warning

This is the continuity record for the experimental fork boundary
`GPT56_EXPERIMENTAL_FORK_CONTINUITY_AND_OPEN_THREADS_DOC_UPDATE`.

This document records experimental-fork state only. It is not authoritative
main ratification, does not select a product wedge, and does not establish
production readiness. The authoritative main line remained untouched during
this fork sequence at `a882bb960f9686f62bd316276716fe2047141f52`.

## Current fork identity

- Branch: `experiment/gpt56-local-ai-consulting-wedge`
- HEAD at this documentation boundary:
  `e851f906c7622c8d684f786777d6e301eba056ee`
- Fork scope: GPT-5.6/Luna local-model reasoning and the bounded local-AI
  consulting/dossier-case proving history.
- Product posture: no first product wedge selected; Phase 387 remains parked.

## Accepted milestones and ratified proof levels

### `363e84e` — coordinator-to-owner-review packet bridge

Accepted fork progress includes the coordinator-to-owner-review packet bridge,
neutral dossier/case readback, and operator format. This is deterministic
control/readback evidence; it does not prove model execution, worker dispatch,
or product authorization.

### `3f1c9f7` — local-model contract and disabled provider seam

Accepted as fork local-model contract/provider-seam progress. The contract
defines structured intake and deterministic validation/fallback behavior; the
disabled/static provider seam does not itself invoke a model.

### Live WSL/zsh llama.cpp TQ3 smoke

The prior live smoke produced one structured JSON interpretation candidate
through `llama-completion` with `-no-cnv` using
`llama.cpp-tq3 + Qwen3.6-27B-TQ3_4S` in local WSL/zsh. The accepted evidence
label is:

`PASS_RUNTIME_SMOKE_WITH_JSON_CANDIDATE / NON_STRICT_JSON_RAW_OUTPUT`

The raw output was not strict JSON-only: it included empty `<think></think>`
tags and `[end of text]`. This is a narrow runtime smoke result, not a
durable provider or semantic-correctness result.

### `e851f90` — deterministic normalization

Provisionally accepted as normalization-contract progress based on the Worker
report and focused tests. The change adds deterministic handling for embedded
local-model JSON output while retaining conservative rejection of malformed,
ambiguous, multiple-candidate, and authority-shaped output.

## Failed and partial evidence attempts

### `GPT56_LOCAL_QWEN_NORMALIZATION_RUNTIME_EVIDENCE_RELAY_READONLY`

- Disposition: `FAIL_WITH_USEFUL_EVIDENCE`.
- WSL resolved `python3` at `/usr/bin/python3`.
- Experimental branch and HEAD were confirmed at
  `e851f906c7622c8d684f786777d6e301eba056ee`.
- `normalize_local_model_output(raw_output: str)` was found and invoked.
- The tested raw artifact was normalized as
  `rejected_multiple_json_candidates`.
- Reason: `more_than_one_top_level_json_object`.
- Contract validation was not attempted because normalization rejected the raw
  output first.

This does not prove `e851f90` is broken. It shows that the tested raw artifact
did not match the known-good prior shape and was conservatively rejected.
The Relay failure and its useful evidence must remain visible in future
handoffs.

## Open threads

1. Establish one clean normalization evidence boundary using either the exact
   known-good prior raw-output shape or a fresh, tightly bounded
   `llama-completion -no-cnv` output against `e851f90` normalization.
2. Keep the next evidence command minimal and contract-focused; do not broaden
   into rediscovery, provider integration, coordinator looping, or product
   evaluation.
3. Reconcile any future fork evidence with current repo docs and live git
   state before CTO/coordinator review.
4. Preserve the separation between experimental evidence and authoritative-main
   ratification before any promotion or merge decision.

## Explicit non-proofs

This fork record does not prove:

- strict JSON-only model output;
- durable provider integration;
- an end-to-end coordinator loop using a live local model;
- worker dispatch or task execution;
- persistence implementation;
- semantic correctness, customer value, or product readiness;
- production readiness;
- a selected first product wedge;
- Phase 387 resumption;
- authoritative main ratification.

Runtime/provider/model work remains unproven except for the narrow, prior
runtime-smoke statement recorded above. No claim here authorizes runtime,
provider, model, WSL, Ollama, Hermes, OpenClaw, worker, production, or product
execution.

## Residue and validation posture

The experimental fork retains dirty generated-data residue: one tracked
generated-data modification and 312 untracked generated-data files. This
boundary does not clean, delete, archive, move, stage, commit, or push that
residue. The full test suite is not green and was not rerun for this latest
docs-only boundary.

## Recommended next boundaries

1. `GPT56_LOCAL_QWEN_NORMALIZATION_KNOWN_GOOD_SHAPE_EVIDENCE_READONLY` —
   replay the exact known-good raw shape through the existing normalizer and
   report normalization plus contract-validation results, without changing
   source or tests.
2. If replay is unavailable, a separately authorized minimal
   `llama-completion -no-cnv` evidence boundary may capture one fresh raw
   artifact and pass it to the normalizer. It must report raw-shape limits and
   must not imply strict JSON-only output.
3. Only after CTO/coordinator review of that evidence should a new boundary be
   ranked for any provider-seam or coordinator-loop work. No product wedge is
   selected by this record.

## Coordination and acceptance

- Coordination-doc update needed: YES — this new fork-specific status record
  should be named by future CTO/coordinator startup or re-entry packets when
  the GPT-5.6 experimental fork is in scope.
- Worker/Codex evidence is not CTO/coordinator acceptance. Promotion to
  authoritative main requires a separate explicit review and boundary.

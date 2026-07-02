# Packet To Patch Bridge Operator Runbook

## Scope

This runbook covers the packet-result-to-patch-proposal bridge proven by
Phases 288-291.

The bridge is local, deterministic, and evidence-only. It does not create an
authorized patch proposal, does not authorize apply, and does not apply a
patch.

## Packet Result Acceptance

Packet result acceptance means an operator recorded `accepted` for a completed
packet result with a non-empty note/reason after current-success review.

Acceptance is not patch authorization. Acceptance is not semantic correctness
proof. Acceptance is not production readiness proof.

Required acceptance evidence:

- packet id
- run id
- task id
- execution artifact id/path
- verifier result path
- current-success review classification
- latest operator decision record
- operator decision value
- operator decision timestamp
- operator note/reason

## Eligibility Readback

Phase 288 eligibility readback returns one of:

- `eligible`
- `ineligible`
- `blocked`

Eligibility requires:

- path-safe task id
- completed packet result evidence
- existing execution artifact path
- existing verifier result path
- current-success classification `completed_current_state_success`
- latest accepted operator decision
- non-empty operator note/reason
- decision links back to the same task/artifact/verifier/current-success
  evidence
- no provider/model/runtime/platform execution claim
- no semantic correctness claim as proof
- no autonomous AI coding claim as proof
- no production-readiness claim as proof
- structured patch-candidate evidence

Eligibility is not patch authorization and does not create a patch proposal.

## Candidate Artifact Creation

Phase 289 candidate creation accepts only Phase 288 `eligible` readback plus a
non-empty candidate note/reason.

The candidate artifact status is `candidate_only`.

Candidate artifacts preserve:

- candidate id
- source packet id
- source run id
- source task id
- source execution artifact id/path
- source verifier result path
- current-success review reference
- operator decision record id/path
- eligibility readback
- proposed patch evidence payload when present
- missing or ambiguous patch fields
- caveats
- non-proofs
- timestamp
- no-apply/no-authorization flags

Candidate creation is not patch authorization and is not a patch apply request.

## Promotion / Rejection / Defer Gate

Phase 290 operator promotion records support:

- `promote_to_patch_proposal_candidate_ready`
- `reject_candidate`
- `defer_candidate`

Promotion requires a valid `candidate_only` artifact and a non-empty operator
note/reason.

Accepted packet decisions alone cannot promote a candidate. Candidate
promotion is not patch apply authorization and does not create a draft patch
proposal in the current source state.

## Where Patch Proposal Begins

The existing patch proposal spine begins at the separately proven patch
proposal modules and phase boundaries. The packet bridge does not automatically
enter that spine.

A later explicit boundary is required to connect a promoted candidate to a
draft or authorized patch proposal artifact.

## Where Patch Apply Remains Blocked

Patch apply remains blocked until a later explicit apply-authorization boundary
proves otherwise.

The following do not authorize apply:

- packet result acceptance
- eligibility readback
- candidate artifact creation
- candidate promotion
- candidate rejection
- candidate defer

## Timestamps

Operator command batches should print:

- start timestamp
- end timestamp
- elapsed time
- PASS/FAIL lines
- visible artifact paths

## Shell Expectations

Use native PowerShell syntax when running from Windows PowerShell.

Use zsh/bash syntax only from zsh/bash. When calling Windows PowerShell from
WSL, use `powershell.exe` explicitly and preserve Windows paths exactly.

Operator-facing PowerShell batches should avoid `exit`, avoid `throw` for
expected boundary failures, accumulate failures, and complete naturally.

## Non-Proofs

The packet-to-patch bridge does not prove:

- semantic correctness
- autonomous AI coding
- model-backed generation
- provider/model/runtime execution
- runtime/platform behavior
- production readiness
- service/API/UI/dashboard/auth/deployment behavior
- scheduler/reminder/connector behavior
- `general_answer` resumption
- platform/OpenClaw/Hermes/LightRAG behavior
- cleanup/delete/archive authority
- patch apply authorization from acceptance, eligibility, candidate creation,
  or promotion
- integrated production patch workflow readiness

## Source ZIP Hygiene Caveat

The operator `srczip` flow may include generated `__pycache__` or `.pyc`
entries depending on packaging. Product capsule proof should come from the
official product capsule refresh output, not source upload hash alone.

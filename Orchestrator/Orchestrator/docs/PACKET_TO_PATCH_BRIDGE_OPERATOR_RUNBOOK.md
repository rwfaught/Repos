# Packet To Patch Bridge Operator Runbook

## Scope

This runbook covers the packet-result-to-patch-proposal bridge proven by
Phases 288-291 and the promoted-candidate-to-draft-proposal-to-authorization
eligibility bridge proven by Phases 294-296.

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
promotion is not patch apply authorization.

## Draft Patch Proposal Artifact

Phase 294 can create a `draft_patch_proposal` artifact from a promoted
`candidate_only` artifact when the promotion record, candidate evidence, current
success reference, accepted packet evidence, operator decision reference, and
structured patch evidence are complete and consistent.

The draft proposal artifact is marked:

- `draft_only`
- `not_authorized_for_apply`
- `not_applied`

Draft patch proposal artifacts preserve:

- draft proposal id
- source candidate id
- source promotion record id
- source packet id
- source run id
- source task id
- source execution artifact id/path
- source verifier result path
- current-success review reference
- operator decision record id/path
- Phase 288 eligibility reference
- Phase 289 candidate reference
- Phase 290 promotion reference
- structured patch payload
- linked evidence
- caveats
- non-proofs
- timestamp
- no-apply/no-authorization flags

Draft creation is not apply authorization. Draft creation does not apply a
patch. Draft creation does not prove semantic correctness, autonomous AI
coding, model/provider/runtime execution, or production readiness.

## Authorization Eligibility Readback

Phase 296 authorization eligibility readback returns one of:

- `authorization_eligible`
- `authorization_ineligible`
- `authorization_blocked`

Authorization eligibility requires:

- draft proposal exists
- draft proposal status is `draft_only`
- draft proposal is `not_authorized_for_apply`
- draft proposal is `not_applied`
- draft links to promoted candidate
- promoted candidate links to candidate artifact
- candidate links to accepted packet result
- accepted packet result links to task/artifact/verifier/current-success/
  operator acceptance
- all evidence links are consistent
- structured patch payload is present and unambiguous
- no residue guard blocking condition is present, if guard integration exists
- no provider/model/runtime/platform execution claim is present
- no semantic correctness proof claim is present
- no production-readiness claim is present
- no existing apply authorization exists
- no apply has already occurred

The readback includes:

- draft proposal id
- authorization eligibility status
- reason code
- exact missing evidence list
- linked evidence list
- caveats
- non-proofs
- explicit no-authorization statement
- explicit no-apply statement
- timestamp

Authorization eligibility is not authorization. It only determines whether the
draft proposal has enough structured evidence for a later explicit operator
apply-authorization decision.

## Operator Apply-Authorization Record

Phase 299 can persist an operator apply-authorization record after a clean
Phase 296 authorization eligibility readback.

Supported decisions are:

- `authorize_apply`
- `reject_apply_authorization`
- `defer_apply_authorization`

`authorize_apply` authorizes a later bounded apply attempt only. It does not
apply the patch, does not create an apply result, does not finalize the task,
does not prove semantic correctness, and does not prove production readiness.

Reject and defer decisions preserve the operator decision and reason without
authorizing apply.

Phase 300 hardens negative edges around missing, mismatched, unsafe,
duplicate, rejected, deferred, and smuggled authorization evidence. It also
preserves that no apply execution, apply result, or finalization occurs.

## Authorization Status Readback

Phase 301 readback shows:

- draft proposal id
- latest authorization decision
- authorization id
- authorization timestamp
- operator authorization note/reason
- linked evidence chain
- whether authorization is active, rejected, deferred, or blocked
- `patch_not_applied`
- `no_apply_execution_in_this_phase`
- caveats
- non-proofs

The readback is for operator visibility before a future bounded apply
boundary. It is not apply execution.

## Where Patch Proposal Begins

The existing patch proposal spine begins at the separately proven patch
proposal modules and phase boundaries. The packet bridge and draft proposal
bridge do not automatically enter that spine.

A later explicit boundary is required to create actual apply authorization.

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
- draft patch proposal creation
- authorization eligibility readback
- operator apply-authorization status readback

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
- promotion, draft creation, or authorization eligibility readback
- integrated production patch workflow readiness
- Backbone V0
- apply-authorization readback as apply execution

## Source ZIP Hygiene Caveat

The operator `srczip` flow may include generated `__pycache__` or `.pyc`
entries depending on packaging. Product capsule proof should come from the
official product capsule refresh output, not source upload hash alone.

Generated product capsule ZIP files under the outer Git root are packaging
artifacts. They are not product source, docs, tests, data records, manifests,
or proof of runtime behavior.

Use the official product zipper for capsule proof:

`C:\Users\accou\Desktop\Repos\Powershell Scripts\Zip-OrchestratorProductRepo.ps1`

## Backbone V0 Open Thread

The control loop is approaching Backbone V0 criteria, but Backbone V0 remains
open. Still missing are actual apply authorization, bounded apply,
apply-result verification, finalization, and domain separation.

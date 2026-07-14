# Experimental Branch Reconciliation Ledger

Boundary: `EXPERIMENT_RECONCILIATION_LEDGER_DOCS_ONLY`

Mode: `DOCS_ONLY_CURRENT_MAIN_RECONCILIATION_LEDGER_AND_COORDINATION_ALIGNMENT`

Status: `EXPERIMENTAL_BRANCH_RECONCILIATION_LEDGER_CREATED_PENDING_COMMIT_PUSH_AND_RETENTION_DECISION`

## Purpose and Authority

This is the durable final-disposition ledger for
`experiment/gpt56-local-ai-consulting-wedge` against authoritative `main`.
It records accepted review outcomes for every commit unique to the experimental
branch. It does not merge branches, adopt experimental source, select a
provider or model, prove runtime or semantic behavior, authorize cleanup,
branch deletion, worktree removal, or product-work resumption.

## Repository Topology and Count Reconciliation

- Authoritative repository/worktree: `rwfaught/Repos` at
  `C:\Users\accou\Desktop\Repos`, branch `main`.
- Authoritative product root: `Orchestrator/Orchestrator`.
- Authoritative HEAD at ledger creation:
  `ea818195add622dc0727b00bb4fafb1bd5743d4c`.
- Experimental linked worktree:
  `C:\Users\accou\Desktop\Repos\Orchestrator_gpt56_experiment`.
- Experimental branch/HEAD:
  `experiment/gpt56-local-ai-consulting-wedge` at
  `64125b9`.
- Verified merge base: `a882bb960f9686f62bd316276716fe2047141f52`.
- Comparison basis:
  `git rev-list --reverse main..experiment/gpt56-local-ai-consulting-wedge`.
- Verified experiment-exclusive commit count: **16**.

The prior sixteen-commit count is correct. The apparent seventeenth grouped
item was the documentation-reconciliation topic, not an additional
experiment-exclusive Git commit. Live history contains no separate
experiment-exclusive first-revenue documentation commit. The current-main
documentation replacement is the independent
`ee705a8649889890dea4fee31598dc80c23dbb29`
(`docs: record first revenue proving use case`). Therefore this ledger has
exactly the sixteen rows emitted by the comparison command, with no forced
extra row and no duplicate count.

The experimental linked worktree and its pre-existing dirty/generated residue
remain preserved and untouched. No retention, archival, cleanup, removal, or
deletion decision is recorded here.

## Reconciliation Method

Wholesale merge and bulk cherry-pick were rejected. No patch-equivalence route
was accepted. Each experiment-exclusive commit received one individual
disposition after comparison with current-main architecture and tests. Adoption
required a concrete, provider-neutral, generally reusable capability gap
compatible with current intake/admission and the canonical alpha runtime. No
remaining adoption-grade gap was found.

## Disposition Vocabulary

- `ADOPT_CANDIDATE`: a narrow, presently missing provider-neutral capability
  qualifies for a separately authorized adoption boundary.
- `ALREADY_COVERED`: current main already provides the behavior, including an
  independent current-main reimplementation where stated.
- `EXPERIMENTAL_RESEARCH_PRESERVED`: retain historical evidence or concepts;
  do not adopt source.
- `OBSOLETE_OR_SUPERSEDED`: later experimental or current-main documentation
  supersedes the material.
- `REQUIRES_CTO_REVIEW`: classification cannot safely be completed from the
  accepted evidence.

No commit received `ADOPT_CANDIDATE` or `REQUIRES_CTO_REVIEW`.

## Commit-by-Commit Final Dispositions

| SHA | Subject / group | Substantive behavior | Final disposition | Direct source adopted | Concept reimplemented or retained | Current-main replacement or equivalent | Remaining non-proofs / merge note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `70c218ca9fc6a1efbed305b678160c08e92e6053` | Add local AI consulting sandbox audit flow — consulting | Fictional audit intake, review gate, report, and dossier bridge. | `EXPERIMENTAL_RESEARCH_PRESERVED` | No | Yes: manual dossier/template concepts only. | Neutral dossier/case mapping and task-readiness seams. | No client proof, source/CLI/classifier adoption, or pilot-template work; consulting source would lock in a use case. |
| `fcf9ceae42b73f5485954dae5e7593676aab7643` | Autonomous fork campaign: add consulting operator readback — consulting | Four fictional scenarios, campaign packet, operator readback, and CLI. | `EXPERIMENTAL_RESEARCH_PRESERVED` | No | Yes: owner-review and deferred-automation template ideas. | Neutral packet/readiness surfaces. | No workflow, CLI, integration, or runtime adoption; campaign code is use-case-specific. |
| `53dcffa467a259183b6252bb4b558a9ed53cd4d9` | Autonomous fork campaign: improve operator review flow — consulting | PM-readable summaries and markdown review refinements. | `EXPERIMENTAL_RESEARCH_PRESERVED` | No | Yes: report-section ideas only. | Current neutral readback/operator-review surfaces. | No source/CLI adoption or client-value/production proof. |
| `ec7aec81aa7fe05f371dbd2565203e1d62a938c1` | Add deterministic capability routing triage — structured assessment | Fixture-based capability factors and executor recommendations. | `ALREADY_COVERED` | No | Yes: general concepts independently reimplemented. | `ea818195add622dc0727b00bb4fafb1bd5743d4c` (`feat: add structured capability assessment`). | Reimplementation uses current intake/admission interfaces and selects no provider, worker, or route. |
| `ec2db4bbf9a041eeed9e689a60cb0c1028a5f657` | Connect objectives to routing and owner packets — structured assessment | Objective-to-route packet loop and owner-packet CLI. | `ALREADY_COVERED` | No | Yes: assessment, clarification, blocking, and review concepts independently reimplemented. | `ea818195add622dc0727b00bb4fafb1bd5743d4c`; current intake/admission pipeline. | No experimental routing/CLI adoption, dispatch, or authorization. |
| `682c158099d9a8e8f0c27e7137ef1883195bfbc7` | Add dry coordinator agent loop architecture — coordinator review | Alternate dry coordinator, worker, review, and closeout architecture. | `ALREADY_COVERED` | No | Yes: bounded review/control concepts remain represented. | Current canonical alpha lifecycle and structured admission/review posture. | No second coordinator/admission spine, runtime, dispatch, or autonomy proof. |
| `363e84ef7b3f615082541993fde81b7dc777cdf9` | Autonomous fork: connect coordinator operator review packet — coordinator review | Operator packet and markdown over the dry coordinator loop. | `ALREADY_COVERED` | No | Yes: operator-facing review/readback concepts only. | Current packet, review, and reconciliation surfaces. | No experimental coordinator or CLI adoption; no execution authority. |
| `3f1c9f79d14594cadccc251368d04d1ea1066741` | Add local-model reasoning contract seam — local-model substrate | Model-shaped request/result contract, stubs, and coordinator integration. | `EXPERIMENTAL_RESEARCH_PRESERVED` | No | Yes: strict input and non-authority concepts retained historically. | Current structured capability assessment and canonical alpha runtime. | No local-model ingress, provider registry, prompt contract, or parallel coordinator adoption. |
| `e851f906c7622c8d684f786777d6e301eba056ee` | Normalize embedded local-model JSON output — local-model substrate | Conservative extraction of one JSON candidate from raw model text. | `EXPERIMENTAL_RESEARCH_PRESERVED` | No | Yes: raw-evidence preservation and ambiguity quarantine retained as research. | Current structured intake rejects raw-model ingress by design. | No raw-output admission contract; parser adoption would reopen provider intake architecture. |
| `9cd460eae123819b929c0fb3a10243ef366ed971` | Record GPT-5.6 experimental fork status — obsolete status | Initial experimental-fork continuity/status record. | `OBSOLETE_OR_SUPERSEDED` | No | No. | Later experimental status evidence and current-main current-state docs. | Historical evidence remains; this status record is not current adoption authority. |
| `79ba35db033496b87750a80e07b28ff59aa4dbc4` | Record Qwen known-good shape normalization evidence — local-model substrate | Documents/tests a Qwen wrapper/output shape. | `EXPERIMENTAL_RESEARCH_PRESERVED` | No | Yes: provider/model evidence retained historically only. | Current provider-evidence/non-proof posture. | No Qwen selection, local-model integration, or general parser proof. |
| `7de018cb59eb5abda88274b88a3115385c765e50` | Accept whitespace-only multiline think wrappers — local-model substrate | Accepts a narrow `<think>` wrapper shape in the parser. | `EXPERIMENTAL_RESEARCH_PRESERVED` | No | Yes: conservative parsing lesson retained historically. | Current structured-input-only admission posture. | No model-specific wrapper rule in the neutral core. |
| `927a41e484c6e83b89ea93aefa57e5d26446cfc1` | Integrate bounded local provider advisory seam — advisory adapter | Injected transport, raw-output references, fallback, and coordinator integration. | `EXPERIMENTAL_RESEARCH_PRESERVED` | No | Yes: evidence preservation, quarantine, and fallback concepts only. | Current structured assessment and canonical alpha worker seam. | No advisory provider, transport, or parallel coordinator/admission adoption. |
| `e69dcea7647ff13947451f0843ec187754a05bf4` | Align local model advisory prompt schema — advisory adapter | Narrows model prompt categories and uncertainty fields. | `EXPERIMENTAL_RESEARCH_PRESERVED` | No | Yes: strict-schema principle retained historically. | Current explicit structured capability assessment. | No prompt-shape contract or model-produced intake in current main. |
| `5526034397e3460f5ca886495e6370d2a1ac9c51` | Preserve provider-neutral native Codex advisory repair — advisory adapter | Native Codex WSL/subscription adapter, JSONL extraction, and transport/auth classification. | `EXPERIMENTAL_RESEARCH_PRESERVED` | No | Yes: historical transport/failure evidence only. | Canonical alpha `SubprocessWorkerProvider` seam for authorized coding tasks. | No Codex/WSL/auth/provider integration, selection, or production claim. |
| `64125b9909b7e72b7d7d3c542caac3274def086b` | Admit safe bounded clarification outputs — clarification | Allows bounded clarification under the experimental model contract. | `ALREADY_COVERED` | No | Yes: safe clarification posture is covered by structured assessment. | `ea818195add622dc0727b00bb4fafb1bd5743d4c`; current clarification-required outcome. | Experimental model-contract source remains preserved; no raw-model admission or execution authority. |

Every commit in the verified exclusive history appears once and only once in the
table above.

## Accepted Group Conclusions

### Documentation Reconciliation

Current-main documentation reconciliation was independently recorded in
`ee705a8649889890dea4fee31598dc80c23dbb29`. It is not an additional
experiment-exclusive commit and does not authorize product implementation.

### Structured Capability Assessment

The two experimental routing commits supplied useful concepts, but current main
independently reimplemented the general provider-neutral assessment against its
intake/admission interfaces. No experimental source or CLI was ported.

### Clarification and Coordinator Review

Safe clarification is covered by current-main structured assessment. The dry
coordinator/operator-review architecture remains historical research because a
second coordinator/admission spine is not authorized.

### Consulting Experiment

The consulting implementation is retained only for template/manual-workflow
concepts. No source, CLI, fixed classifier, or pilot-template work is adopted.

### Advisory Adapter and Local-Model Substrate

Raw-evidence preservation, strict validation, ambiguity quarantine,
deterministic fallback, and non-authority of model output are preserved as
historical concepts. No provider integration, raw-model ingress, prompt or
wrapper assumption, local-model runtime path, or alternate coordinator spine
is adopted.

### Obsolete Status Material

The initial experimental status commit is superseded by later experimental
evidence and current-main documentation; its historical evidence is not erased.

## Current-Main Adoption Summary

Direct experimental-source adoption: **none**.

Independent current-main reimplementation: the general structured capability
assessment in `ea818195add622dc0727b00bb4fafb1bd5743d4c`, and the
first-revenue proving-use-case documentation reconciliation in
`ee705a8649889890dea4fee31598dc80c23dbb29`.

Already-covered behavior: clarification and coordinator/operator-review control
concepts through current-main structured admission, review, and canonical
lifecycle surfaces. Historical concept preservation does not mean source
copying or source adoption.

## Remaining Non-Proofs

- No generalized provider/model competence or provider/model selection.
- No raw-model-output admission contract, local-model production path, or
  advisory-provider integration.
- No production readiness, product-market fit, or final product-wedge
  selection.
- No consulting pilot-template implementation or product-work resumption.
- No branch/worktree cleanup, retention decision, deletion authorization, or
  proof that experimental dirty residue is safe to delete.

## Preservation Posture and Campaign Status

The experimental branch and linked worktree remain preserved. Their dirty and
generated residue remains untouched. Retention, archival labeling, worktree
removal, and deletion decisions belong to a later CTO/coordinator boundary
after this ledger is committed and pushed.

All experiment-exclusive commits now have final dispositions, but the wider
split-repository campaign is not closed: this ledger still requires commit and
push, followed by an explicit retention and campaign-closure decision.

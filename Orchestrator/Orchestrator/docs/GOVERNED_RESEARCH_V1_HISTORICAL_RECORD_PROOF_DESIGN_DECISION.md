# Governed Research V1 Historical-Record Proof Design Decision

## Status and Authority

`DOCUMENT_CLASS=DURABLE_CTO_PROOF_DESIGN_DECISION`

`PROOF_DOMAIN_SELECTION=CTO_RATIFIED`

`SELECTION_CONFIDENCE=HIGH`

This CTO-ratified record selects and designs the first bounded public-source
proof posture for Governed Research V1. It records proof design and
coordination only. It does not collect sources, answer the selected question,
prepare a source packet, implement behavior, or authorize proof execution.

## Relationship to Earlier Decisions

This decision follows the durable direction and dossier-pause decision, the
cross-domain generality audit, and the bounded Governed Research V1 application
design decision. It supersedes their current planning posture that the public
source proof domain was not yet selected; that former posture remains an
accurate historical description of those earlier decisions.

The existing design's application-layer boundary, adapter-mediated reuse,
provenance limits, abstention posture, and separation of recommendation from
human disposition remain in force.

## Selected Domain, Question, Scope, and Exclusions

`SELECTED_PROOF_DOMAIN=PUBLIC_HISTORICAL_RECORD_CLAIM_BRIEF`

Selected bounded question:

> Did the ceremonial joining of the Union Pacific and Central Pacific railroads at Promontory Summit on May 10, 1869, establish an immediately continuous coast-to-coast rail route in the United States, or does the historical record require a narrower description of what was completed that day?

The proof will distinguish the May 10 ceremony from immediately continuous
operational rail travel. It remains limited to the factual scope of the event
and connected infrastructure. It excludes cultural significance, economic
impact, labor history, Indigenous history, political symbolism, legal
interpretation, and broad railroad history. The proof may reach a supported,
qualified, conflicting, insufficient-evidence, or abstaining result; it does
not assume the familiar public account is false.

## One Corpus and Diagnostic Variants

`TARGET_CORPUS_SIZE=6`

`MINIMUM_CORPUS_SIZE=5`

`MAXIMUM_CORPUS_SIZE=7`

`ONE_REAL_BOUNDED_CORPUS=REQUIRED`

`SUPPORTED_OR_QUALIFIED_END_TO_END_PATH=REQUIRED`

`ABSTAINING_OR_BLOCKED_DIAGNOSTIC_VARIANT=REQUIRED`

`SECOND_FULL_REAL_CORPUS=NOT_REQUIRED`

One real bounded corpus, plus the required supported-or-qualified and
abstaining-or-blocked diagnostic variants, is the planned proof shape. The
corpus must not expand merely to eliminate uncertainty.

## Corpus and Source-Category Posture

The finite corpus plan requires:

1. a contemporaneous official or near-official event record;
2. an independent contemporaneous newspaper, telegraph, railroad, or eyewitness record;
3. a public institutional historical interpretation;
4. an independent scholarly or university-affiliated treatment;
5. a source directly addressing operational network continuity or remaining gaps; and
6. an optional contrasting retrospective broad-completion account.

Minimum corpus posture:

```text
PRIMARY_OR_CONTEMPORANEOUS_SOURCES>=2
SECONDARY_INTERPRETIVE_SOURCES>=2
OPERATIONAL_CONTINUITY_SOURCE>=1
INDEPENDENT_ORIGINATING_INSTITUTIONS>=3
```

Every source-plan category must be recorded as `SATISFIED`, `UNAVAILABLE`,
`SUBSTITUTED`, or `EXPLICIT_GAP`.

## Provenance, Claims, and Typed Evidence

Each source must carry stable identity; title or precise description; origin or
publisher; publication, creation, or version date when available; retrieval
date; public locator; source type; primary, contemporaneous, or secondary
posture; access, transcription, reproduction, or version limits; source-plan
category; operator selection rationale; and evaluator identity and date.

Each material claim must carry stable identity; exact proposition; quotation,
paraphrase, summary, data extraction, or inference posture; support status;
typed evidence associations; useful locator; qualification and scope; relevant
contradiction and limitation links; and explicit unsupported status where
applicable.

Evidence associations remain typed rather than treated as truth. Source
evaluation remains multidimensional and human-owned.

`PHASE_5_PROVENANCE=INCOMPLETE`

`GENERALIZED_PHASE_6=INCOMPLETE`

The later proof will not establish complete provenance, authenticity,
completeness, reproducibility, source quality, extraction correctness, or
Phase 5 completion.

## Outcomes, Recommendation, and Disposition

Permitted terminal outcomes are:

```text
SUPPORTED_CONCLUSION
QUALIFIED_CONCLUSION
CONFLICTING_EVIDENCE
INSUFFICIENT_EVIDENCE
NO_CONCLUSION
NO_RECOMMENDATION
LIMITED_RECOMMENDATION
```

`ABSTENTION=FIRST_CLASS_SUCCESSFUL_OUTCOME`

`RECOMMENDATION=OPTIONAL`

`CANDIDATE_RANKING=NOT_REQUIRED`

Any recommendation is limited to careful wording or characterization and is
not operational authorization. Findings and any recommendation remain separate
from final human disposition.

## Persistence and Proof-Success Criterion

`PERSISTENCE_NOT_REQUIRED_FOR_FIRST_PROOF`

`LIKELY_LATER_PROOF_POSTURE=FIXTURE_DRIVEN_SOURCE_TEST_PROOF`

The proposed proof-success classification is:

`COMPLETED_GOVERNED_RESEARCH_V1_HISTORICAL_RECORD_CLAIM_BRIEF_SOURCE_TEST_PROOF_WITH_EXPLICIT_PROVENANCE_LIMITS_AND_SUPPORTED_OR_ABSTAINING_HUMAN_DISPOSITION`

The later proof must demonstrate one bounded question and explicit operational
definition; a finite five-to-seven-source plan; stable source and claim
identities; minimum provenance; multidimensional human-owned source evaluation;
typed evidence associations; at least one genuine qualification, contradiction,
uncertainty, or gap from the supplied corpus; deterministic structural
validation; supported, qualified, conflicting, insufficient, or abstaining
completion; recommendation separate from final human disposition; no dossier
candidate, prioritization, or readiness requirement; no provider/model or
autonomous-analysis claim; and explicit provenance and capability non-proofs.

This record does not satisfy that criterion.

## Evidence Preparation and Next Gate

`EVIDENCE_PREPARATION_ACTOR=SPECIALIST`

`EVIDENCE_PREPARATION_SEPARATE_FROM_IMPLEMENTATION=TRUE`

`SOURCE_COLLECTION_MUST_PRECEDE_IMPLEMENTATION_DECISION=TRUE`

`CTO_SOURCE_AND_CLAIM_PACKET_REVIEW_REQUIRED=TRUE`

`MANUAL_VS_SOURCE_TEST_PROOF_DECISION=DEFERRED_PENDING_PREPARED_EVIDENCE`

`SOURCE_COLLECTION_NEXT_CANDIDATE=YES`

`SOURCE_COLLECTION_AUTHORIZED_BY_THIS_RECORD=FALSE`

The next gate is CTO/coordinator review and ratification of this design, then a
separately issued Specialist evidence-preparation boundary. Source preparation,
documentary/manual analysis, fixture or source/test proof, application
implementation, neutral-core admission, and productionization are separate
activities and require their own authorization.

## Explicit Lockouts and Non-Proofs

```text
PUBLIC_SOURCE_COLLECTION_AUTHORIZED=FALSE
PUBLIC_SOURCE_PROOF_AUTHORIZED=FALSE
HISTORICAL_QUESTION_ANSWERING_AUTHORIZED=FALSE
SOURCE_PACKET_PREPARATION_AUTHORIZED=FALSE
FIXTURE_CREATION_AUTHORIZED=FALSE
SOURCE_TEST_IMPLEMENTATION_AUTHORIZED=FALSE
RESEARCH_IMPLEMENTATION_AUTHORIZED=FALSE
PROVIDER_MODEL_EXECUTION_AUTHORIZED=FALSE
PERSISTENCE_ADOPTION_AUTHORIZED=FALSE
NEUTRAL_CORE_ADMISSION_AUTHORIZED=FALSE
PHASE_5_PROVENANCE_COMPLETION=FALSE
GENERALIZED_PHASE_6_COMPLETION=FALSE
PRODUCT_WEDGE_SELECTION_AUTHORIZED=FALSE
PRODUCTIONIZATION_AUTHORIZED=FALSE
```

This decision does not prove historical truth, source quality, corpus
completeness, authenticity, reproducibility, extraction correctness,
evaluation quality, analytical correctness, recommendation correctness,
research competence, implementation readiness, provider/model capability,
neutral-core suitability, product usefulness, product-wedge suitability, or
production readiness.

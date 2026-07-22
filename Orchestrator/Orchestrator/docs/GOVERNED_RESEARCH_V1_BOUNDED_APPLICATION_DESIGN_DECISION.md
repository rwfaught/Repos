# Governed Research V1 Bounded Application Design Decision

## Status and Authority

`DOCUMENT_CLASS=DURABLE_CTO_APPLICATION_DESIGN_DECISION`

`GOVERNED_RESEARCH_V1_BOUNDED_DESIGN=COMPLETED_CTO_RATIFIED`

`GOVERNED_RESEARCH_V1_PROOF_PLANNING_GATE=READY`

`PUBLIC_SOURCE_PROOF_DOMAIN=NOT_YET_SELECTED`

`PUBLIC_SOURCE_PROOF_AUTHORIZED=FALSE`

`RESEARCH_IMPLEMENTATION_AUTHORIZED=FALSE`

This CTO-ratified decision governs bounded application design and readiness to
plan a proof. It does not authorize implementation, public-source proof
execution, source collection, or research execution.

Specialist source classification:
`SPECIALIST_GOVERNED_RESEARCH_V1_BOUNDED_DESIGN_COMPLETE_WITH_NAMED_GAPS`.

CTO-ratified classification:
`PASS_GOVERNED_RESEARCH_V1_BOUNDED_APPLICATION_DESIGN_CTO_RATIFIED`.

## V1 Objective and Explicit Non-Goals

Governed Research V1 is a small supervised research-work application operated
by a knowledgeable human for one bounded, public, non-sensitive question. It
uses a finite caller-supplied or caller-approved corpus and can represent a
supported conclusion, qualified conclusion, conflict, insufficient evidence,
no conclusion, no recommendation, limited recommendation, and a separate
human disposition.

`APPLICATION_RECORDS_AND_EXPOSES_OPERATOR_JUDGMENT`

`APPLICATION_DOES_NOT_IMPERSONATE_JUDGMENT`

V1 is not a general research platform, autonomous investigator, crawler or
collector, truth adjudicator, complete provenance system, automated literature
review, authority-ranking engine, generic workflow engine, recommendation
optimizer, persistent knowledge base, provider/model integration, or
production research product.

## Application-Layer Boundary and Reuse Posture

The research application layer owns the question; scope and exclusions; source
plan; source records; source evaluations; claims; evidence relationships;
contradictions and gaps; synthesis statements; conclusion or abstention;
optional recommendation; human disposition; and transformations into reused
neutral seams. Automated retrieval, autonomous extraction or evaluation, truth
adjudication, provider/model selection, complete provenance, generalized
orchestration, and production remain outside V1.

`NEUTRAL_EVIDENCE_LINK=REUSE_UNCHANGED`

`DETERMINISTIC_VALIDATION_AND_BLOCKING=REUSE_WITH_CONSTRAINTS`

`RECOMMENDATION_DISPOSITION_SEPARATION=REUSE_WITH_CONSTRAINTS`

`EXPLICIT_RECORD_IDENTITY=REUSE_WITH_CONSTRAINTS`

`CALLER_DECLARED_TRANSITIONS=REUSE_WITH_CONSTRAINTS`

`CASE_PACKET_PERSISTENCE_BEHAVIOR=REUSE_VIA_RESEARCH_APPLICATION_ADAPTER`

`PACKET_LOCAL_SYNTHESIS_PRESENTATION=REUSE_VIA_RESEARCH_APPLICATION_ADAPTER`

`DOSSIER_SOURCE_INVENTORY_AS_IS=DO_NOT_REUSE`

`CANDIDATE_ASSESSMENT_STRUCTURES=DO_NOT_REUSE`

`PRIORITIZATION_JUDGMENT=DO_NOT_REUSE`

`CONTROLLED_DOSSIER_WORKFLOW_COORDINATOR=DO_NOT_REUSE`

`GENERIC_WORKFLOW_ENGINE=DO_NOT_REUSE`

`NEW_GENERALIZED_PROVENANCE_ABSTRACTION=DEFER_PENDING_PROOF`

## Research Adapter

The research application adapter is a semantic firewall. It must preserve
caller-supplied identity and ordering; translate identified source records into
research-source meaning; translate identified extracted-fact storage into
caller-approved claim meaning without asserting fact status; preserve
qualifications and claim posture; use typed evidence associations; preserve
contradictions, gaps, abstention, and disposition; and expose identity or
semantic mismatch as failure.

It must not invent source quality or authority, invent claims, infer identity
continuity, fabricate dossier-only fields, treat association as truth, convert
recommendation into authorization, or perform vocabulary-only field renaming.

## Conceptual Record Model

The minimum conceptual records are research work identity, question, scope,
source-plan item, source record, source evaluation, claim, evidence link,
contradiction, missing-information item, synthesis statement, conclusion or
abstention, optional recommendation, and human disposition. This is a
conceptual design: not every record need be a separate persisted object, exact
implementation schemas remain deferred until proof selection, and claims are
propositions rather than confirmed facts.

## Minimum Provenance and Source Plan

For a later proof, each source requires stable identity; title or description;
publisher or origin; publication/version date when available; retrieval date;
public locator; source type; and known access/version limits. Each material
claim requires stable identity, support or explicit unsupported status,
quotation/paraphrase/summary/data-extraction/inference posture, useful source
locator, qualification and scope, and material contradiction and limitation
links. Source evaluation requires evaluator, date, dimension-specific
rationale, and limitations. The overall package requires source-plan coverage,
unavailable or uncollected source classes, known incompleteness, and disclosure
that the corpus was manually/operator selected.

`PHASE_5_PROVENANCE=INCOMPLETE`

`GENERALIZED_PHASE_6=INCOMPLETE`

A source plan must define required source kinds; required authorities or
perspectives; time, geography, jurisdiction, population, or version limits;
inclusion and exclusion criteria; minimum independence or diversity; stopping
condition; and acknowledged coverage gaps. Before synthesis, every plan
category must be satisfied, unavailable, substituted, or an explicit gap.

## Evaluation, Claims, Contradictions, and Gaps

Source evaluation is a human-owned multidimensional profile, not an opaque
scalar score. Dimensions may include relevance, authority, directness,
recency/version fitness, independence, methodology, interests or bias, scope
fit, limitations, and evaluator confidence. The application may preserve and
validate evaluation presence; it does not infer the judgment.

Claims are caller supplied or caller approved, require stable identity, and
keep quotation, paraphrase, summary, extraction, and inference distinguishable.
Inference must be explicitly labeled. Evidence relationships may be supporting,
contradicting, qualifying, contextual, or methodological. One source may
support several claims and one claim may depend on several sources. Unsupported
material claims must block or remain visibly unsupported. Autonomous claim
extraction is outside V1.

Designed categories are direct contradiction, apparent contradiction,
unresolved disagreement, missing source, missing perspective, weak support,
methodological limitation, uncertainty, and unknown. Identities,
relationships, categories, status, and declared materiality can be represented
deterministically. Whether a contradiction exists, whether scope resolves it,
and whether it blocks a conclusion remain human judgment.

## Synthesis, Abstention, and Human Disposition

Permitted terminal postures are supported conclusion, qualified conclusion,
conflicting evidence, insufficient evidence, no conclusion, no recommendation,
and recommendation with limitations.

`ABSTENTION=FIRST_CLASS_SUCCESSFUL_OUTCOME`

`RECOMMENDATION=OPTIONAL`

`CANDIDATE_RANKING=NOT_REQUIRED`

Human disposition is separate and must distinguish accepted findings; rejected
or disputed findings; accepted limitations; actions authorized; actions not
authorized; unresolved questions; and future research decisions. A disposition
may accept the brief while authorizing no action.

## Hard Blocks and Warnings

Major hard blocks include missing question or scope; malformed or duplicate
work/source identity; missing required locator; material claim used without
evidence; unknown evidence subject or source; unlabeled inference; insufficient
provenance for a material source; unresolved critical contradiction or gap that
invalidates the conclusion; recommendation under an explicit abstention
condition; unsupported conclusion; recommendation presented as authorization;
absent final human disposition; adapter identity mismatch; and an adapter
requirement to fabricate dossier fields. Non-critical weaknesses remain visible
warnings and must not be silently normalized away.

## Proof-Domain Posture and Next Gate

The advisory ranking remains: (1) public historical-record claim brief, (2)
public standards/guidance comparison, and (3) small public scientific-literature
evidence note.

`PUBLIC_SOURCE_PROOF_DOMAIN=NOT_YET_SELECTED`

The historical-record claim brief is only the current leading candidate. Proof
planning must explicitly decide whether persistence is necessary or whether an
in-memory/fixture-driven proof better isolates semantic transfer.

`GOVERNED_RESEARCH_V1_PROOF_PLANNING_GATE=READY`

The next candidate boundary is a read-only public-source proof design that must
determine one proof domain, one exact question, one finite corpus posture, one
provenance requirement, one success criterion, one stop condition, whether
persistence is required, and exact non-proofs. The proof itself remains
unauthorized.

## Explicit Non-Proofs

This design does not prove implementation readiness, proof success, research
competence, source collection competence, source completeness or authenticity,
source quality, extraction accuracy, contradiction-discovery accuracy,
analytical or recommendation correctness, complete provenance, Phase 5
completion, generalized Phase 6, provider/model suitability, runtime
capability, product usefulness, product wedge, neutral-core admission, or
production readiness.

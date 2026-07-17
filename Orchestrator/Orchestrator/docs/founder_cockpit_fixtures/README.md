# Founder Cockpit Fictional Fixtures

This local docs/data package contains fictional, read-only Founder Cockpit fixtures. Every root snapshot is a `fictional_fixture` and a `non_authoritative_projection`; none is current project evidence.

## Package Inventory

| File | Role |
| --- | --- |
| `canonical_snapshot.json` | Canonical reconciled fixture. |
| `stale_sources.json` | Degraded fixture: available but stale, unreconciled sources. |
| `conflicting_authority.json` | Degraded fixture: unresolved competing fictional claims. |
| `no_next_move.json` | Degraded fixture: no active bounded move recorded. |
| `unratified_wedge.json` | Degraded fixture: active proving use case with no ratified wedge. |
| `STATIC_WIREFRAME_FIXTURE.md` | Tool-neutral textual projection of the canonical fixture. |
| `ROGER_COMPREHENSION_TEST.md` | Recorded informed-review results and reusable review prompts. |
| `README.md` | This package guide and scope record. |

The five JSON fixtures use only `Snapshot`, `WorkItem`, `Claim`, `Decision`, and `Source` records. The accepted six-unit hierarchy remains: stage/pursuit; proof/decisive non-proof; proving-use-case/product-wedge posture; open wedge decision; next move/move posture; and source health with the fictional/non-authoritative warning. The persistent fictional, non-authoritative, read-only label is separate from that count.

## Recorded Review Status

The canonical fixture and all four degraded variants completed informed founder review. The review was informed rather than blind: Roger participated in fixture design. The record is in `ROGER_COMPREHENSION_TEST.md`.

- Canonical: `PASS_FOUNDER_COCKPIT_CANONICAL_SIX_UNIT_FIXTURE_INFORMED_FOUNDER_REVIEW_AND_DISCLOSURE_REFINEMENT_COMPLETE`
- Stale sources: `PASS_FOUNDER_COCKPIT_STALE_SOURCES_INFORMED_FOUNDER_REVIEW`
- Conflicting authority: `PASS_FOUNDER_COCKPIT_CONFLICTING_AUTHORITY_INFORMED_FOUNDER_REVIEW`
- No next move: `PASS_FOUNDER_COCKPIT_NO_NEXT_MOVE_INFORMED_FOUNDER_REVIEW`
- Unratified wedge: `PASS_FOUNDER_COCKPIT_UNRATIFIED_WEDGE_INFORMED_FOUNDER_REVIEW`
- Campaign: `PASS_FOUNDER_COCKPIT_CANONICAL_AND_FOUR_DEGRADED_VARIANT_INFORMED_FOUNDER_REVIEW_COMPLETE`

## Scope and Durability

This package is local and untracked in the current working tree. Its review records do not make it a durable repository package, a remote verification, or a later CTO review outcome; commit/push and any such review require separate authorization.

The package does not prove or authorize HTML, CSS, JavaScript, visual implementation, platform work, live data, APIs, persistence, project-management functions, product-wedge selection, implementation, or architectural lock-in. Future visual prototyping requires a separate boundary.

# Phase 119 - Manual Review CLI Adapter Contract

## Status

Locally source/test/docs-proven.

Marker:

`PHASE119_MANUAL_REVIEW_CLI_ADAPTER_LOCAL_SOURCE_TEST_DOCS_PROVEN=PASS`

## Purpose

Add a deterministic, standard-library-only CLI-compatible adapter contract for
the Phase 118 manual coordinator review runner. The adapter lists built-in
review fixtures and renders coordinator review text for one named fixture.

## Changed Files

- `orchestrator/manual_review_cli.py`
- `tests/test_phase_119_manual_review_cli_adapter_contract.py`
- `docs/PHASE_119.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`

## Source Contract Added

- `ManualReviewCliResult` records deterministic adapter outcome fields:
  command, fixture id, output text, error text, listed fixtures, accepted
  status, non-proofs, no-activity flags, caveats, and integer exit code.
- `build_manual_review_cli_output(...)` supports `--list-fixtures`,
  `--fixture <fixture_id>`, `--help`, and empty-argument help output without
  project state mutation.
- `main(...)` prints the deterministic adapter output and returns the integer
  exit code.
- Unknown fixtures and malformed commands fail conservatively with non-zero
  exits and no execution.

## Tests Added

- Fixture listing preserves Phase 118 built-in fixture IDs in stable order.
- Named fixture rendering preserves Phase 118 review report text.
- Unknown fixture handling is conservative and non-executing.
- Help and empty arguments do not run fixtures.
- Non-proofs and no-activity flags remain explicit.
- Source import inspection rejects service, provider, platform, connector,
  scheduler, UI, and third-party CLI framework imports.

## Validation Performed

- `git status --short` before edits.
- `python -m py_compile orchestrator/manual_review_cli.py orchestrator/manual_review_runner.py orchestrator/coordinator_review_report.py orchestrator/fixture_packet_pipeline.py orchestrator/boundary_packet.py orchestrator/intake_admission_pipeline.py orchestrator/prompt_to_envelope.py orchestrator/route_proposal.py orchestrator/request_routing.py orchestrator/capability_registry.py`
- `python -m unittest tests.test_phase_119_manual_review_cli_adapter_contract`
- `python -m unittest tests.test_phase_118_manual_review_runner_contract`
- `python -m unittest tests.test_phase_117_coordinator_review_report_contract`
- `python -m unittest tests.test_phase_116_fixture_to_boundary_packet_pipeline`
- `python -m unittest tests.test_phase_115_admission_to_boundary_packet_contract`
- `python -m unittest tests.test_phase_114_end_to_end_intake_admission_pipeline`
- `python -m unittest tests.test_phase_113_prompt_to_envelope_fixture_contract`
- `python -m unittest tests.test_phase_111_route_proposal_source_contract`
- `python -m unittest tests.test_phase_110_route_validator_capability_registry_integration`
- `python -m unittest tests.test_phase_103_domain_general_request_routing_contract`
- `rg` read/search verification for Phase 119 docs, marker, source, test, and
  ledger registration content.
- `git status --short` after edits.

## Explicit Non-Proofs

Phase 119 does not prove service/API/UI productization, live prompt inference,
raw prompt-to-envelope inference, natural-language intent inference, regex
classification, live routing, route execution, worker execution, Codex or Relay
invocation, concrete substrate selection, provider/model/runtime/platform
selection or execution, RAG/local document lookup, web lookup, scheduler or
reminder execution, connector execution, file mutation behavior, artifact
export/package behavior, cleanup, deletion, archive, production execution, or
production readiness.

## Caveats

- This is a source/test adapter contract only.
- The adapter output is deterministic review text, not coordinator acceptance.
- Listing fixtures is not execution.
- A validated named-fixture run is not productized CLI/UI, worker dispatch,
  route execution, provider/model selection, or production readiness.

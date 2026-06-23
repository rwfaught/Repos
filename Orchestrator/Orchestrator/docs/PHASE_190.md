# Phase 190 - 30B Provider Viability Marker Smoke

## Purpose

Phase 190 documents the accepted constrained 30B viability marker-smoke result
for `qwen3:30b-a3b-instruct-2507-q4_K_M`.

This phase is viability evidence only. It is not route execution, semantic
correctness proof, real workload sufficiency proof, long-context proof,
sustained-load proof, or production readiness.

## One-Call 30B Viability Result

The accepted Phase 190 marker-smoke facts are:

- HTTP status: `200`
- JSON parse success: `true`
- Returned model: `qwen3:30b-a3b-instruct-2507-q4_K_M`
- Response text: `ORCH_30B_VIABILITY_OK`
- Done: `true`
- Done reason: `stop`
- Duration: `9394ms`
- Marker present: `true`
- Classification: `pass_30b_marker_smoke_viability`

## Artifact Backfill Caveat

Phase 190 Retry 1 backfilled the proof artifact with no provider call:

`C:\Users\accou\AppData\Local\Temp\orchestrator_phase190_30b_provider_viability\phase_190_30b_provider_viability_probe.json`

The artifact records accepted proof facts. The Retry 1 backfill action is not a
new provider/model/runtime probe.

## GPU Observation Caveat

Captured GPU observation:

- Before memory: `0MiB / 24463MiB`
- After memory: `18302MiB / 24463MiB`
- Process attribution was not proven by the `nvidia-smi` process table.

The GPU observation is operational context only. It is not sustained-load,
long-context, real workload sufficiency, or production readiness proof.

## Non-Proofs

Phase 190 does not prove:

- Route execution
- Semantic correctness
- Real workload sufficiency
- Long-context behavior
- Sustained-load stability
- Production readiness
- Product tracer `ORCH_PROVIDER_SMOKE_OK` marker proof

## Decision Impact

Phase 190 establishes that `qwen3:30b-a3b-instruct-2507-q4_K_M` has accepted
constrained 30B marker-smoke viability. Phase 191 uses that accepted viability
fact to retarget the supervised provider-call tracer packet away from the
disallowed `qwen3.6:35b-a3b` laptop target.

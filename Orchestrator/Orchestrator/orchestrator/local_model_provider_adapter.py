"""Injected-transport local-provider adapter for bounded advisory intake."""

from __future__ import annotations

import hashlib
from typing import Protocol

from orchestrator.local_model_provider_stub import ProviderInterpretationResult
from orchestrator.local_model_reasoning_contract import (
    LocalModelInterpretationRequest,
    normalize_local_model_output,
    validate_local_model_raw_output,
)


class LocalModelTransport(Protocol):
    def __call__(self, request: LocalModelInterpretationRequest) -> str:
        """Return raw provider text; transport owns no coordinator authority."""


def _raw_reference(raw_output: str) -> str:
    return f"sha256:{hashlib.sha256(raw_output.encode('utf-8')).hexdigest()}"


class InjectedLocalModelProvider:
    """Adapt an injected runner without executing a runtime or provider itself."""

    provider_key = "injected_local_model_transport"

    def __init__(self, transport: LocalModelTransport):
        self._transport = transport

    def interpret(self, request: LocalModelInterpretationRequest) -> ProviderInterpretationResult:
        try:
            raw_output = self._transport(request)
        except Exception as exc:
            return ProviderInterpretationResult(
                provider_key=self.provider_key,
                status="transport_exception",
                detail=f"Injected transport failed: {type(exc).__name__}",
                fallback_status="deterministic_fallback",
            )
        if not isinstance(raw_output, str):
            return ProviderInterpretationResult(
                provider_key=self.provider_key,
                status="invalid_transport_output",
                detail="Injected transport must return raw text.",
                fallback_status="deterministic_fallback",
            )
        normalization = normalize_local_model_output(raw_output)
        review = validate_local_model_raw_output(request, raw_output)
        authority_quarantined = review.classification == "rejected_authority_or_execution_claim"
        admitted = review.accepted and review.validation is not None and review.validation.interpretation is not None
        return ProviderInterpretationResult(
            provider_key=self.provider_key,
            status="candidate_admitted" if admitted else "candidate_quarantined",
            response=review.validation.interpretation if admitted and review.validation else None,
            detail=("Validated advisory candidate; deterministic policy remains authoritative."
                     if admitted else "Candidate was quarantined or rejected; deterministic fallback required."),
            raw_output=raw_output,
            normalization_classification=normalization.classification,
            validation_classification=review.classification,
            validation_reasons=review.reasons,
            fallback_status="not_required" if admitted else "deterministic_fallback",
            candidate_admitted=admitted,
            authority_quarantined=authority_quarantined,
            raw_output_reference=_raw_reference(raw_output),
            raw_output_validation=review,
        )

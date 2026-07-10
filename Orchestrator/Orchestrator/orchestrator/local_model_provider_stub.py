"""Disabled and caller-supplied stubs for the future local reasoning seam."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping, Protocol

from orchestrator.local_model_reasoning_contract import LocalModelInterpretationRequest


@dataclass(frozen=True)
class ProviderInterpretationResult:
    provider_key: str
    status: str
    response: Any = None
    detail: str = ""
    execution_performed: bool = False
    raw_output: str | None = None


class LocalModelReasoningProvider(Protocol):
    provider_key: str

    def interpret(self, request: LocalModelInterpretationRequest) -> ProviderInterpretationResult:
        """Return a structured candidate response without granting authority."""


class DisabledLocalModelProvider:
    provider_key = "local_model_disabled_stub"

    def interpret(self, request: LocalModelInterpretationRequest) -> ProviderInterpretationResult:
        return ProviderInterpretationResult(
            provider_key=self.provider_key,
            status="disabled",
            detail="Local-model reasoning is disabled in this dry-run boundary.",
            execution_performed=False,
        )


class StaticLocalModelProvider:
    """Return caller-supplied structured data for deterministic seam tests."""

    provider_key = "caller_supplied_static_stub"

    def __init__(self, response: Mapping[str, Any] | Any):
        self._response = deepcopy(response)

    def interpret(self, request: LocalModelInterpretationRequest) -> ProviderInterpretationResult:
        response = None if isinstance(self._response, str) else deepcopy(self._response)
        raw_output = self._response if isinstance(self._response, str) else None
        return ProviderInterpretationResult(
            provider_key=self.provider_key,
            status="stub_response",
            response=response,
            detail="Caller-supplied response; no model was invoked.",
            execution_performed=False,
            raw_output=raw_output,
        )

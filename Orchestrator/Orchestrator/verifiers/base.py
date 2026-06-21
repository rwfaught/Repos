from dataclasses import dataclass
from typing import Any


@dataclass
class VerificationCheckResult:
    name: str
    passed: bool
    message: str
    evidence: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "message": self.message,
            "evidence": self.evidence,
        }


@dataclass
class VerificationResult:
    overall_passed: bool
    checks: list[VerificationCheckResult]
    messages: list[str]
    execution_artifact_id: str | None = None
    causal_change_required: bool | None = None
    causal_change_passed: bool | None = None
    causal_change_targets: list[dict[str, Any]] | None = None
    changed_targets: list[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        result = {
            "overall_passed": self.overall_passed,
            "checks": [check.to_dict() for check in self.checks],
            "messages": self.messages,
        }
        if self.execution_artifact_id is not None:
            result["execution_artifact_id"] = self.execution_artifact_id
        if self.causal_change_required is not None:
            result["causal_change_required"] = self.causal_change_required
        if self.causal_change_passed is not None:
            result["causal_change_passed"] = self.causal_change_passed
        if self.causal_change_targets is not None:
            result["causal_change_targets"] = self.causal_change_targets
        if self.changed_targets is not None:
            result["changed_targets"] = self.changed_targets
        return result

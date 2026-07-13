"""Validation and normalization for bounded subprocess-worker execution."""

from __future__ import annotations

import math
from typing import Any


POLICY_ID = "worker_execution_policy_v1"
DEFAULT_WHOLE_WORKER_TIMEOUT_SECONDS = 600.0
MIN_WHOLE_WORKER_TIMEOUT_SECONDS = 10.0
MAX_WHOLE_WORKER_TIMEOUT_SECONDS = 3600.0
DEFAULT_POLL_INTERVAL_SECONDS = 1.0
DEFAULT_GRACEFUL_TERMINATION_SECONDS = 5.0
DEFAULT_FORCED_CLEANUP_CONFIRMATION_SECONDS = 5.0
DEFAULT_MAX_OUTPUT_BYTES = 1_000_000


def _finite_number(value: Any, *, label: str) -> float:
    if isinstance(value, bool) or value is None:
        raise ValueError(f"{label} must be a finite number.")
    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{label} must be a finite number.") from error
    if not math.isfinite(number):
        raise ValueError(f"{label} must be finite.")
    return number


def normalize_worker_execution_policy(
    whole_worker_timeout_seconds: Any = None,
    *,
    selection_source: str = "provider_default",
    poll_interval_seconds: Any = DEFAULT_POLL_INTERVAL_SECONDS,
    graceful_termination_seconds: Any = DEFAULT_GRACEFUL_TERMINATION_SECONDS,
    forced_cleanup_confirmation_seconds: Any = DEFAULT_FORCED_CLEANUP_CONFIRMATION_SECONDS,
    max_output_bytes: Any = DEFAULT_MAX_OUTPUT_BYTES,
) -> dict[str, Any]:
    """Return a durable, bounded policy or raise ``ValueError``.

    ``None`` selects the canonical 600-second ceiling. Callers that supply a
    value (including the CLI) are validated before a worker can be launched.
    """
    timeout = (
        DEFAULT_WHOLE_WORKER_TIMEOUT_SECONDS
        if whole_worker_timeout_seconds is None
        else _finite_number(whole_worker_timeout_seconds, label="whole_worker_timeout_seconds")
    )
    if timeout < MIN_WHOLE_WORKER_TIMEOUT_SECONDS or timeout > MAX_WHOLE_WORKER_TIMEOUT_SECONDS:
        raise ValueError(
            "whole_worker_timeout_seconds must be between 10 and 3600 seconds."
        )
    poll = _finite_number(poll_interval_seconds, label="poll_interval_seconds")
    graceful = _finite_number(graceful_termination_seconds, label="graceful_termination_seconds")
    forced = _finite_number(forced_cleanup_confirmation_seconds, label="forced_cleanup_confirmation_seconds")
    if not 0.1 <= poll <= 1.0:
        raise ValueError("poll_interval_seconds must be between 0.1 and 1.0 seconds.")
    if graceful <= 0 or forced <= 0:
        raise ValueError("termination durations must be positive finite numbers.")
    if isinstance(max_output_bytes, bool):
        raise ValueError("max_output_bytes must be a positive integer.")
    try:
        output_limit = int(max_output_bytes)
    except (TypeError, ValueError) as error:
        raise ValueError("max_output_bytes must be a positive integer.") from error
    if output_limit <= 0:
        raise ValueError("max_output_bytes must be a positive integer.")
    source = str(selection_source or "").strip()
    if not source:
        raise ValueError("selection_source is required.")
    return {
        "policy_id": POLICY_ID,
        "whole_worker_timeout_seconds": timeout,
        "poll_interval_seconds": poll,
        "graceful_termination_seconds": graceful,
        "forced_cleanup_confirmation_seconds": forced,
        "max_output_bytes": output_limit,
        "selection_source": source,
    }


def validate_normalized_worker_execution_policy(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("worker execution policy must be an object.")
    if value.get("policy_id") != POLICY_ID:
        raise ValueError("worker execution policy identity is unsupported.")
    return normalize_worker_execution_policy(
        value.get("whole_worker_timeout_seconds"),
        selection_source=value.get("selection_source", ""),
        poll_interval_seconds=value.get("poll_interval_seconds"),
        graceful_termination_seconds=value.get("graceful_termination_seconds"),
        forced_cleanup_confirmation_seconds=value.get("forced_cleanup_confirmation_seconds"),
        max_output_bytes=value.get("max_output_bytes"),
    )


def policies_match(left: Any, right: Any) -> bool:
    try:
        return validate_normalized_worker_execution_policy(left) == validate_normalized_worker_execution_policy(right)
    except ValueError:
        return False

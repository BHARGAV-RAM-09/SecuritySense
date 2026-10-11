
"""Build traceable ProofLoop evidence records without overstating claims."""

from copy import deepcopy
from typing import Any


VALID_STATUSES = {
    "passed",
    "failed",
    "unrun",
    "inconclusive",
}


def _normalize_status(value: Any) -> str:
    """Return a supported status, or inconclusive for unknown values."""
    if isinstance(value, str) and value in VALID_STATUSES:
        return value
    return "inconclusive"


def build_proofloop_evidence(
    finding: dict[str, Any],
    investigation: dict[str, Any],
    reproduction: dict[str, Any] | None = None,
    verification: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Combine evidence while keeping unperformed checks explicitly unrun."""
    if not isinstance(finding, dict):
        raise TypeError("finding must be a dictionary.")

    if not isinstance(investigation, dict):
        raise TypeError("investigation must be a dictionary.")

    if reproduction is not None and not isinstance(reproduction, dict):
        raise TypeError("reproduction must be a dictionary or None.")

    if verification is not None and not isinstance(verification, dict):
        raise TypeError("verification must be a dictionary or None.")

    reproduction_data = deepcopy(reproduction) if reproduction is not None else None
    verification_data = deepcopy(verification) if verification is not None else None

    reproduction_status = _normalize_status(
        reproduction_data.get("status", "unrun")
        if reproduction_data is not None
        else "unrun"
    )
    verification_status = _normalize_status(
        verification_data.get("status", "unrun")
        if verification_data is not None
        else "unrun"
    )

    finding_present = bool(
        finding.get("rule_id")
        and finding.get("file")
        and isinstance(finding.get("line"), int)
        and not isinstance(finding.get("line"), bool)
        and finding["line"] >= 1
    )

    investigation_evidence = investigation.get("evidence")
    evidence_complete = bool(
        finding_present
        and isinstance(investigation_evidence, list)
        and investigation_evidence
    )

    # A passing status alone is insufficient: the verifier must explicitly
    # report a successful verification result.
    fix_verified = bool(
        verification_data is not None
        and verification_status == "passed"
        and verification_data.get("verified") is True
    )

    vulnerability_reproduced = bool(
        reproduction_data is not None
        and reproduction_status == "passed"
        and reproduction_data.get("vulnerability_reproduced") is True
    )

    return {
        "finding": deepcopy(finding),
        "investigation": deepcopy(investigation),
        "reproduction": reproduction_data,
        "verification": verification_data,
        "reproduction_status": reproduction_status,
        "verification_status": verification_status,
        "evidence_complete": evidence_complete,
        "claims": {
            "finding_detected": finding_present,
            "investigation_performed": bool(investigation),
            "vulnerability_reproduced": vulnerability_reproduced,
            "fix_verified": fix_verified,
        },
    }


import pytest

from app.proofloop.evidence import build_proofloop_evidence


def make_finding():
    return {
        "rule_id": "B105",
        "file": "sample.py",
        "line": 2,
        "message": "Possible hardcoded password",
    }


def make_investigation():
    return {
        "investigation_status": "evidence_collected",
        "evidence": [{"type": "source_location", "line": 2}],
    }


def test_proofloop_preserves_finding_and_investigation():
    finding = make_finding()
    investigation = make_investigation()

    result = build_proofloop_evidence(finding, investigation)

    assert result["finding"] == finding
    assert result["investigation"] == investigation
    assert result["evidence_complete"] is True
    assert result["reproduction_status"] == "unrun"
    assert result["verification_status"] == "unrun"
    assert result["claims"]["vulnerability_reproduced"] is False
    assert result["claims"]["fix_verified"] is False


def test_proofloop_records_actual_reproduction_result():
    reproduction = {
        "status": "passed",
        "vulnerability_reproduced": True,
        "checks_passed": 3,
        "checks_total": 3,
    }

    result = build_proofloop_evidence(
        make_finding(),
        make_investigation(),
        reproduction=reproduction,
    )

    assert result["reproduction_status"] == "passed"
    assert result["claims"]["vulnerability_reproduced"] is True


def test_proofloop_does_not_claim_unrun_fix_is_verified():
    result = build_proofloop_evidence(
        make_finding(),
        make_investigation(),
        verification={"status": "unrun"},
    )

    assert result["claims"]["fix_verified"] is False
    assert result["verification_status"] == "unrun"


def test_proofloop_handles_unknown_status_as_inconclusive():
    result = build_proofloop_evidence(
        make_finding(),
        make_investigation(),
        reproduction={"status": "invented_status"},
        verification={"status": "invented_status"},
    )

    assert result["reproduction_status"] == "inconclusive"
    assert result["verification_status"] == "inconclusive"
    assert result["claims"]["vulnerability_reproduced"] is False
    assert result["claims"]["fix_verified"] is False


def test_proofloop_rejects_invalid_input_types():
    with pytest.raises(TypeError, match="finding"):
        build_proofloop_evidence(
            "not-a-dictionary",
            make_investigation(),
        )


def test_proofloop_requires_source_location_for_complete_evidence():
    result = build_proofloop_evidence(
        {"rule_id": "B105"},
        make_investigation(),
    )

    assert result["evidence_complete"] is False
    assert result["claims"]["finding_detected"] is False


def test_proofloop_requires_explicit_verification_flag():
    result = build_proofloop_evidence(
        make_finding(),
        make_investigation(),
        verification={"status": "passed"},
    )

    assert result["verification_status"] == "passed"
    assert result["claims"]["fix_verified"] is False


def test_proofloop_does_not_mutate_input_records():
    finding = make_finding()
    investigation = make_investigation()
    original_finding = deepcopy_for_test(finding)

    build_proofloop_evidence(finding, investigation)

    assert finding == original_finding


def deepcopy_for_test(value):
    """Create a detached copy for mutation assertions."""
    from copy import deepcopy

    return deepcopy(value)

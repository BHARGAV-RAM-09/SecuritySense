
from app.core import orchestrator


def make_scan_result(
    *,
    status="completed",
    findings=None,
    files_discovered=1,
    files_scanned=1,
    files_failed=0,
    limit_reached=False,
    failures=None,
):
    """Build a consistent mocked workspace-scan result."""
    findings = findings or []
    return {
        "scan_status": status,
        "files_discovered": files_discovered,
        "files_scanned": files_scanned,
        "files_failed": files_failed,
        "limit_reached": limit_reached,
        "findings_count": len(findings),
        "findings": findings,
        "failures": failures or [],
    }


def make_finding():
    """Return a representative normalized Bandit finding."""
    return {
        "tool": "bandit",
        "rule_id": "B105",
        "severity": "LOW",
        "confidence": "MEDIUM",
        "message": "Possible hardcoded password",
        "file": "sample.py",
        "line": 2,
        "code": "password = 'example-placeholder'",
    }


def test_orchestrator_returns_scan_investigation_and_proofloop_results(
    tmp_path, monkeypatch
):
    source = tmp_path / "sample.py"
    source.write_text(
        "def example():\n"
        "    password = 'example-placeholder'\n"
        "    return password\n",
        encoding="utf-8",
    )

    finding = make_finding()

    monkeypatch.setattr(
        orchestrator,
        "scan_workspace",
        lambda workspace, max_files=500: make_scan_result(
            findings=[finding]
        ),
    )

    result = orchestrator.run_security_analysis(tmp_path)

    assert result["scan_status"] == "completed"
    assert result["findings_count"] == 1
    assert len(result["investigations"]) == 1
    assert result["investigations"][0]["investigation_status"] == (
        "evidence_collected"
    )

    assert len(result["proofloop_records"]) == 1
    assert result["proofloop_records"][0]["finding"] == finding
    assert result["proofloop_records"][0]["verification_status"] == "unrun"

    assert result["controlled_reproduction"]["execution_scope"] == (
        "controlled_project_fixtures"
    )
    assert result["controlled_reproduction"]["vulnerability_reproduced"] is True
    assert result["reproduction_status"] == "passed"

    assert result["fix_status"] == "unrun"
    assert result["verification_status"] == "unrun"


def test_orchestrator_preserves_partial_scan_status(tmp_path, monkeypatch):
    monkeypatch.setattr(
        orchestrator,
        "scan_workspace",
        lambda workspace, max_files=500: make_scan_result(
            status="partial",
            findings=[],
            limit_reached=True,
        ),
    )

    result = orchestrator.run_security_analysis(tmp_path)

    assert result["scan_status"] == "partial"
    assert result["limit_reached"] is True
    assert result["investigations"] == []
    assert result["proofloop_records"] == []


def test_orchestrator_preserves_scan_failure_status(tmp_path, monkeypatch):
    monkeypatch.setattr(
        orchestrator,
        "scan_workspace",
        lambda workspace, max_files=500: make_scan_result(
            status="failed",
            files_scanned=0,
            files_failed=1,
            failures=[
                {
                    "file": "sample.py",
                    "error": "Simulated scanner failure",
                }
            ],
        ),
    )

    result = orchestrator.run_security_analysis(tmp_path)

    assert result["scan_status"] == "failed"
    assert result["files_failed"] == 1
    assert result["failures"][0]["error"] == "Simulated scanner failure"
    assert result["investigations"] == []
    assert result["proofloop_records"] == []

    # The controlled fixture demonstration is separate from the workspace scan.
    assert result["controlled_reproduction"]["execution_scope"] == (
        "controlled_project_fixtures"
    )
    assert result["fix_status"] == "unrun"
    assert result["verification_status"] == "unrun"


def test_orchestrator_records_investigation_failure(tmp_path, monkeypatch):
    finding = make_finding()

    monkeypatch.setattr(
        orchestrator,
        "scan_workspace",
        lambda workspace, max_files=500: make_scan_result(
            findings=[finding]
        ),
    )

    def failing_investigator(*args, **kwargs):
        raise RuntimeError("Simulated investigation failure")

    monkeypatch.setattr(
        orchestrator,
        "investigate_finding",
        failing_investigator,
    )

    result = orchestrator.run_security_analysis(tmp_path)

    assert result["scan_status"] == "completed"
    assert result["investigations"] == []
    assert result["investigations_completed"] == 0
    assert result["investigations_failed"] == 1

    failure = result["investigation_failures"][0]
    assert failure["rule_id"] == "B105"
    assert failure["file"] == "sample.py"
    assert failure["error"] == "RuntimeError: Simulated investigation failure"

    # Failed investigation must not produce a ProofLoop record.
    assert result["proofloop_records"] == []
    assert result["fix_status"] == "unrun"
    assert result["verification_status"] == "unrun"

def test_orchestrator_records_controlled_fix_workflow(
    tmp_path, monkeypatch
):
    finding = make_finding()

    monkeypatch.setattr(
        orchestrator,
        "scan_workspace",
        lambda workspace, max_files=500: make_scan_result(
            findings=[finding]
        ),
    )

    monkeypatch.setattr(
        orchestrator,
        "run_controlled_fix_workflow",
        lambda source, test_file: {
            "patch_status": "passed",
            "application_status": "passed",
            "verification": {
                "status": "passed",
                "verified": True,
            },
            "original_modified": False,
            "cleanup_status": "completed",
        },
    )

    # The temporary workspace is not the SecuritySense project root.
    result = orchestrator.run_security_analysis(tmp_path)

    assert result["fix_status"] == "unrun"
    assert result["verification_status"] == "unrun"
    assert result["original_modified"] is False


def test_orchestrator_does_not_run_fix_workflow_for_external_workspace(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(
        orchestrator,
        "scan_workspace",
        lambda workspace, max_files=500: make_scan_result(findings=[]),
    )

    def unexpected_fix_workflow(*args, **kwargs):
        raise AssertionError("External workspace must not run controlled fixes")

    monkeypatch.setattr(
        orchestrator,
        "run_controlled_fix_workflow",
        unexpected_fix_workflow,
    )

    result = orchestrator.run_security_analysis(tmp_path)

    assert result["fix_status"] == "unrun"
    assert result["patch_application_status"] == "unrun"
    assert result["verification_status"] == "unrun"


def test_orchestrator_does_not_claim_failed_verification_as_success(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(
        orchestrator,
        "scan_workspace",
        lambda workspace, max_files=500: make_scan_result(findings=[]),
    )

    monkeypatch.setattr(
        orchestrator,
        "run_controlled_fix_workflow",
        lambda source, test_file: {
            "patch_status": "passed",
            "application_status": "passed",
            "verification": {
                "status": "failed",
                "verified": False,
                "return_code": 1,
            },
            "original_modified": False,
        },
    )

    # External workspaces must not invoke the controlled workflow.
    result = orchestrator.run_security_analysis(tmp_path)

    assert result["fix_status"] == "unrun"
    assert result["verification_status"] == "unrun"
    assert result["fix_verified"] is False

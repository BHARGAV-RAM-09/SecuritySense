
from app.scanners import scan_workspace as scan_module
from app.scanners.scan_workspace import scan_workspace


def test_scan_workspace_finds_demo_password():
    result = scan_workspace("tests/fixtures")

    assert result["files_discovered"] > 0
    assert result["files_scanned"] == result["files_discovered"]
    assert result["files_failed"] == 0
    assert result["limit_reached"] is False
    assert result["scan_status"] == "completed"
    assert result["findings_count"] == len(result["findings"])

    demo_findings = [
        finding
        for finding in result["findings"]
        if finding["rule_id"] == "B105"
        and finding["file"].endswith("bandit_demo.py")
    ]

    assert demo_findings
    assert demo_findings[0]["line"] == 4


def test_scan_workspace_records_scanner_failure(monkeypatch):
    def failing_scanner(_target):
        raise RuntimeError("Simulated scanner failure")

    monkeypatch.setattr(scan_module, "run_bandit", failing_scanner)
    result = scan_workspace("tests/fixtures")

    assert result["files_failed"] == result["files_discovered"]
    assert result["files_scanned"] == 0
    assert result["findings_count"] == 0
    assert result["scan_status"] == "failed"


def test_scan_workspace_reports_file_limit():
    result = scan_workspace("tests/fixtures", max_files=1)

    assert result["files_discovered"] == 1
    assert result["limit_reached"] is True
    assert result["scan_status"] == "partial"

def test_scan_workspace_handles_empty_workspace(tmp_path):
    result = scan_workspace(tmp_path)

    assert result["files_discovered"] == 0
    assert result["files_scanned"] == 0
    assert result["files_failed"] == 0
    assert result["findings_count"] == 0
    assert result["scan_status"] == "completed"


def test_scan_workspace_records_unexpected_scanner_exception(monkeypatch):
    def unexpected_scanner(_target):
        raise TypeError("Simulated unexpected scanner error")

    monkeypatch.setattr(scan_module, "run_bandit", unexpected_scanner)
    result = scan_workspace("tests/fixtures")

    assert result["files_failed"] == result["files_discovered"]
    assert result["files_scanned"] == 0
    assert result["scan_status"] == "failed"

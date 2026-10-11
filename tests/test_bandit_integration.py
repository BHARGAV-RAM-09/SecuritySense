
from app.scanners.bandit_runner import run_bandit
from app.scanners.findings import normalize_bandit_report


def test_bandit_finding_is_normalized():
    report = run_bandit("tests/fixtures/bandit_demo.py")
    findings = normalize_bandit_report(report)

    assert findings, "Expected Bandit to detect the demo hardcoded password"

    finding = next(
        (item for item in findings if item["rule_id"] == "B105"),
        None,
    )

    assert finding is not None
    assert finding["tool"] == "bandit"
    assert finding["file"].endswith("bandit_demo.py")
    assert finding["line"] == 4

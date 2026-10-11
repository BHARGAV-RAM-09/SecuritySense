
from app.scanners.findings import normalize_bandit_report


def test_normalize_bandit_report():
    report = {
        "results": [
            {
                "test_id": "B105",
                "issue_severity": "LOW",
                "issue_confidence": "MEDIUM",
                "issue_text": "Possible hardcoded password",
                "filename": "tests/fixtures/bandit_demo.py",
                "line_number": 5,
                "code": 'DEMO_PASSWORD = "example-hardcoded-password"',
            }
        ]
    }

    findings = normalize_bandit_report(report)

    assert len(findings) == 1
    assert findings[0]["tool"] == "bandit"
    assert findings[0]["rule_id"] == "B105"
    assert findings[0]["file"] == "tests/fixtures/bandit_demo.py"
    assert findings[0]["line"] == 5


def test_normalize_empty_report():
    assert normalize_bandit_report({"results": []}) == []

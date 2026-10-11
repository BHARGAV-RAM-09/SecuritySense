
from app.agents import reproducer


def test_reproducer_confirms_controlled_access_control_vulnerability():
    result = reproducer.reproduce_access_control()

    assert result["status"] == "passed"
    assert result["vulnerability_reproduced"] is True
    assert result["checks_passed"] == 3
    assert result["checks_total"] == 3
    assert result["execution_scope"] == "controlled_project_fixtures"


def test_reproducer_records_each_check():
    result = reproducer.reproduce_access_control()

    checks = [item["check"] for item in result["evidence"]]

    assert checks == [
        "unauthorized_access_vulnerable_fixture",
        "unauthorized_access_secure_fixture",
        "owner_access_secure_fixture",
    ]
    assert all(item["passed"] for item in result["evidence"])


def test_reproducer_reports_unexpected_fixture_error(monkeypatch):
    def failing_fixture(_requester, _requested_user):
        raise RuntimeError("Simulated fixture failure")

    monkeypatch.setattr(
        reproducer,
        "vulnerable_get_profile",
        failing_fixture,
    )

    result = reproducer.reproduce_access_control()

    assert result["status"] == "failed"
    assert result["vulnerability_reproduced"] is False
    assert result["error"] == "RuntimeError: Simulated fixture failure"

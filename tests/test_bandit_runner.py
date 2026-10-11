
import json

import pytest

from app.scanners import bandit_runner


@pytest.mark.parametrize("timeout", [0, -1, 121, True, 1.5, "30"])
def test_run_bandit_rejects_invalid_timeout(timeout):
    with pytest.raises(ValueError):
        bandit_runner.run_bandit("tests/fixtures/bandit_demo.py", timeout)


def test_run_bandit_rejects_report_without_results(monkeypatch):
    class FakeCompletedProcess:
        returncode = 0
        stdout = json.dumps({"metrics": {}})
        stderr = ""

    monkeypatch.setattr(
        bandit_runner.subprocess,
        "run",
        lambda *args, **kwargs: FakeCompletedProcess(),
    )

    with pytest.raises(RuntimeError, match="results list"):
        bandit_runner.run_bandit("tests/fixtures/bandit_demo.py")


def test_run_bandit_rejects_non_object_report(monkeypatch):
    class FakeCompletedProcess:
        returncode = 0
        stdout = json.dumps([])
        stderr = ""

    monkeypatch.setattr(
        bandit_runner.subprocess,
        "run",
        lambda *args, **kwargs: FakeCompletedProcess(),
    )

    with pytest.raises(RuntimeError, match="report structure"):
        bandit_runner.run_bandit("tests/fixtures/bandit_demo.py")

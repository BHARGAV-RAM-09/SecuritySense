
import sys

import pytest

from app.agents.verifier import verify_with_pytest


def test_verifier_records_successful_test_run(tmp_path):
    test_file = tmp_path / "test_example.py"
    test_file.write_text(
        "def test_example():\n"
        "    assert 2 + 2 == 4\n",
        encoding="utf-8",
    )

    result = verify_with_pytest(tmp_path, test_file)

    assert result["status"] == "passed"
    assert result["verified"] is True
    assert result["return_code"] == 0


def test_verifier_records_failed_test_run(tmp_path):
    test_file = tmp_path / "test_example.py"
    test_file.write_text(
        "def test_example():\n"
        "    assert 2 + 2 == 5\n",
        encoding="utf-8",
    )

    result = verify_with_pytest(tmp_path, test_file)

    assert result["status"] == "failed"
    assert result["verified"] is False
    assert result["return_code"] != 0


def test_verifier_rejects_test_outside_workspace(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    outside_test = tmp_path / "test_outside.py"
    outside_test.write_text(
        "def test_example():\n"
        "    assert True\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="inside the workspace"):
        verify_with_pytest(workspace, outside_test)


@pytest.mark.parametrize("timeout", [0, -1, 121, True, 1.5, "30"])
def test_verifier_rejects_invalid_timeout(tmp_path, timeout):
    test_file = tmp_path / "test_example.py"
    test_file.write_text("def test_example():\n    assert True\n", encoding="utf-8")

    with pytest.raises(ValueError, match="timeout_seconds"):
        verify_with_pytest(tmp_path, test_file, timeout)


def test_verifier_returns_inconclusive_on_timeout(tmp_path, monkeypatch):
    test_file = tmp_path / "test_example.py"
    test_file.write_text("def test_example():\n    assert True\n", encoding="utf-8")

    def timeout_run(*args, **kwargs):
        raise __import__("subprocess").TimeoutExpired(
            cmd="pytest",
            timeout=1,
        )

    monkeypatch.setattr("app.agents.verifier.subprocess.run", timeout_run)

    result = verify_with_pytest(tmp_path, test_file)

    assert result["status"] == "inconclusive"
    assert result["verified"] is False
    assert result["return_code"] is None

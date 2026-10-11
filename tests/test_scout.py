
import pytest

from app.agents.scout import discover_python_files


def test_scout_discovers_python_fixtures():
    files = discover_python_files("tests")
    names = {path.name for path in files}

    assert "vulnerable_app.py" in names
    assert "secure_app.py" in names
    assert "bandit_demo.py" in names


def test_scout_excludes_virtual_environment():
    files = discover_python_files(".")
    assert all(".venv" not in path.parts for path in files)


def test_scout_rejects_missing_directory():
    with pytest.raises(ValueError):
        discover_python_files("directory_that_does_not_exist")


def test_scout_rejects_zero_file_limit():
    with pytest.raises(ValueError):
        discover_python_files("tests", max_files=0)


def test_scout_respects_file_limit():
    files = discover_python_files("tests", max_files=1)
    assert len(files) == 1

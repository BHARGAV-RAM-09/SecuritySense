
from app.agents.scout import discover_python_files_detailed


def test_scout_reports_limit_when_more_python_files_exist():
    result = discover_python_files_detailed("tests/fixtures", max_files=1)

    assert len(result["files"]) == 1
    assert result["limit_reached"] is True


def test_scout_does_not_report_limit_when_all_files_fit():
    result = discover_python_files_detailed("tests/fixtures", max_files=100)

    assert result["limit_reached"] is False
    assert len(result["files"]) <= 100

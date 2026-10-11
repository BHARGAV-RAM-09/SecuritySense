
import pytest

from app.agents.investigator import investigate_finding


@pytest.fixture
def workspace(tmp_path):
    source = tmp_path / "sample.py"
    source.write_text(
        "def greet():\n"
        "    password = 'example-placeholder'\n"
        "    return password\n",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def finding():
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


def test_investigator_collects_source_context(workspace, finding):
    result = investigate_finding(finding, workspace)

    assert result["investigation_status"] == "evidence_collected"
    assert result["source_context"]
    assert result["source_context"][1]["line"] == 2
    assert result["reproduced"] is False
    assert result["fix_verified"] is False


def test_investigator_rejects_path_escape(workspace, finding):
    finding["file"] = "../outside.py"

    result = investigate_finding(finding, workspace)

    assert result["investigation_status"] == "inconclusive"
    assert result["source_context"] == []


def test_investigator_rejects_invalid_line(workspace, finding):
    finding["line"] = 0

    result = investigate_finding(finding, workspace)

    assert result["investigation_status"] == "inconclusive"


@pytest.mark.parametrize("context_lines", [-1, 21, True, 1.5])
def test_investigator_rejects_invalid_context_lines(
    workspace, finding, context_lines
):
    with pytest.raises(ValueError):
        investigate_finding(finding, workspace, context_lines=context_lines)

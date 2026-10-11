
from app.proofloop.patch import propose_access_control_patch
from app.proofloop.apply_patch import apply_proposal_to_copy

def vulnerable_source():
    return (
        "USERS = {}\n\n"
        "def get_profile(requester: str, requested_user: str):\n"
        "    if requested_user not in USERS:\n"
        "        return None\n\n"
        "    # BUG: requester is ignored; any caller can access any profile.\n"
        "    return USERS[requested_user]\n"
    )


def test_patch_proposal_contains_authorization_check(tmp_path):
    source = tmp_path / "vulnerable_app.py"
    original = vulnerable_source()
    source.write_text(original, encoding="utf-8")

    result = propose_access_control_patch(source)

    assert result["status"] == "passed"
    assert result["original_modified"] is False
    assert "if requester != requested_user:" in result["proposed_content"]
    assert result["patch"]
    assert source.read_text(encoding="utf-8") == original


def test_patch_proposal_rejects_unsupported_source(tmp_path):
    source = tmp_path / "unrelated.py"
    original = "def hello():\n    return 'hello'\n"
    source.write_text(original, encoding="utf-8")

    result = propose_access_control_patch(source)

    assert result["status"] == "inconclusive"
    assert result["patch"] is None
    assert result["original_modified"] is False
    assert source.read_text(encoding="utf-8") == original


def test_patch_proposal_rejects_missing_file(tmp_path):
    missing = tmp_path / "missing.py"

    try:
        propose_access_control_patch(missing)
    except ValueError as exc:
        assert "existing regular file" in str(exc)
    else:
        raise AssertionError("Expected ValueError for missing source file")

def test_apply_proposal_writes_to_new_copy_and_preserves_original(tmp_path):
    source = tmp_path / "vulnerable_app.py"
    original = vulnerable_source()
    source.write_text(original, encoding="utf-8")

    proposal = propose_access_control_patch(source)
    destination = tmp_path / "disposable" / "secure_app.py"
    destination.parent.mkdir()

    result = apply_proposal_to_copy(proposal, destination)

    assert result["status"] == "passed"
    assert result["original_modified"] is False
    assert "if requester != requested_user:" in destination.read_text(
        encoding="utf-8"
    )
    assert source.read_text(encoding="utf-8") == original


def test_apply_proposal_refuses_to_overwrite_existing_file(tmp_path):
    destination = tmp_path / "existing.py"
    destination.write_text("keep this content", encoding="utf-8")

    proposal = {
        "status": "passed",
        "proposed_content": "replacement",
    }

    try:
        apply_proposal_to_copy(proposal, destination)
    except FileExistsError:
        pass
    else:
        raise AssertionError("Expected FileExistsError")

    assert destination.read_text(encoding="utf-8") == "keep this content"


def test_apply_proposal_rejects_inconclusive_proposal(tmp_path):
    destination = tmp_path / "new.py"

    proposal = {
        "status": "inconclusive",
        "proposed_content": "replacement",
    }

    try:
        apply_proposal_to_copy(proposal, destination)
    except ValueError as exc:
        assert "successful patch proposals" in str(exc)
    else:
        raise AssertionError("Expected ValueError")

    assert not destination.exists()

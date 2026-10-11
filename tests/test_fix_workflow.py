
from app.proofloop.fix_workflow import run_controlled_fix_workflow


def test_controlled_fix_workflow_preserves_original(tmp_path):
    source = tmp_path / "vulnerable_app.py"
    original = (
        "USERS = {'alice': {'name': 'Alice'}, 'bob': {'name': 'Bob'}}\n\n"
        "def get_profile(requester: str, requested_user: str):\n"
        "    if requested_user not in USERS:\n"
        "        return None\n\n"
        "    # BUG: requester is ignored; any caller can access any profile.\n"
        "    return USERS[requested_user]\n"
    )
    source.write_text(original, encoding="utf-8")

    test_file = tmp_path / "test_example.py"
    test_file.write_text(
        "def test_example():\n"
        "    assert 2 + 2 == 4\n",
        encoding="utf-8",
    )

    result = run_controlled_fix_workflow(source, test_file)

    assert result["patch_status"] == "passed"
    assert result["application_status"] == "passed"
    assert result["verification"]["status"] == "passed"
    assert result["verification"]["verified"] is True
    assert result["original_modified"] is False
    assert source.read_text(encoding="utf-8") == original


def test_controlled_fix_workflow_rejects_unsupported_source(tmp_path):
    source = tmp_path / "unrelated.py"
    source.write_text(
        "def hello():\n    return 'hello'\n",
        encoding="utf-8",
    )

    test_file = tmp_path / "test_example.py"
    test_file.write_text(
        "def test_example():\n    assert True\n",
        encoding="utf-8",
    )

    result = run_controlled_fix_workflow(source, test_file)

    assert result["patch_status"] == "inconclusive"
    assert result["application_status"] == "unrun"
    assert result["verification"]["status"] == "unrun"
    assert result["original_modified"] is False

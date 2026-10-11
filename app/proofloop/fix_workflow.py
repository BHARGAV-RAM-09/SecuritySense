
"""Run a controlled patch-and-verification workflow safely."""

import tempfile
from pathlib import Path
from typing import Any

from app.agents.verifier import verify_with_pytest
from app.proofloop.apply_patch import apply_proposal_to_copy
from app.proofloop.patch import propose_access_control_patch


def run_controlled_fix_workflow(
    source: str | Path,
    test_file: str | Path,
) -> dict[str, Any]:
    """Patch a disposable copy and test its access-control behavior."""
    source_path = Path(source).resolve()
    test_path = Path(test_file).resolve()

    result: dict[str, Any] = {
        "patch_status": "unrun",
        "patch_proposal": None,
        "application_status": "unrun",
        "verification": {"status": "unrun", "verified": False},
        "original_modified": False,
        "cleanup_status": "unrun",
        "execution_scope": "temporary_copy_only",
    }

    if not source_path.is_file():
        result["patch_status"] = "inconclusive"
        result["error"] = "Source must be an existing regular file."
        return result

    if not test_path.is_file():
        result["verification"] = {
            "status": "inconclusive",
            "verified": False,
            "error": "Test file must be an existing regular file.",
        }
        return result

    # The supplied test path is checked for compatibility, but its contents
    # are never executed. Verification uses fixed tests generated below.
    try:
        original_bytes = source_path.read_bytes()
    except OSError as exc:
        result["patch_status"] = "inconclusive"
        result["error"] = f"Could not read source: {type(exc).__name__}"
        return result

    try:
        proposal = propose_access_control_patch(source_path)
        result["patch_proposal"] = {
            key: value
            for key, value in proposal.items()
            if key != "proposed_content"
        }
        result["patch_status"] = proposal.get("status", "inconclusive")

        if result["patch_status"] != "passed":
            return result

        with tempfile.TemporaryDirectory(
            prefix="securitysense-fix-"
        ) as temporary_directory:
            temp_root = Path(temporary_directory)
            disposable_source = temp_root / "vulnerable_app.py"
            disposable_test = temp_root / "test_patched_access_control.py"

            application = apply_proposal_to_copy(
                proposal,
                disposable_source,
            )
            result["application_status"] = application.get(
                "status", "inconclusive"
            )

            if result["application_status"] != "passed":
                result["verification"] = {
                    "status": "inconclusive",
                    "verified": False,
                    "error": "Patch application did not succeed.",
                }
                return result

            # These tests exercise the patched function, not the original.
            disposable_test.write_text(
                "from vulnerable_app import get_profile\n\n"
                "def test_non_owner_cannot_access_profile():\n"
                "    assert get_profile('alice', 'bob') is None\n\n"
                "def test_owner_can_access_own_profile():\n"
                "    result = get_profile('bob', 'bob')\n"
                "    assert result is not None\n"
                "    assert result.get('name') == 'Bob'\n\n"
                "def test_unknown_profile_is_denied():\n"
                "    assert get_profile('alice', 'unknown') is None\n",
                encoding="utf-8",
            )

            verification = verify_with_pytest(
                temp_root,
                disposable_test,
            )
            result["verification"] = verification
            result["cleanup_status"] = "completed"

    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        if result["patch_status"] == "unrun":
            result["patch_status"] = "inconclusive"
        if result["application_status"] == "unrun":
            result["application_status"] = "inconclusive"
        if result["verification"]["status"] == "unrun":
            result["verification"] = {
                "status": "inconclusive",
                "verified": False,
                "error": result["error"],
            }

    finally:
        try:
            result["original_modified"] = (
                source_path.read_bytes() != original_bytes
            )
        except OSError:
            result["original_modified"] = None
            result["original_integrity_check"] = "inconclusive"

        if result["original_modified"] is True:
            result["verification"] = {
                "status": "inconclusive",
                "verified": False,
                "error": "Original source integrity check failed.",
            }

    return result

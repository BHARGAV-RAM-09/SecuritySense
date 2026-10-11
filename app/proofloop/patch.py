
"""Create reviewable patch proposals without modifying source files."""

import difflib
from pathlib import Path
from typing import Any


def propose_access_control_patch(
    source: str | Path,
) -> dict[str, Any]:
    """Propose the controlled access-control fix for an exact known fixture."""
    source_path = Path(source).resolve()

    if not source_path.exists() or not source_path.is_file():
        raise ValueError("Source must be an existing regular file.")

    original = source_path.read_text(encoding="utf-8")

    vulnerable_block = (
        "    if requested_user not in USERS:\n"
        "        return None\n\n"
        "    # BUG: requester is ignored; any caller can access any profile.\n"
        "    return USERS[requested_user]"
    )

    secure_block = (
        "    if requester != requested_user:\n"
        "        return None\n\n"
        "    if requested_user not in USERS:\n"
        "        return None\n\n"
        "    return USERS[requested_user]"
    )

    if original.count(vulnerable_block) != 1:
        return {
            "status": "inconclusive",
            "source": str(source_path),
            "reason": "Source does not contain the exact supported vulnerable block.",
            "original_modified": False,
            "patch": None,
        }

    proposed = original.replace(vulnerable_block, secure_block, 1)

    diff = "".join(
        difflib.unified_diff(
            original.splitlines(keepends=True),
            proposed.splitlines(keepends=True),
            fromfile=f"a/{source_path.name}",
            tofile=f"b/{source_path.name}",
        )
    )

    return {
        "status": "passed",
        "source": str(source_path),
        "reason": "Exact supported access-control block matched.",
        "original_modified": False,
        "patch": diff,
        "proposed_content": proposed,
    }

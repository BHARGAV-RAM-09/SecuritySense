
"""Apply an approved patch proposal to a new disposable file."""

from pathlib import Path
from typing import Any


def apply_proposal_to_copy(
    proposal: dict[str, Any],
    destination: str | Path,
) -> dict[str, Any]:
    """Write proposed content to a new file without overwriting anything."""
    if not isinstance(proposal, dict):
        raise TypeError("proposal must be a dictionary.")

    if proposal.get("status") != "passed":
        raise ValueError("Only successful patch proposals can be applied.")

    proposed_content = proposal.get("proposed_content")
    if not isinstance(proposed_content, str):
        raise ValueError("Proposal does not contain valid proposed content.")

    destination_path = Path(destination).resolve()

    if destination_path.exists():
        raise FileExistsError("Destination already exists; refusing to overwrite.")

    if not destination_path.parent.exists():
        raise ValueError("Destination parent directory must already exist.")

    if not destination_path.parent.is_dir():
        raise ValueError("Destination parent must be a directory.")

    # Exclusive creation prevents accidental overwrites.
    with destination_path.open("x", encoding="utf-8", newline="") as handle:
        handle.write(proposed_content)

    return {
        "status": "passed",
        "destination": str(destination_path),
        "original_modified": False,
        "bytes_written": destination_path.stat().st_size,
    }

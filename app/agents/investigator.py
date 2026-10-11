
"""Investigate scanner findings using available source-code evidence."""

from pathlib import Path
from typing import Any


def investigate_finding(
    finding: dict[str, Any],
    workspace: str | Path,
    context_lines: int = 3,
) -> dict[str, Any]:
    """Attach source evidence without overstating a finding's validity."""
    if not isinstance(finding, dict):
        raise TypeError("finding must be a dictionary.")

    if (
        isinstance(context_lines, bool)
        or not isinstance(context_lines, int)
        or context_lines < 0
        or context_lines > 20
    ):
        raise ValueError("context_lines must be an integer between 0 and 20.")

    root = Path(workspace).resolve()

    if not root.is_dir():
        raise ValueError("Workspace must be an existing directory.")

    relative_file = finding.get("file")
    line_number = finding.get("line")

    result: dict[str, Any] = {
        "finding": finding.copy(),
        "investigation_status": "inconclusive",
        "evidence": [],
        "source_context": [],
        "assessment": (
            "The scanner reported a candidate finding. "
            "Further validation is required to establish exploitability."
        ),
        "reproduced": False,
        "fix_verified": False,
    }

    if not isinstance(relative_file, str) or not relative_file.strip():
        result["evidence"].append(
            {
                "type": "validation",
                "detail": "Finding has no valid file path.",
            }
        )
        return result

    if (
        isinstance(line_number, bool)
        or not isinstance(line_number, int)
        or line_number < 1
    ):
        result["evidence"].append(
            {
                "type": "validation",
                "detail": "Finding has no valid line number.",
            }
        )
        return result

    candidate = Path(relative_file)

    try:
        if candidate.is_absolute():
            source_path = candidate.resolve()
        else:
            source_path = (root / candidate).resolve()

        # Absolute and relative paths must resolve inside the workspace.
        source_path.relative_to(root)
    except (ValueError, OSError, RuntimeError):
        result["evidence"].append(
            {
                "type": "validation",
                "detail": "Finding path escapes the workspace or is invalid.",
            }
        )
        return result

    if not source_path.is_file() or source_path.suffix.lower() != ".py":
        result["evidence"].append(
            {
                "type": "validation",
                "detail": "Finding does not reference a Python file.",
            }
        )
        return result

    try:
        source_lines = source_path.read_text(
            encoding="utf-8"
        ).splitlines()
    except (OSError, UnicodeError):
        result["evidence"].append(
            {
                "type": "source_read_error",
                "detail": "Could not read the referenced source file.",
            }
        )
        return result

    if line_number > len(source_lines):
        result["evidence"].append(
            {
                "type": "validation",
                "detail": "Finding line number is outside the source file.",
            }
        )
        return result

    start = max(1, line_number - context_lines)
    end = min(len(source_lines), line_number + context_lines)

    result["source_context"] = [
        {
            "line": number,
            "code": source_lines[number - 1],
        }
        for number in range(start, end + 1)
    ]

    # Report a workspace-relative path, not an absolute machine path.
    display_path = source_path.relative_to(root).as_posix()

    result["evidence"].append(
        {
            "type": "source_location",
            "file": display_path,
            "line": line_number,
            "detail": (
                "Source context was read from the referenced "
                "workspace file."
            ),
        }
    )

    result["investigation_status"] = "evidence_collected"
    result["assessment"] = (
        "Source context was collected for the scanner finding. "
        "This supports review but does not independently prove exploitability."
    )

    return result

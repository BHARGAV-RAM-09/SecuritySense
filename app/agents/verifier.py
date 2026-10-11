
"""Verify a patched disposable copy using explicitly selected pytest tests."""

import subprocess
import sys
from pathlib import Path
from typing import Any


def verify_with_pytest(
    workspace: str | Path,
    test_file: str | Path,
    timeout_seconds: int = 30,
) -> dict[str, Any]:
    """Run a selected test file and record the actual pytest outcome."""
    if (
        isinstance(timeout_seconds, bool)
        or not isinstance(timeout_seconds, int)
        or not 1 <= timeout_seconds <= 120
    ):
        raise ValueError("timeout_seconds must be an integer from 1 to 120.")

    workspace_path = Path(workspace).resolve()
    test_path = Path(test_file).resolve()

    if not workspace_path.is_dir():
        raise ValueError("Workspace must be an existing directory.")

    if not test_path.is_file():
        raise ValueError("Test file must be an existing regular file.")

    try:
        test_path.relative_to(workspace_path)
    except ValueError as exc:
        raise ValueError("Test file must be inside the workspace.") from exc

    command = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        str(test_path),
    ]

    try:
        completed = subprocess.run(
            command,
            cwd=workspace_path,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "status": "inconclusive",
            "verified": False,
            "return_code": None,
            "stdout": "",
            "stderr": "Verification timed out.",
            "test_file": str(test_path),
        }
    except OSError as exc:
        return {
            "status": "inconclusive",
            "verified": False,
            "return_code": None,
            "stdout": "",
            "stderr": f"{type(exc).__name__}: {exc}",
            "test_file": str(test_path),
        }

    status = "passed" if completed.returncode == 0 else "failed"

    return {
        "status": status,
        "verified": completed.returncode == 0,
        "return_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "test_file": str(test_path),
    }

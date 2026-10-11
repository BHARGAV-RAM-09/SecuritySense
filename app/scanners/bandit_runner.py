
"""Run Bandit against an explicitly selected, controlled target."""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def run_bandit(
    target: str | Path,
    timeout_seconds: int = 30,
) -> dict[str, Any]:
    """Run Bandit and return a validated JSON report."""
    if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, int):
        raise ValueError("timeout_seconds must be a positive integer.")

    if timeout_seconds < 1 or timeout_seconds > 120:
        raise ValueError("timeout_seconds must be between 1 and 120.")

    target_path = Path(target).resolve()

    if not target_path.exists():
        raise FileNotFoundError(f"Scanner target does not exist: {target_path}")

    if not target_path.is_file() and not target_path.is_dir():
        raise ValueError("Scanner target must be a file or directory.")

    command = [
        sys.executable,
        "-m",
        "bandit",
        "-f",
        "json",
        "-q",
        str(target_path),
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError("Bandit scan exceeded its time limit.") from exc

    # Bandit can return exit code 1 when findings are present.
    if result.returncode not in (0, 1):
        raise RuntimeError(
            f"Bandit could not complete the scan: {result.stderr.strip()}"
        )

    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Bandit did not return valid JSON.") from exc

    if not isinstance(report, dict):
        raise RuntimeError("Bandit returned an unexpected report structure.")

    results = report.get("results")
    if not isinstance(results, list):
        raise RuntimeError("Bandit report is missing its results list.")

    if not all(isinstance(item, dict) for item in results):
        raise RuntimeError("Bandit report contains an invalid finding.")

    return report

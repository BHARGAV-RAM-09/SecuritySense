
"""Scan discovered Python files and report successes, failures, and limits."""

from pathlib import Path
from typing import Any

from app.agents.scout import discover_python_files_detailed
from app.scanners.bandit_runner import run_bandit
from app.scanners.findings import normalize_bandit_report


def scan_workspace(
    root: str | Path,
    max_files: int = 500,
) -> dict[str, Any]:
    """Scan discovered Python files and report successes, failures, and limits."""
    discovery = discover_python_files_detailed(root, max_files=max_files)
    files = discovery["files"]

    findings: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    scanned_files = 0

    for file_path in files:
        try:
            report = run_bandit(file_path)
            file_findings = normalize_bandit_report(report)
        except Exception as exc:
            failures.append(
                {
                    "file": str(file_path),
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
            continue

        findings.extend(file_findings)
        scanned_files += 1

    if failures and scanned_files == 0:
        status = "failed"
    elif failures or discovery["limit_reached"]:
        status = "partial"
    else:
        status = "completed"

    return {
        "files_discovered": len(files),
        "files_scanned": scanned_files,
        "files_failed": len(failures),
        "limit_reached": discovery["limit_reached"],
        "findings_count": len(findings),
        "findings": findings,
        "failures": failures,
        "scan_status": status,
    }

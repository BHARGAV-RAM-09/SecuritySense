
"""Coordinate scanning, investigation, controlled reproduction, and evidence."""

from pathlib import Path
from typing import Any

from app.agents.investigator import investigate_finding
from app.agents.reproducer import reproduce_access_control
from app.proofloop.evidence import build_proofloop_evidence
from app.proofloop.fix_workflow import run_controlled_fix_workflow
from app.scanners.scan_workspace import scan_workspace


def run_security_analysis(
    workspace: str | Path,
    max_files: int = 500,
    context_lines: int = 3,
) -> dict[str, Any]:
    """Run analysis and preserve honest status for every workflow stage."""
    workspace_path = Path(workspace).resolve()

    scan_result = scan_workspace(
        workspace_path,
        max_files=max_files,
    )

    investigations: list[dict[str, Any]] = []
    investigation_failures: list[dict[str, Any]] = []
    proofloop_records: list[dict[str, Any]] = []

    for finding in scan_result["findings"]:
        try:
            investigation = investigate_finding(
                finding=finding,
                workspace=workspace_path,
                context_lines=context_lines,
            )
            investigations.append(investigation)
        except Exception as exc:
            investigation_failures.append(
                {
                    "rule_id": finding.get("rule_id"),
                    "file": finding.get("file"),
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
            continue

        proofloop_records.append(
            build_proofloop_evidence(
                finding=finding,
                investigation=investigation,
            )
        )

    # Reproduction is limited to the project's controlled fixtures.
    try:
        controlled_reproduction = reproduce_access_control()
    except Exception as exc:
        controlled_reproduction = {
            "status": "inconclusive",
            "vulnerability_reproduced": False,
            "evidence": [],
            "error": f"{type(exc).__name__}: {exc}",
            "execution_scope": "controlled_project_fixtures",
        }

    project_root = Path(__file__).resolve().parents[2]
    fixtures_dir = (project_root / "tests" / "fixtures").resolve()

    # Run the fix demonstration only for explicitly trusted project paths.
    # Never run this workflow against an arbitrary submitted workspace.
    approved_workspaces = {
        project_root.resolve(),
        fixtures_dir,
    }

    fix_workflow: dict[str, Any] = {
        "patch_status": "unrun",
        "application_status": "unrun",
        "verification": {
            "status": "unrun",
            "verified": False,
        },
        "original_modified": False,
        "reason": "Controlled access-control demo has not been run.",
        "scope": "controlled_access_control_fixture",
    }

    if workspace_path in approved_workspaces:
        source_fixture = fixtures_dir / "vulnerable_app.py"
        test_fixture = project_root / "tests" / "test_access_control.py"

        try:
            fix_workflow = run_controlled_fix_workflow(
                source=source_fixture,
                test_file=test_fixture,
            )
            fix_workflow["scope"] = "controlled_access_control_fixture"
        except Exception as exc:
            fix_workflow = {
                "patch_status": "inconclusive",
                "application_status": "inconclusive",
                "verification": {
                    "status": "inconclusive",
                    "verified": False,
                    "error": f"{type(exc).__name__}: {exc}",
                },
                "original_modified": False,
                "error": f"{type(exc).__name__}: {exc}",
                "scope": "controlled_access_control_fixture",
            }

    verification = fix_workflow.get("verification") or {}
    verification_status = verification.get("status", "unrun")

    return {
        "workspace": str(workspace_path),
        "scan_status": scan_result["scan_status"],
        "files_discovered": scan_result["files_discovered"],
        "files_scanned": scan_result["files_scanned"],
        "files_failed": scan_result["files_failed"],
        "limit_reached": scan_result["limit_reached"],
        "findings_count": scan_result["findings_count"],
        "findings": scan_result["findings"],
        "investigations": investigations,
        "investigations_completed": len(investigations),
        "investigations_failed": len(investigation_failures),
        "investigation_failures": investigation_failures,
        "proofloop_records": proofloop_records,
        "controlled_reproduction": controlled_reproduction,
        "reproduction_status": controlled_reproduction.get(
            "status", "inconclusive"
        ),
        "fix_workflow": fix_workflow,
        "fix_status": fix_workflow.get("patch_status", "unrun"),
        "patch_application_status": fix_workflow.get(
            "application_status", "unrun"
        ),
        "verification_status": verification_status,
        "fix_verified": verification.get("verified") is True,
        "original_modified": fix_workflow.get("original_modified", False),
        "failures": scan_result["failures"],
    }

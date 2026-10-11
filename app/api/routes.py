
"""SecuritySense API routes for controlled security analysis."""

from copy import deepcopy
from pathlib import Path
from threading import Lock
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.orchestrator import run_security_analysis

router = APIRouter(prefix="/api", tags=["Security Analysis"])

# Only scan directories explicitly configured by the server operator.
# Never accept arbitrary server filesystem paths from an API client.
ALLOWED_WORKSPACES = [
    Path("tests/fixtures").resolve(),
]

_SCAN_RESULTS: dict[str, dict] = {}
_SCAN_LOCK = Lock()


class ScanRequest(BaseModel):
    """Input for a scan of an approved local workspace."""

    workspace_name: str = Field(
        default="demo",
        min_length=1,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
    )
    max_files: int = Field(default=100, ge=1, le=500)
    context_lines: int = Field(default=3, ge=0, le=10)


def _get_scan(scan_id: str) -> dict:
    """Return a scan result or raise a consistent 404 response."""
    with _SCAN_LOCK:
        result = _SCAN_RESULTS.get(scan_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Scan not found.")
        return deepcopy(result)


@router.get("/status")
def api_status() -> dict[str, str]:
    """Report the scan API's availability."""
    return {
        "status": "ready",
        "message": "Security analysis API is available.",
    }


@router.post("/scans", status_code=201)
def create_scan(request: ScanRequest) -> dict:
    """Run analysis against the configured demonstration workspace."""
    if request.workspace_name != "demo":
        raise HTTPException(
            status_code=400,
            detail="Only the configured demo workspace is available currently.",
        )

    workspace = ALLOWED_WORKSPACES[0]

    if not workspace.is_dir():
        raise HTTPException(
            status_code=503,
            detail="The configured demo workspace is unavailable.",
        )

    try:
        result = run_security_analysis(
            workspace=workspace,
            max_files=request.max_files,
            context_lines=request.context_lines,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Security analysis could not complete: {type(exc).__name__}",
        ) from exc

    scan_id = str(uuid4())
    stored_result = {
        "scan_id": scan_id,
        **result,
    }

    with _SCAN_LOCK:
        _SCAN_RESULTS[scan_id] = stored_result

    return {
        "scan_id": scan_id,
        "scan_status": result["scan_status"],
        "findings_count": result["findings_count"],
        "message": "Scan completed; retrieve its result using scan_id.",
    }


@router.get("/scans/{scan_id}")
def get_scan(scan_id: str) -> dict:
    """Retrieve the full result of a scan."""
    return _get_scan(scan_id)


@router.get("/scans/{scan_id}/findings")
def get_scan_findings(scan_id: str) -> dict:
    """Retrieve findings and investigation evidence for a scan."""
    result = _get_scan(scan_id)
    return {
        "scan_id": result["scan_id"],
        "scan_status": result["scan_status"],
        "findings_count": result["findings_count"],
        "findings": result["findings"],
        "investigations": result["investigations"],
        "proofloop_records": result["proofloop_records"],
    }


@router.get("/scans/{scan_id}/report")
def get_scan_report(scan_id: str) -> dict:
    """Return a concise, evidence-based scan report."""
    result = _get_scan(scan_id)
    return {
        "scan_id": result["scan_id"],
        "workspace": result["workspace"],
        "scan_status": result["scan_status"],
        "files_discovered": result["files_discovered"],
        "files_scanned": result["files_scanned"],
        "files_failed": result["files_failed"],
        "limit_reached": result["limit_reached"],
        "findings_count": result["findings_count"],
        "investigations_completed": result["investigations_completed"],
        "investigations_failed": result["investigations_failed"],
        "reproduction_status": result["reproduction_status"],
        "fix_status": result["fix_status"],
        "verification_status": result["verification_status"],
        "failures": result["failures"],
        "investigation_failures": result["investigation_failures"],
    }

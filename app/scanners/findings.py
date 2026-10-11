
from typing import Any


def normalize_bandit_report(report: dict[str, Any]) -> list[dict[str, Any]]:
    """Convert Bandit JSON results into SecuritySense finding records."""
    normalized = []

    for item in report.get("results", []):
        normalized.append(
            {
                "tool": "bandit",
                "rule_id": item.get("test_id"),
                "severity": (item.get("issue_severity") or "UNKNOWN").upper(),
                "confidence": (item.get("issue_confidence") or "UNKNOWN").upper(),
                "message": item.get("issue_text", "No description provided"),
                "file": item.get("filename"),
                "line": item.get("line_number"),
                "code": item.get("code"),
            }
        )

    return normalized


"""Reproduce the controlled access-control demonstration safely."""

from typing import Any

from tests.fixtures.secure_app import get_profile as secure_get_profile
from tests.fixtures.vulnerable_app import get_profile as vulnerable_get_profile


def reproduce_access_control() -> dict[str, Any]:
    """Compare vulnerable and secure fixtures using controlled test inputs."""
    evidence: list[dict[str, Any]] = []

    try:
        vulnerable_result = vulnerable_get_profile("alice", "bob")
        vulnerable_exposed = (
            isinstance(vulnerable_result, dict)
            and vulnerable_result.get("name") == "Bob"
        )

        evidence.append(
            {
                "check": "unauthorized_access_vulnerable_fixture",
                "expected": "Alice must not receive Bob's profile",
                "observed": (
                    "Bob's profile was returned"
                    if vulnerable_exposed
                    else "Bob's profile was not returned"
                ),
                "passed": vulnerable_exposed,
            }
        )

        secure_result = secure_get_profile("alice", "bob")
        secure_denied = secure_result is None

        evidence.append(
            {
                "check": "unauthorized_access_secure_fixture",
                "expected": "Alice must be denied Bob's profile",
                "observed": (
                    "Access was denied"
                    if secure_denied
                    else "A profile was returned"
                ),
                "passed": secure_denied,
            }
        )

        owner_result = secure_get_profile("bob", "bob")
        owner_allowed = (
            isinstance(owner_result, dict)
            and owner_result.get("name") == "Bob"
        )

        evidence.append(
            {
                "check": "owner_access_secure_fixture",
                "expected": "Bob can access his own profile",
                "observed": (
                    "Bob's profile was returned"
                    if owner_allowed
                    else "Bob's profile was not returned"
                ),
                "passed": owner_allowed,
            }
        )

    except Exception as exc:
        return {
            "status": "failed",
            "vulnerability_reproduced": False,
            "checks_passed": sum(item["passed"] for item in evidence),
            "checks_total": 3,
            "evidence": evidence,
            "error": f"{type(exc).__name__}: {exc}",
            "execution_scope": "controlled_project_fixtures",
        }

    all_checks_passed = all(item["passed"] for item in evidence)

    return {
        "status": "passed" if all_checks_passed else "failed",
        "vulnerability_reproduced": (
            evidence[0]["passed"]
            and evidence[1]["passed"]
            and evidence[2]["passed"]
        ),
        "checks_passed": sum(item["passed"] for item in evidence),
        "checks_total": len(evidence),
        "evidence": evidence,
        "execution_scope": "controlled_project_fixtures",
    }

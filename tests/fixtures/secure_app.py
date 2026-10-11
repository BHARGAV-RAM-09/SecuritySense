
# SecuritySense controlled secure fixture
# Demonstrates authorization enforced before profile access.

USERS = {
    "alice": {"name": "Alice", "email": "alice@example.com"},
    "bob": {"name": "Bob", "email": "bob@example.com"},
}


def get_profile(requester: str, requested_user: str) -> dict | None:
    """Return a profile only when the requester is authorized."""
    if requester != requested_user:
        return None

    if requested_user not in USERS:
        return None

    return USERS[requested_user]

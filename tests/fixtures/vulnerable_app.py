
# SecuritySense controlled vulnerability fixture
# Demonstrates broken access control.

USERS = {
    "alice": {"name": "Alice", "email": "alice@example.com"},
    "bob": {"name": "Bob", "email": "bob@example.com"},
}


def get_profile(requester: str, requested_user: str) -> dict | None:
    """Return the requested user's profile.

    Vulnerability: the function checks whether the target user exists,
    but never checks whether the requester is authorized to access it.
    """
    if requested_user not in USERS:
        return None

    # BUG: requester is ignored; any caller can access any profile.
    return USERS[requested_user]

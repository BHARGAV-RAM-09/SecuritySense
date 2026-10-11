
from fixtures.vulnerable_app import get_profile as vulnerable_get_profile
from fixtures.secure_app import get_profile as secure_get_profile


def test_vulnerable_app_allows_unauthorized_profile_access():
    """Demonstrate the bug: Alice can access Bob's profile."""
    result = vulnerable_get_profile("alice", "bob")

    assert result is not None
    assert result["name"] == "Bob"


def test_secure_app_denies_unauthorized_profile_access():
    """Verify the fix: Alice cannot access Bob's profile."""
    result = secure_get_profile("alice", "bob")

    assert result is None


def test_secure_app_allows_owner_to_access_own_profile():
    """Verify that Bob can still access his own profile."""
    result = secure_get_profile("bob", "bob")

    assert result is not None
    assert result["name"] == "Bob"

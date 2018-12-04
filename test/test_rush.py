"""Basic tests for our rush public API."""
import rush


def test_rush_has_a_version():
    """A basic test to start our project."""
    assert isinstance(getattr(rush, "__version__", None), str)

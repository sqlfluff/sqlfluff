"""Init PY for tests."""
import pytest

# Register helper functions
# Needed for introspection in case of failure.
pytest.register_assert_rewrite('sqlfluff.testing')

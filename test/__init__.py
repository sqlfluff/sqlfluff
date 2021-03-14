"""Init PY for tests."""
import pytest

# Register helper functions
pytest.register_assert_rewrite('sqlfluff.testing')

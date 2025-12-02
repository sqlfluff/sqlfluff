"""Common test fixtures for reflow modules."""

import pytest

from sqlfluff.core import FluffConfig


@pytest.fixture()
def default_config():
    """Return the default config for reflow tests."""
    return FluffConfig(overrides={"dialect": "ansi"})

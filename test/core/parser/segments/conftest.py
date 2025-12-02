"""Common fixtures for segment tests."""

import pytest

from sqlfluff.core.parser import BaseSegment


@pytest.fixture(scope="module")
def raw_segments(generate_test_segments):
    """Construct a list of raw segments as a fixture."""
    return generate_test_segments(["foobar", ".barfoo"])


@pytest.fixture(scope="module")
def raw_seg(raw_segments):
    """Construct a raw segment as a fixture."""
    return raw_segments[0]


@pytest.fixture(scope="session")
def DummySegment():
    """Construct a raw segment as a fixture."""

    class DummySegment(BaseSegment):
        """A dummy segment for testing with no grammar."""

        type = "dummy"

    return DummySegment


@pytest.fixture(scope="session")
def DummyAuxSegment():
    """Construct a raw segment as a fixture."""

    class DummyAuxSegment(BaseSegment):
        """A different dummy segment for testing with no grammar."""

        type = "dummy_aux"

    return DummyAuxSegment

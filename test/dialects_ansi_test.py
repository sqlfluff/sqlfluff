"""Tests specific to the ansi dialect."""

import pytest
import logging

from sqlfluff.parser import FileSegment
from sqlfluff.config import FluffConfig


@pytest.mark.parametrize(
    "raw,res",
    [
        ("a b", ['a', ' ', 'b']),
        ("b.c", ['b', '.', 'c']),
        ("abc \n \t def  ;blah", ['abc', ' ', '\n', ' \t ', 'def', '  ', ';', 'blah'])
    ]
)
def test__dialect__ansi__file_from_raw(raw, res, caplog):
    """Test we don't drop bits on simple examples."""
    config = FluffConfig(overrides=dict(dialect='ansi'))
    with caplog.at_level(logging.DEBUG):
        fs = FileSegment.from_raw(raw, config=config)
    # From just the initial parse, check we're all there
    assert fs.raw == raw
    assert fs.raw_list() == res

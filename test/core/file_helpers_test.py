"""Test the helpers."""

import pytest

from sqlfluff.core import FluffConfig
from sqlfluff.core.file_helpers import get_encoding


@pytest.mark.parametrize(
    "fname,config_encoding,result",
    [
        (
            "test/fixtures/linter/encoding-utf-8.sql",
            "autodetect",
            "ascii",  # ascii is a subset of utf-8, this is valid
        ),
        (
            "test/fixtures/linter/encoding-utf-8-sig.sql",
            "autodetect",
            "UTF-8-SIG",
        ),
        (
            "test/fixtures/linter/encoding-utf-8.sql",
            "utf-8",
            "utf-8",
        ),
        (
            "test/fixtures/linter/encoding-utf-8-sig.sql",
            "utf-8",
            "utf-8",
        ),
        (
            "test/fixtures/linter/encoding-utf-8.sql",
            "utf-8-sig",
            "utf-8-sig",
        ),
        (
            "test/fixtures/linter/encoding-utf-8-sig.sql",
            "utf-8-sig",
            "utf-8-sig",
        ),
    ],
)
def test__parser__helper_get_encoding(fname, config_encoding, result):
    """Test get_encoding."""
    assert (
        get_encoding(
            fname=fname, config=FluffConfig(overrides={"encoding": config_encoding})
        )
        == result
    )

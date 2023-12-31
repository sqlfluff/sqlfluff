"""Test the helpers."""

import os.path
from pathlib import Path

import pytest

from sqlfluff.core.helpers.file import get_encoding, iter_intermediate_paths


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
            fname=fname,
            config_encoding=config_encoding,
        )
        == result
    )


@pytest.mark.parametrize(
    "path,working_path,result",
    [
        (
            # Standard use case.
            # SQLFluff run from an outer location, looking to an inner.
            ["test", "fixtures", "config", "inheritance_a", "nested", "blah.sql"],
            "test/fixtures",
            # Order should work up from outer to inner
            [
                "test/fixtures",
                "test/fixtures/config",
                "test/fixtures/config/inheritance_a",
                "test/fixtures/config/inheritance_a/nested",
            ],
        ),
        (
            # Reverse use case.
            # SQLFluff running from an inner location, looking to outer.
            ["test", "fixtures"],
            "test/fixtures/config/inheritance_a",
            # Should only return inner, then outer.
            [
                "test/fixtures/config/inheritance_a",
                "test/fixtures",
            ],
        ),
        (
            # Unrelated use case.
            # SQLFluff running from an one location, looking to parallel.
            ["test", "fixtures"],
            "test/core",
            # Should each individually, with the working location first
            [
                "test/core",
                "test/fixtures",
            ],
        ),
    ],
)
def test__config__iter_config_paths(path, working_path, result):
    """Test that config paths are fetched ordered by priority."""
    cfg_paths = iter_intermediate_paths(Path(os.path.join(*path)), Path(working_path))
    assert [str(p) for p in cfg_paths] == [str(Path(p).resolve()) for p in result]

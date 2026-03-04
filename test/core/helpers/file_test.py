"""Test the helpers."""

import sys
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
            "utf-8-sig",
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


def test__parser__helper_get_encoding_utf16_bom(tmp_path):
    """Test get_encoding returns utf-16 for UTF-16 BOM files."""
    test_file = tmp_path / "utf16_bom.sql"
    test_file.write_bytes(
        b"\xff\xfeS\x00E\x00L\x00E\x00C\x00T\x00 \x001\x00;\x00\n\x00"
    )

    assert get_encoding(fname=str(test_file), config_encoding="autodetect") == "utf-16"


def test__parser__helper_get_encoding_chardet_path(tmp_path, monkeypatch):
    """Test get_encoding returns detected encoding when chardet provides one."""
    test_file = tmp_path / "detected_encoding.sql"
    test_file.write_bytes(b"\x93quoted text\x94\n")

    monkeypatch.setattr(
        "sqlfluff.core.helpers.file.chardet.detect",
        lambda data: {"encoding": "Windows-1252"},
    )

    assert (
        get_encoding(fname=str(test_file), config_encoding="autodetect")
        == "Windows-1252"
    )


def test__parser__helper_get_encoding_chardet_none_fallback(tmp_path, monkeypatch):
    """Test get_encoding falls back to utf-8 when chardet returns no encoding."""
    test_file = tmp_path / "fallback_utf8.sql"
    test_file.write_bytes(b"\x80\x81\x82")

    monkeypatch.setattr(
        "sqlfluff.core.helpers.file.chardet.detect",
        lambda data: {"encoding": None},
    )

    assert get_encoding(fname=str(test_file), config_encoding="autodetect") == "utf-8"


@pytest.mark.parametrize(
    "path,working_path,result",
    [
        (
            # Standard use case.
            # SQLFluff run from an outer location, looking to an inner.
            "test/fixtures/config/inheritance_a/nested/blah.sql",
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
            "test/fixtures",
            "test/fixtures/config/inheritance_a",
            # Should only return inner, then outer.
            [
                # "test/fixtures/config/inheritance_a",  # This SHOULD be present
                "test/fixtures",
            ],
        ),
        (
            # Unrelated use case.
            # SQLFluff running from an one location, looking to parallel.
            "test/fixtures",
            "test/core",
            # Should each individually, with the working location first
            [
                "test",  # This SHOULD NOT be present.
                # "test/core",  # This SHOULD be present.
                "test/fixtures",
            ],
        ),
    ],
)
def test__config__iter_config_paths(path, working_path, result):
    """Test that config paths are fetched ordered by priority."""
    cfg_paths = iter_intermediate_paths(Path(path), Path(working_path))
    assert [str(p) for p in cfg_paths] == [str(Path(p).resolve()) for p in result]


@pytest.mark.skipif(sys.platform != "win32", reason="Only applicable on Windows")
def test__config__iter_config_paths_exc_win():
    """Test that config path resolution exception handling works on windows."""
    cfg_paths = iter_intermediate_paths(Path("J:\\\\"), Path("C:\\\\"))
    assert list(cfg_paths) == [Path("C:\\\\"), Path("J:\\\\")]


@pytest.mark.skipif(sys.platform == "win32", reason="Not applicable on Windows")
def test__config__iter_config_paths_exc_unix():
    """Test that config path resolution exception handling works on linux."""
    cfg_paths = iter_intermediate_paths(Path("/abc/def"), Path("/ghi/jlk"))
    # NOTE: `/def` doesn't exist, so we'll use it's parent instead because `.is_dir()`
    # will return false. This should still test the "zero path length" handling routine.
    assert list(cfg_paths) == [Path("/"), Path("/abc")]

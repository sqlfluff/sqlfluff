"""Tests the path routines from the Linter class."""

import os

import pytest

from sqlfluff.core.errors import SQLFluffUserError
from sqlfluff.core.linter.discovery import _load_specs_from_lines, paths_from_path


def normalise_paths(paths):
    """Test normalising paths.

    NB Paths on difference platforms might look different, so this
    makes them comparable.
    """
    return {pth.replace("/", ".").replace("\\", ".") for pth in paths}


def test__linter__path_from_paths__dir():
    """Test extracting paths from directories."""
    paths = paths_from_path("test/fixtures/lexer")
    assert normalise_paths(paths) == {
        "test.fixtures.lexer.block_comment.sql",
        "test.fixtures.lexer.inline_comment.sql",
        "test.fixtures.lexer.basic.sql",
    }


def test__linter__path_from_paths__default():
    """Test .sql files are found by default."""
    paths = normalise_paths(paths_from_path("test/fixtures/linter"))
    assert "test.fixtures.linter.passing.sql" in paths
    assert "test.fixtures.linter.passing_cap_extension.SQL" in paths
    assert "test.fixtures.linter.discovery_file.txt" not in paths


def test__linter__path_from_paths__exts():
    """Test configuration of file discovery."""
    paths = normalise_paths(
        paths_from_path("test/fixtures/linter", target_file_exts=[".txt", ".txt.j2"])
    )
    assert "test.fixtures.linter.passing.sql" not in paths
    assert "test.fixtures.linter.passing_cap_extension.SQL" not in paths
    assert "test.fixtures.linter.discovery_file.txt" in paths
    assert "test.fixtures.linter.discovery_file.txt.j2" in paths


def test__linter__path_from_paths__file():
    """Test extracting paths from a file path."""
    paths = paths_from_path("test/fixtures/linter/indentation_errors.sql")
    assert normalise_paths(paths) == {"test.fixtures.linter.indentation_errors.sql"}


def test__linter__path_from_paths__not_exist():
    """Test that the right errors are raise when a file doesn't exist."""
    with pytest.raises(SQLFluffUserError):
        paths_from_path("asflekjfhsakuefhse")


def test__linter__path_from_paths__not_exist_ignore():
    """Test extracting paths from a file path."""
    paths = paths_from_path("asflekjfhsakuefhse", ignore_non_existent_files=True)
    assert len(paths) == 0


def test__linter__path_from_paths__explicit_ignore():
    """Test ignoring files that were passed explicitly."""
    paths = paths_from_path(
        "test/fixtures/linter/sqlfluffignore/path_a/query_a.sql",
        ignore_non_existent_files=True,
        ignore_files=True,
        working_path="test/fixtures/linter/sqlfluffignore/",
    )
    assert len(paths) == 0


def test__linter__path_from_paths__sqlfluffignore_current_directory():
    """Test that .sqlfluffignore in the current directory is read when dir given."""
    oldcwd = os.getcwd()
    try:
        os.chdir("test/fixtures/linter/sqlfluffignore")
        paths = paths_from_path(
            "path_a/",
            ignore_non_existent_files=True,
            ignore_files=True,
            working_path="test/fixtures/linter/sqlfluffignore/",
        )
        assert len(paths) == 0
    finally:
        os.chdir(oldcwd)


def test__linter__path_from_paths__dot():
    """Test extracting paths from a dot."""
    # Use set theory to check that we get AT LEAST these files
    assert normalise_paths(paths_from_path(".")) >= {
        "test.fixtures.lexer.block_comment.sql",
        "test.fixtures.lexer.inline_comment.sql",
        "test.fixtures.lexer.basic.sql",
    }


@pytest.mark.parametrize(
    "path",
    [
        "test/fixtures/linter/sqlfluffignore",
        "test/fixtures/linter/sqlfluffignore/",
        "test/fixtures/linter/sqlfluffignore/.",
    ],
)
def test__linter__path_from_paths__ignore(path):
    """Test extracting paths from a dot."""
    # We should only get query_b, because of the sqlfluffignore files.
    assert normalise_paths(paths_from_path(path)) == {
        "test.fixtures.linter.sqlfluffignore.path_b.query_b.sql"
    }


def test__linter__path_from_paths__specific_bad_ext():
    """Test we get no match if a path with the wrong extension is passed."""
    assert paths_from_path("README.md") == []


@pytest.mark.parametrize(
    "lines",
    [
        12345,  # Something not iterable
        ["!"],  # An iterable, with an invalid pattern in it.
    ],
)
def test__linter__load_specs_from_lines(lines):
    """Test the unhappy path of _load_specs_from_lines.

    This is typically if we pass something un-iterable,
    or an invalid pattern
    """
    with pytest.raises(SQLFluffUserError):
        _load_specs_from_lines(lines, "<test>")

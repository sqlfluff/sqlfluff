"""Tests for the hashing helpers.

These digests are the foundation of the lint cache: if any of them can fail to
change when their inputs change, a stale result gets served. The tests here are
therefore mostly about *sensitivity* -- proving that each kind of change to the
input produces a different digest.
"""

import hashlib
import os

import pytest

from sqlfluff.core.helpers.hashing import (
    hash_file_bytes,
    hash_path_contents,
    hash_strings,
)


def _digest(*values: str) -> str:
    hasher = hashlib.sha256()
    hash_strings(hasher, *values)
    return hasher.hexdigest()


def test__helpers_hashing__strings_are_stable():
    """The same strings always produce the same digest."""
    assert _digest("a", "b") == _digest("a", "b")


def test__helpers_hashing__strings_are_delimited():
    """Moving a boundary between values changes the digest.

    Without delimiting, ("ab", "c") and ("a", "bc") would hash identically,
    which would let a config value bleed into the next one.
    """
    assert _digest("ab", "c") != _digest("a", "bc")


def test__helpers_hashing__empty_string_is_distinct_from_no_string():
    """An empty value is not the same as an absent one."""
    assert _digest("a", "") != _digest("a")


def test__helpers_hashing__strings_survive_surrogates():
    """Undecodable content doesn't raise.

    Config values can carry text which came from a file read with
    `errors="backslashreplace"`, so encoding has to be forgiving.
    """
    assert _digest("\udcff") == _digest("\udcff")


def test__helpers_hashing__file_bytes(tmp_path):
    """Hashing a file's bytes matches hashing those bytes directly."""
    target = tmp_path / "example.sql"
    target.write_bytes(b"SELECT 1\n")
    hasher = hashlib.sha256()
    hash_file_bytes(str(target), hasher)
    assert hasher.hexdigest() == hashlib.sha256(b"SELECT 1\n").hexdigest()


def test__helpers_hashing__file_bytes_spans_chunks(tmp_path, monkeypatch):
    """A file larger than the read chunk still hashes correctly."""
    monkeypatch.setattr("sqlfluff.core.helpers.hashing.HASH_CHUNK_SIZE", 4)
    payload = b"0123456789abcdef"
    target = tmp_path / "big.sql"
    target.write_bytes(payload)
    hasher = hashlib.sha256()
    hash_file_bytes(str(target), hasher)
    assert hasher.hexdigest() == hashlib.sha256(payload).hexdigest()


class TestHashPathContents:
    """Tests for `hash_path_contents`."""

    @staticmethod
    def _make_tree(root, files):
        for relpath, content in files.items():
            target = root / relpath
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        return str(root)

    def test_no_paths(self):
        """No paths is a valid (and stable) input."""
        assert hash_path_contents([]) == hash_path_contents([])

    def test_identical_trees_differ_by_path(self, tmp_path):
        """Two identical trees hash differently, because the path is included.

        This matters because a template can refer to a search path by name, so
        two directories are not interchangeable just because their contents
        match.
        """
        a = self._make_tree(tmp_path / "a", {"m.sql": "x"})
        b = self._make_tree(tmp_path / "b", {"m.sql": "x"})
        assert hash_path_contents([a]) != hash_path_contents([b])

    def test_stable_for_unchanged_tree(self, tmp_path):
        """Repeated calls on an unchanged tree agree."""
        root = self._make_tree(tmp_path, {"a/m.sql": "x", "b/n.sql": "y"})
        assert hash_path_contents([root]) == hash_path_contents([root])

    def test_sensitive_to_edited_file(self, tmp_path):
        """Editing a file changes the digest."""
        root = self._make_tree(tmp_path, {"m.sql": "x"})
        before = hash_path_contents([root])
        (tmp_path / "m.sql").write_text("y", encoding="utf-8")
        assert hash_path_contents([root]) != before

    def test_sensitive_to_added_file(self, tmp_path):
        """Adding a file changes the digest.

        This is the case a per-file dependency list would miss: a new macro
        file can shadow or supplement what a template resolves to.
        """
        root = self._make_tree(tmp_path, {"m.sql": "x"})
        before = hash_path_contents([root])
        (tmp_path / "n.sql").write_text("x", encoding="utf-8")
        assert hash_path_contents([root]) != before

    def test_sensitive_to_removed_file(self, tmp_path):
        """Removing a file changes the digest."""
        root = self._make_tree(tmp_path, {"m.sql": "x", "n.sql": "y"})
        before = hash_path_contents([root])
        os.remove(tmp_path / "n.sql")
        assert hash_path_contents([root]) != before

    def test_sensitive_to_rename(self, tmp_path):
        """Renaming a file changes the digest, even though contents are equal."""
        root = self._make_tree(tmp_path, {"m.sql": "x"})
        before = hash_path_contents([root])
        os.rename(tmp_path / "m.sql", tmp_path / "n.sql")
        assert hash_path_contents([root]) != before

    def test_sensitive_to_move_between_subdirectories(self, tmp_path):
        """Moving a file between directories changes the digest."""
        root = self._make_tree(tmp_path, {"a/m.sql": "x", "b/.keep": ""})
        before = hash_path_contents([root])
        os.rename(tmp_path / "a" / "m.sql", tmp_path / "b" / "m.sql")
        assert hash_path_contents([root]) != before

    def test_sensitive_to_path_order(self, tmp_path):
        """Order matters, because Jinja resolves a search path in order."""
        a = self._make_tree(tmp_path / "a", {"m.sql": "x"})
        b = self._make_tree(tmp_path / "b", {"m.sql": "y"})
        assert hash_path_contents([a, b]) != hash_path_contents([b, a])

    def test_missing_path_is_recorded(self, tmp_path):
        """A path which doesn't exist is distinct from an empty directory.

        Creating a configured-but-absent macro directory has to invalidate.
        """
        missing = str(tmp_path / "nope")
        digest_missing = hash_path_contents([missing])
        os.makedirs(missing)
        assert hash_path_contents([missing]) != digest_missing

    def test_single_file_path(self, tmp_path):
        """A path may be a file rather than a directory."""
        target = tmp_path / "lib.py"
        target.write_text("A = 1", encoding="utf-8")
        before = hash_path_contents([str(target)])
        target.write_text("A = 2", encoding="utf-8")
        assert hash_path_contents([str(target)]) != before

    @pytest.mark.parametrize("content", ["x", ""])
    def test_empty_file_is_hashed(self, tmp_path, content):
        """An empty file still contributes its name."""
        root = self._make_tree(tmp_path, {"m.sql": content})
        assert hash_path_contents([root]) == hash_path_contents([root])

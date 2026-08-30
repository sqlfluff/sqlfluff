"""Hashing helpers used to fingerprint inputs to a lint run.

These live outside the linter package because templaters need them too, and a
templater should not have to import the linter in order to describe what it
reads.

Everything here is about producing digests which are *stable* (the same inputs
always give the same digest, in this process and the next) and *sensitive* (any
change to the inputs changes the digest). They are not used for anything
security related: the goal is to detect accidental staleness, not to resist an
adversary.
"""

import hashlib
import os

#: Read files in chunks so that a very large file isn't held in memory purely
#: to be fingerprinted.
HASH_CHUNK_SIZE = 1024 * 1024


def hash_file_bytes(fname: str, hasher: "hashlib._Hash") -> None:
    """Feed the raw bytes of a file into a hasher.

    We deliberately hash *bytes* rather than decoded text. Encoding detection
    is itself configuration dependent, so hashing bytes means that a change of
    encoding is necessarily a change of digest.
    """
    with open(fname, "rb") as f:
        while True:
            chunk = f.read(HASH_CHUNK_SIZE)
            if not chunk:
                break
            hasher.update(chunk)


def hash_strings(hasher: "hashlib._Hash", *values: str) -> None:
    """Feed length delimited strings into a hasher.

    Delimiting means that ``("ab", "c")`` and ``("a", "bc")`` produce different
    digests, so two distinct inputs cannot be made to collide simply by moving
    a boundary between them.
    """
    for value in values:
        encoded = value.encode("utf-8", errors="backslashreplace")
        hasher.update(str(len(encoded)).encode("ascii"))
        hasher.update(b"\0")
        hasher.update(encoded)
        hasher.update(b"\0")


def hash_path_contents(paths: list[str]) -> str:
    """Return a stable digest of the contents of a set of files or directories.

    This is the building block templaters use to fingerprint the external files
    they read (Jinja macro directories, python library directories and so on).
    Directories are walked in sorted order and every file within contributes
    both its relative path and its contents, so adding, removing, renaming or
    editing any file changes the digest.

    A path which does not exist contributes a marker rather than being ignored,
    so that creating it later is also a change.

    Args:
        paths: The paths to fingerprint, in a meaningful order. Order is part
            of the digest, because search order can affect how a template
            resolves.

    Returns:
        A hex digest of the contents of all the given paths.
    """
    hasher = hashlib.sha256()
    for path in paths:
        # The configured path is part of the digest in its own right: two
        # directories with identical contents are not interchangeable, because
        # a template may refer to one of them by name.
        hash_strings(hasher, "path", path)
        if os.path.isfile(path):
            hash_strings(hasher, "file", "")
            hash_file_bytes(path, hasher)
        elif os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path):
                # Sort in place so that os.walk descends deterministically.
                dirnames.sort()
                for filename in sorted(filenames):
                    full = os.path.join(dirpath, filename)
                    hash_strings(hasher, "entry", os.path.relpath(full, path))
                    try:
                        hash_file_bytes(full, hasher)
                    except OSError as err:
                        # An unreadable file folds the error into the digest
                        # rather than being treated as though it were absent.
                        hash_strings(hasher, "unreadable", str(err))
        else:
            hash_strings(hasher, "missing", "")
    return hasher.hexdigest()

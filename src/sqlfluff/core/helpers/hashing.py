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

    ``surrogatepass`` rather than ``backslashreplace``: filenames can contain
    bytes which don't decode, and ``os.fsdecode`` represents those as lone
    surrogates. ``backslashreplace`` would render such a surrogate as the
    literal text of an escape sequence, which is exactly what a file whose name
    contains that text encodes to -- so two different names could produce the
    same digest. ``surrogatepass`` encodes the surrogate itself, which is
    injective.
    """
    for value in values:
        encoded = value.encode("utf-8", errors="surrogatepass")
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
            hash_strings(hasher, "file", _file_digest(path))
        elif os.path.isdir(path):
            # NOTE: `followlinks=True`. The default is False, but a Jinja
            # loader reads straight through a symlinked directory, so leaving
            # it out would let an edit to a linked-in macro go unnoticed and
            # replay a stale clean result. `seen` breaks the cycles that
            # following links can introduce.
            seen: set[str] = set()
            for dirpath, dirnames, filenames in os.walk(path, followlinks=True):
                real = os.path.realpath(dirpath)
                if real in seen:
                    # Reached by another route already, so its contents are in
                    # the digest and re-walking would not terminate on a cycle.
                    #
                    # The *name* still has to count. A second link to an
                    # already-walked directory makes those files resolvable
                    # under a new name -- `{% include "z_alias/m.sql" %}` where
                    # only `macros/m.sql` existed before -- so adding or
                    # retargeting the link changes what Jinja can render even
                    # though no file changed. Recording the alias and where it
                    # points makes both of those a change of digest.
                    hash_strings(hasher, "alias", os.path.relpath(dirpath, path), real)
                    dirnames[:] = []
                    continue
                seen.add(real)
                # Sort in place so that os.walk descends deterministically.
                dirnames.sort()
                for filename in sorted(filenames):
                    full = os.path.join(dirpath, filename)
                    hash_strings(
                        hasher,
                        "entry",
                        os.path.relpath(full, path),
                        _file_digest(full),
                    )
        else:
            hash_strings(hasher, "missing", "")
    return hasher.hexdigest()


def _file_digest(fname: str) -> str:
    """Digest one file's contents, or the reason it could not be read.

    Returned as a fixed-length string and fed through `hash_strings` rather
    than streamed into the caller's hasher directly. Raw bytes carry no
    boundary, so a file whose contents happened to look like the encoding of a
    following entry could make an added file leave the hash input unchanged.
    """
    hasher = hashlib.sha256()
    try:
        hash_file_bytes(fname, hasher)
    except OSError as err:
        # An unreadable file folds the error into the digest rather than being
        # treated as though it were absent.
        return f"unreadable:{err}"
    return hasher.hexdigest()

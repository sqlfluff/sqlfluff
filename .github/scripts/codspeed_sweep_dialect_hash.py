"""Content hash for the Rust dialect-codegen pipeline, for the checked-out worktree.

`utils/rustify.py build` (~105s per the local perf_sweep tool's own
measurements) regenerates sqlfluffrs/sqlfluffrs_dialects/src/dialect/** from
utils/build_dialect.py, build_lexers.py, build_parsers.py, build_dialects.py,
src/sqlfluff/core/dialects/**, src/sqlfluff/core/parser/**, and
src/sqlfluff/dialects/**. Its output is architecture-independent text, and
most commits in a sweep don't touch any of these paths, so this hash lets
the workflow cache the generated files and skip regenerating them.

Mirrors utils/perf_sweep/dialect_cache.py's GENERATION_PATHS, but hashes the
already-checked-out worktree directly (this runs after `git checkout --force
<sha>` in the CodSpeed sweep workflow) rather than using git archive.
"""

from __future__ import annotations

import hashlib
import os

GENERATION_PATHS = [
    "utils/rustify.py",
    "utils/build_dialect.py",
    "utils/build_lexers.py",
    "utils/build_parsers.py",
    "utils/build_dialects.py",
    "src/sqlfluff/core/dialects",
    "src/sqlfluff/core/parser",
    "src/sqlfluff/dialects",
]


def _collect_files(paths: list) -> list:
    files = []
    for path in paths:
        if os.path.isfile(path):
            files.append(path)
        elif os.path.isdir(path):
            for root, _dirs, names in os.walk(path):
                files.extend(os.path.join(root, name) for name in names)
    return files


def main() -> None:
    """Hash the checked-out worktree's dialect-generation inputs and write it out."""
    existing = [p for p in GENERATION_PATHS if os.path.exists(p)]
    if not existing:
        raise RuntimeError(
            "none of the dialect-generation paths exist in this checkout"
        )

    digest = hashlib.sha256()
    for path in sorted(_collect_files(existing)):
        digest.update(path.encode())
        with open(path, "rb") as f:
            digest.update(f.read())

    with open(os.environ["GITHUB_OUTPUT"], "a") as f:
        f.write(f"hash={digest.hexdigest()}\n")


if __name__ == "__main__":
    main()

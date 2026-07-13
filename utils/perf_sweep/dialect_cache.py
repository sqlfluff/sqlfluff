"""Content hash for the Rust dialect-codegen pipeline.

`utils/rustify.py build` runs utils/build_dialect.py, build_lexers.py,
build_parsers.py and build_dialects.py, which together introspect
src/sqlfluff/core/dialects/**, src/sqlfluff/core/parser/** (grammar/segments
the generators walk) and src/sqlfluff/dialects/** (the actual dialect
definitions) to emit Rust source. All of that has to be in the cache key, not
just the dialect definitions - a change to grammar/sequence.py or the
generator scripts themselves can change the output with zero dialect diff,
and there's no CI check that would catch that drift for us.

Uses git plumbing only (ls-tree/cat-file/archive), so it never requires a
checkout - the same code path works for a real run and for --dry-run.
"""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

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


def _existing_paths(repo_dir: Path, sha: str) -> list:
    existing = []
    for path in GENERATION_PATHS:
        probe = subprocess.run(
            ["git", "-C", str(repo_dir), "cat-file", "-e", f"{sha}:{path}"],
            capture_output=True,
        )
        if probe.returncode == 0:
            existing.append(path)
    return existing


def compute_generation_hash(repo_dir: Path, sha: str) -> str:
    """Hash of everything that can affect `rustify.py build`'s output, as of `sha`."""
    paths = _existing_paths(repo_dir, sha)
    if not paths:
        raise RuntimeError(f"none of the dialect-generation paths exist at {sha}")
    archive = subprocess.run(
        ["git", "-C", str(repo_dir), "archive", sha, "--", *paths],
        capture_output=True,
        check=True,
    ).stdout
    return hashlib.sha256(archive).hexdigest()

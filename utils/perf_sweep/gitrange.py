"""Git commit-range resolution and the sweep's persistent worktree.

Also holds the dialect/docs-only skip rule used to decide which commits
in a range are worth building and measuring.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# A commit is skippable only if *every* changed path matches one of these.
# Broad rule (agreed): dialect source + its tests/fixtures, plus docs/changelog.
SKIP_PATTERNS = [
    re.compile(r"^src/sqlfluff/dialects/"),
    re.compile(r"^src/sqlfluff/rules/"),
    re.compile(r"^src/sqlfluff/core/rules?/"),
    re.compile(r"^src/sqlfluff/core/templaters/"),
    re.compile(r"^test/"),
    re.compile(r"^CHANGELOG\.md$"),
    re.compile(r"(^|/)AGENTS\.md$"),
    re.compile(r"^docs/"),
    re.compile(r"^docsv/"),
    re.compile(r"^plugins/"),
    re.compile(r"^utils/"),
    re.compile(r"^\.github/"),
    re.compile(r"^pyproject\.toml$"),
    re.compile(r"^sqlfluffrs/sqlfluffrs_benchmarks/"),
    re.compile(r"^sqlfluffrs/tests?/"),
]


def run_git(
    repo_dir: Path, *args: str, check: bool = True
) -> subprocess.CompletedProcess:
    """Run `git -C repo_dir <args>`, capturing text output."""
    return subprocess.run(
        ["git", "-C", str(repo_dir), *args],
        capture_output=True,
        text=True,
        check=check,
    )


@dataclass
class CommitInfo:
    """One commit in the swept range plus its skip classification."""

    sha: str
    parent: Optional[str]
    author_date: str
    subject: str
    changed_files: list
    skip: bool
    skip_reason: Optional[str]


def classify_skip(files: list) -> tuple:
    """Return (skip, reason) for a commit's changed-file list."""
    if not files:
        return True, "empty diff (no files changed)"
    if all(any(p.match(f) for p in SKIP_PATTERNS) for f in files):
        return True, (
            "dialect/rules source, core rules/templaters, plugins, utils, test/, docs, "
            "changelog, AGENTS.md, CI workflows, pyproject.toml, or the Rust benchmarks/tests only"
        )
    return False, None


def resolve_commits(repo_dir: Path, start_ref: str, end_ref: str) -> list:
    """Return commits in [start_ref, end_ref], oldest first.

    Each is classified against the skip rule via a diff against its first
    parent. Uses `start_ref^..end_ref` (rather than plain
    `start_ref..end_ref`) so start_ref itself is included, not just its
    descendants.
    """
    rng = f"{start_ref}^..{end_ref}"
    out = run_git(
        repo_dir,
        "log",
        "--reverse",
        "--format=%H%x01%P%x01%ad%x01%s",
        "--date=iso-strict",
        rng,
    ).stdout

    result = []
    for line in out.splitlines():
        if not line:
            continue
        sha, parents, date, subject = line.split("\x01", 3)
        parent_list = parents.split()
        parent = parent_list[0] if parent_list else None

        if parent is None:
            files: list = []
        else:
            diff = run_git(repo_dir, "diff", "--name-only", parent, sha).stdout
            files = [f for f in diff.splitlines() if f]

        skip, reason = classify_skip(files)
        result.append(CommitInfo(sha, parent, date, subject, files, skip, reason))
    return result


def ensure_worktree(repo_dir: Path, worktree_dir: Path, seed_ref: str) -> None:
    """Create the sweep's persistent worktree at worktree_dir if missing."""
    if worktree_dir.exists():
        return
    # If a previous run's output directory (containing this worktree) was
    # deleted without `git worktree remove`, git still has it registered and
    # refuses to recreate it at the same path until pruned.
    run_git(repo_dir, "worktree", "prune")
    worktree_dir.parent.mkdir(parents=True, exist_ok=True)
    run_git(repo_dir, "worktree", "add", "--detach", str(worktree_dir), seed_ref)


def checkout_commit(worktree_dir: Path, sha: str) -> None:
    """Detach the persistent worktree onto sha, discarding local changes."""
    run_git(worktree_dir, "checkout", "--detach", "--force", sha)

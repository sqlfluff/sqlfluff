"""Compute which commits the CodSpeed historical sweep should benchmark.

Used by the `plan` job in .github/workflows/codspeed-sweep.yml. Reads
COMMIT_COUNT from the environment, walks `main` back to the v4.2.2 floor
(rust_parser.py doesn't exist before it, so the benchmark file's
module-level import would fail outright on anything older, a much older
boundary than the native_ast skip guard in test_codspeed_tpc_parse.py,
which covers commits *after* this floor but before PR #7983), drops any
commit already recorded in .github/codspeed-swept.json, further drops any
commit whose entire diff is perf-irrelevant (see SKIP_PATTERNS below, ported
from the retired utils/perf_sweep tool's gitrange.classify_skip since that
tool no longer exists in this repo), and writes `all_shas`/`has_work` to
$GITHUB_OUTPUT.

Alternatively, if COMMIT_SHA is set (non-empty), that single commit is
selected instead of walking COMMIT_COUNT commits back from `main`. An
explicitly-named commit bypasses the perf-irrelevance filter — the user
asked for it, so they get it — but is still dropped if already recorded in
.github/codspeed-swept.json, since CodSpeed errors on a duplicate SHA.
"""

from __future__ import annotations

import json
import os
import re
import subprocess

SWEPT_PATH = ".github/codspeed-swept.json"

# This fork carries no tags of its own, so the release tags (including the
# 4.2.2 sweep floor used below) have to be fetched from upstream.
UPSTREAM_URL = "https://github.com/sqlfluff/sqlfluff.git"

# A commit is skippable only if *every* changed path matches one of these.
# Dialect source + its tests/fixtures, plus docs/changelog/CI config, none
# of which can move parse performance.
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


def _is_skippable(files: list) -> bool:
    # An empty diff (e.g. a no-op merge commit) is skippable too, same as
    # the retired tool's classify_skip.
    return not files or all(any(p.match(f) for p in SKIP_PATTERNS) for f in files)


def _changed_files(sha: str) -> list:
    diff = subprocess.run(
        ["git", "diff", "--name-only", f"{sha}^", sha],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [f for f in diff.splitlines() if f]


def _resolve_commit(rev: str) -> str:
    """Resolve a user-supplied revision to a full commit hash."""
    result = subprocess.run(
        ["git", "rev-parse", "--verify", f"{rev}^{{commit}}"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SystemExit(f"commit_sha {rev!r} is not a known commit in this repo.")
    return result.stdout.strip()


def main() -> None:
    """Select the commits to sweep this run and write them to $GITHUB_OUTPUT."""
    commit_sha = os.environ.get("COMMIT_SHA", "").strip()

    swept = set(json.load(open(SWEPT_PATH))) if os.path.exists(SWEPT_PATH) else set()

    if commit_sha:
        # No tag fetch needed here: an explicitly-named commit doesn't use
        # the 4.2.2 floor, and the checkout already has the fork's full
        # history.
        requested = [_resolve_commit(commit_sha)]
        # Explicitly-named commits bypass the perf-irrelevance filter; only
        # the already-swept check applies (a duplicate SHA is a hard error on
        # CodSpeed's side, not a wasted run).
        remaining = [sha for sha in requested if sha not in swept]
        benchmarkable = remaining
        skipped = 0
    else:
        commit_count = int(os.environ["COMMIT_COUNT"])

        subprocess.run(
            ["git", "fetch", "--tags", "--quiet", UPSTREAM_URL],
            check=True,
        )

        requested = subprocess.run(
            ["git", "log", "-n", str(commit_count), "--format=%H", "4.2.2^..main"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.split()

        remaining = [sha for sha in requested if sha not in swept]

        benchmarkable = []
        skipped = 0
        for sha in remaining:
            if _is_skippable(_changed_files(sha)):
                skipped += 1
            else:
                benchmarkable.append(sha)

    with open(os.environ["GITHUB_OUTPUT"], "a") as f:
        f.write(f"all_shas={json.dumps(benchmarkable)}\n")
        f.write(f"has_work={'true' if benchmarkable else 'false'}\n")

    already = len(requested) - len(remaining)
    print(
        f"{len(requested)} commit(s) requested, {already} already swept, "
        f"{skipped} skipped as perf-irrelevant, "
        f"{len(benchmarkable)} to benchmark this run."
    )


if __name__ == "__main__":
    main()

"""Compute which commits the CodSpeed historical sweep should benchmark.

Used by the `plan` job in .github/workflows/codspeed-sweep.yml. Reads
COMMIT_COUNT from the environment, walks `main` back to the v4.2.2 floor
(rust_parser.py doesn't exist before it, so the benchmark file's
module-level import would fail outright on anything older, a much older
boundary than the native_ast skip guard in test_codspeed_tpc_parse.py,
which covers commits *after* this floor but before PR #7983), drops any
commit already recorded in .github/codspeed-swept.json, further drops any
commit that utils/perf_sweep/gitrange.classify_skip would skip (dialect,
rules, docs, tests, or similarly perf-irrelevant diffs, same reasoning as
the local sweep tool), and writes `all_shas`/`has_work` to $GITHUB_OUTPUT.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.perf_sweep.gitrange import classify_skip  # noqa: E402

SWEPT_PATH = ".github/codspeed-swept.json"


def _changed_files(sha: str) -> list:
    diff = subprocess.run(
        ["git", "diff", "--name-only", f"{sha}^", sha],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [f for f in diff.splitlines() if f]


def main() -> None:
    """Select the commits to sweep this run and write them to $GITHUB_OUTPUT."""
    commit_count = int(os.environ["COMMIT_COUNT"])

    swept = set(json.load(open(SWEPT_PATH))) if os.path.exists(SWEPT_PATH) else set()

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
        skip, _reason = classify_skip(_changed_files(sha))
        if skip:
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

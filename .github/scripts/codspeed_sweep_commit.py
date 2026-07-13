"""Commit .github/codspeed-swept.json if the finalize step updated it.

Used by the `finalize` job in .github/workflows/codspeed-sweep.yml, after
codspeed_sweep_finalize.py has merged newly-swept commits into the file.
No-ops cleanly if nothing changed.
"""

from __future__ import annotations

import os
import subprocess

SWEPT_PATH = ".github/codspeed-swept.json"


def main() -> None:
    """Commit and push the tracking file if it changed, otherwise no-op."""
    unchanged = (
        subprocess.run(["git", "diff", "--quiet", "--", SWEPT_PATH]).returncode == 0
    )
    if unchanged:
        print("No new commits to record.")
        return

    run_id = os.environ["GITHUB_RUN_ID"]
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)
    subprocess.run(
        ["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"],
        check=True,
    )
    subprocess.run(["git", "add", SWEPT_PATH], check=True)
    subprocess.run(
        [
            "git",
            "commit",
            "-m",
            f"chore: record CodSpeed-swept commits from run {run_id}",
        ],
        check=True,
    )
    subprocess.run(["git", "push"], check=True)


if __name__ == "__main__":
    main()

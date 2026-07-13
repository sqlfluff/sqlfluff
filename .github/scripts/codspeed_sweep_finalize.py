"""Record which commits the CodSpeed historical sweep fully benchmarked.

Used by the `finalize` job in .github/workflows/codspeed-sweep.yml. Queries
this workflow run's own jobs via the GitHub API and cross-checks, for each
commit, that the `walltime <sha>` job and every `simulation <sha> <group>`
shard job succeeded (a commit only counts as done once both instrument types
have fully uploaded, mirroring the local sweep's two-metrics-per-commit
design). Merges the result into .github/codspeed-swept.json in place; the
caller is responsible for committing the file if it changed.
"""

from __future__ import annotations

import json
import os
import subprocess

SWEPT_PATH = ".github/codspeed-swept.json"


def main() -> None:
    """Merge this run's fully-succeeded commits into the tracking file."""
    repo = os.environ["GITHUB_REPOSITORY"]
    run_id = os.environ["GITHUB_RUN_ID"]

    # --paginate walks every page; --jq '.jobs[]' flattens each page's
    # nested `jobs` array into one job object per output line, so a sweep
    # with more than one page of jobs (a full run has 3 jobs per swept
    # commit plus plan/finalize, easily over the API's 30-per-page default)
    # doesn't silently lose jobs from later pages.
    out = subprocess.run(
        [
            "gh",
            "api",
            "--paginate",
            "--jq",
            ".jobs[]",
            f"repos/{repo}/actions/runs/{run_id}/jobs",
        ],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    jobs = [json.loads(line) for line in out.splitlines() if line]

    # Matrix job display names are "walltime <sha>" and
    # "simulation <sha> <group>" (the `name:` fields on benchmark-walltime/
    # benchmark-simulation in the workflow). A commit's simulation results
    # are sharded across several group jobs, so a sha only counts for a kind
    # once *every* job of that kind for it succeeded.
    all_ok = {"walltime": {}, "simulation": {}}
    for job in jobs:
        for kind, shas in all_ok.items():
            prefix = f"{kind} "
            if job["name"].startswith(prefix):
                sha = job["name"][len(prefix) :].split()[0]
                ok = job["conclusion"] == "success"
                shas[sha] = shas.get(sha, True) and ok

    done = {
        sha
        for sha, ok in all_ok["walltime"].items()
        if ok and all_ok["simulation"].get(sha)
    }

    existing = set(json.load(open(SWEPT_PATH))) if os.path.exists(SWEPT_PATH) else set()
    updated = sorted(existing | done)

    if updated != sorted(existing):
        with open(SWEPT_PATH, "w") as f:
            json.dump(updated, f, indent=2)
            f.write("\n")

    print(
        f"{len(done)} commit(s) fully swept this run; "
        f"tracking file now has {len(updated)} total."
    )


if __name__ == "__main__":
    main()

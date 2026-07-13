"""Local historical performance sweep over parse_string, per commit.

Runs parse_string across TPC-H/TPC-DS, in three parser modes, for every
non-skipped commit in a git range.

Usage:
    python -m utils.perf_sweep.cli \
        --repo /path/to/sqlfluff --start-ref 4.2.2 --end-ref upstream/main \
        --output bench-results

    # Cheap end-to-end sanity pass before committing to a real (hours-long) run:
    python -m utils.perf_sweep.cli --dry-run --output bench-results-dry

See README.md in this directory for the full design.
"""

from __future__ import annotations

import argparse
import datetime
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from . import dialect_cache, fixtures, gitrange, noise, perf_summary, rustbuild
from . import manifest as manifest_mod

MODES = ["python", "rust_legacy", "rust_native_ast"]
SUITES = ["tpch", "tpcds"]
BENCH_RUNNER = Path(__file__).with_name("bench_runner.py")


class _Tee:
    """Mirrors writes to several streams.

    Used to send stdout/stderr to the console and a log file at once,
    without changing any `print()` call site.
    """

    def __init__(self, *streams) -> None:
        self.streams = streams

    def write(self, data: str) -> None:
        for s in self.streams:
            s.write(data)
            s.flush()

    def flush(self) -> None:
        for s in self.streams:
            s.flush()


def parse_args(argv=None) -> argparse.Namespace:
    """Parse this sweep's CLI arguments."""
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument(
        "--repo", type=Path, default=Path("."), help="Path to the sqlfluff git repo"
    )
    p.add_argument("--start-ref", default="4.2.2", help="Inclusive start ref/tag/sha")
    p.add_argument("--end-ref", default="upstream/main", help="Inclusive end ref")
    p.add_argument(
        "--output", type=Path, default=Path("bench-results"), help="Output directory"
    )
    p.add_argument(
        "--max-commits",
        type=int,
        default=None,
        help="Max non-skipped commits to benchmark this run",
    )
    p.add_argument(
        "--time-budget-seconds",
        type=float,
        default=None,
        help="Wall-clock cap for the whole sweep",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Skip real builds/measurement; report what would happen",
    )
    p.add_argument(
        "--no-fetch",
        action="store_true",
        help="Don't fetch --end-ref's remote before resolving",
    )
    p.add_argument(
        "--taskset-cores", default=None, help="e.g. '3' to pin measurement to core 3"
    )
    p.add_argument("--nice-level", type=int, default=10)
    p.add_argument(
        "--no-power-plan",
        action="store_true",
        help="Skip the Windows power-plan switch",
    )
    return p.parse_args(argv)


def main(argv=None) -> int:
    """Run the sweep: resolve commits, then build+measure each in turn."""
    args = parse_args(argv)
    repo_dir = args.repo.resolve()
    output_dir = args.output.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Appended, not overwritten - a resumed sweep's log stays contiguous with
    # earlier invocations, same as manifest.jsonl.
    log_file = (output_dir / "sweep.log").open("a", buffering=1)
    sys.stdout = _Tee(sys.stdout, log_file)
    sys.stderr = _Tee(sys.stderr, log_file)
    print(
        f"\n----- sweep invoked {datetime.datetime.now().isoformat(timespec='seconds')} -----"
    )

    state_dir = output_dir / "_state"
    state_dir.mkdir(exist_ok=True)
    fixtures_dir = output_dir / "_fixtures" / "tpc"
    worktree_dir = output_dir / "_worktree"
    cargo_target_dir = output_dir / "_cargo-target"
    venv_tmp_base = output_dir / "_venv_tmp"
    manifest_path = output_dir / "manifest.jsonl"
    dialect_hash_file = state_dir / "dialect_hash.txt"

    if not args.no_fetch and "/" in args.end_ref:
        remote = args.end_ref.split("/")[0]
        print(f"Fetching {remote} (branch + tags) ...")
        subprocess.run(
            ["git", "-C", str(repo_dir), "fetch", remote, "--tags"], check=False
        )

    print(f"Resolving commits ({args.start_ref}..{args.end_ref}) ...")
    commits = gitrange.resolve_commits(repo_dir, args.start_ref, args.end_ref)
    n_skip = sum(1 for c in commits if c.skip)
    print(
        f"{len(commits)} commits total; {n_skip} skipped, {len(commits) - n_skip} to benchmark."
    )

    if not commits:
        print("Nothing to do.")
        return 0

    if not fixtures.ensure_fixtures(fixtures_dir):
        print(
            "ERROR: could not fetch TPC-H/TPC-DS fixtures (no network / no cache present).",
            file=sys.stderr,
        )
        return 1

    prior_manifest = manifest_mod.load_manifest(manifest_path)

    if not args.dry_run:
        rustbuild.ensure_uv()
        gitrange.ensure_worktree(repo_dir, worktree_dir, args.start_ref)
        # A prior run killed by a hard signal (SIGTERM/SIGKILL) never reaches
        # the per-commit `finally: shutil.rmtree(...)` below - Python doesn't
        # unwind finally blocks on default SIGTERM disposition. None of these
        # are a resume source of truth (manifest.jsonl is), so it's always
        # safe to start clean rather than let them accumulate across restarts.
        shutil.rmtree(venv_tmp_base, ignore_errors=True)
        venv_tmp_base.mkdir(exist_ok=True)

    with noise.PowerPlanGuard(enabled=not args.no_power_plan):
        env_reading = noise.detect_environment()
        for w in env_reading.warnings:
            print(f"WARNING (environment): {w}")

        start_time = time.monotonic()
        benchmarked_count = 0

        # start_ref is now the first entry in `commits` (an inclusive range -
        # see gitrange.resolve_commits), so it doubles as the "vs 4.2.2"
        # baseline: no separate build/measure of it. If it was already
        # benchmarked in an earlier (resumed) invocation, pick its points back
        # up from disk; otherwise it's set the moment this run measures it,
        # a few lines below.
        first_real_commit = next((c for c in commits if not c.skip), None)
        baseline_points = None
        if first_real_commit is not None:
            baseline_meta_path = output_dir / first_real_commit.sha / "meta.json"
            if baseline_meta_path.exists():
                baseline_points = perf_summary.points_from_meta(
                    json.loads(baseline_meta_path.read_text())
                )
        last_points = None

        for c in commits:
            prior_entry = prior_manifest.get(c.sha)
            if prior_entry and manifest_mod.is_done(prior_entry, args.dry_run):
                continue

            print(f"\n=== {c.sha[:10]}  {c.subject} ===")
            print(f"  time: {datetime.datetime.now().isoformat(timespec='seconds')}")
            changed_folders = _changed_folders(c.changed_files)
            if changed_folders:
                print("  changed folders:")
                for folder in changed_folders:
                    print(f"    {folder}")
            else:
                print("  changed folders: (none)")

            if c.skip:
                print(f"  SKIPPED: {c.skip_reason}")
                _write_meta(
                    output_dir, c, {"skipped": True, "skip_reason": c.skip_reason}
                )
                manifest_mod.append(
                    manifest_path,
                    {
                        "sha": c.sha,
                        "skipped": True,
                        "reason": c.skip_reason,
                        "subject": c.subject,
                        "author_date": c.author_date,
                    },
                )
                continue

            if args.max_commits is not None and benchmarked_count >= args.max_commits:
                print(f"Reached --max-commits ({args.max_commits}); stopping.")
                break
            if (
                args.time_budget_seconds is not None
                and (time.monotonic() - start_time) >= args.time_budget_seconds
            ):
                print(
                    f"Reached --time-budget-seconds ({args.time_budget_seconds}); stopping."
                )
                break

            meta = {
                "skipped": False,
                "dry_run": args.dry_run,
                "environment": env_reading.as_dict(),
                "modes": {},
            }

            if args.dry_run:
                new_hash = dialect_cache.compute_generation_hash(repo_dir, c.sha)
                previous_hash = (
                    dialect_hash_file.read_text().strip()
                    if dialect_hash_file.exists()
                    else None
                )
                would_rebuild = new_hash != previous_hash
                dialect_hash_file.write_text(new_hash)
                meta["would_rebuild_dialect_codegen"] = would_rebuild
                meta["would_run_maturin_build_release"] = True
                for mode in MODES:
                    meta["modes"][mode] = {"planned": True}
                print(
                    f"  [dry-run] would checkout, "
                    f"{'regenerate' if would_rebuild else 'reuse cached'} dialect codegen, "
                    f"then maturin build --release; would measure {len(MODES)} modes x {len(SUITES)} suites"
                )
            else:
                # A brand-new, previously non-existing directory per commit -
                # uv builds straight into it, and it's discarded once this
                # commit's measurements are done, win or lose.
                commit_venv_dir = Path(
                    tempfile.mkdtemp(dir=str(venv_tmp_base), prefix=f"{c.sha[:10]}-")
                )
                venv_python = rustbuild.venv_python_path(commit_venv_dir)
                try:
                    build_meta = rustbuild.build_commit(
                        repo_dir,
                        worktree_dir,
                        commit_venv_dir,
                        cargo_target_dir,
                        state_dir,
                        c.sha,
                    )
                    meta.update(build_meta)
                    current_points = {}
                    for mode in MODES:
                        mode_result = {}
                        current_points[mode] = {}
                        for suite in SUITES:
                            print(f"  measuring mode={mode} suite={suite} ...")
                            mode_result[suite] = _measure(
                                output_dir / c.sha,
                                venv_python,
                                fixtures_dir,
                                mode,
                                suite,
                                args.taskset_cores,
                                args.nice_level,
                            )
                            current_points[mode][suite] = perf_summary.read_point(
                                mode_result[suite]
                            )
                        meta["modes"][mode] = mode_result
                    if first_real_commit is not None and c.sha == first_real_commit.sha:
                        baseline_points = current_points
                    print(
                        perf_summary.render_summary_table(
                            MODES, SUITES, current_points, last_points, baseline_points
                        )
                    )
                    last_points = current_points
                except rustbuild.BuildError as exc:
                    # A historical commit that doesn't build is real information,
                    # not a reason to abort a multi-hour sweep. Record it and move on.
                    print(f"  BUILD FAILED: {exc}", file=sys.stderr)
                    meta["build_failed"] = True
                    meta["build_error"] = str(exc)[-4000:]
                finally:
                    shutil.rmtree(commit_venv_dir, ignore_errors=True)

            _write_meta(output_dir, c, meta)
            manifest_mod.append(
                manifest_path,
                {
                    "sha": c.sha,
                    "skipped": False,
                    "subject": c.subject,
                    "author_date": c.author_date,
                    "dry_run": args.dry_run,
                },
            )
            benchmarked_count += 1

    print("\nDone.")
    return 0


def _changed_folders(files: list) -> list:
    """Unique parent directories of a commit's changed files, sorted."""
    folders = set()
    for f in files:
        parent = str(Path(f).parent)
        folders.add("." if parent == "." else parent)
    return sorted(folders)


def _write_meta(output_dir: Path, c: gitrange.CommitInfo, extra: dict) -> None:
    commit_dir = output_dir / c.sha
    commit_dir.mkdir(exist_ok=True)
    meta = {"sha": c.sha, "subject": c.subject, "author_date": c.author_date, **extra}
    (commit_dir / "meta.json").write_text(json.dumps(meta, indent=2, default=str))


def _measure(
    commit_dir: Path,
    venv_python: Path,
    fixtures_dir: Path,
    mode: str,
    suite: str,
    cores,
    nice_level: int,
) -> dict:
    commit_dir.mkdir(exist_ok=True)
    result = {}

    callgrind_out = commit_dir / f"{mode}-{suite}-callgrind.out"
    callgrind_run_json = commit_dir / f"{mode}-{suite}-callgrind-run.json"
    cmd = noise.wrap_affinity(
        [
            "valgrind",
            "-q",
            "--tool=callgrind",
            f"--callgrind-out-file={callgrind_out}",
            "--combine-dumps=yes",
            "--dump-line=no",
            str(venv_python),
            str(BENCH_RUNNER),
            "--suite",
            suite,
            "--mode",
            mode,
            "--fixtures-dir",
            str(fixtures_dir),
            "--method",
            "callgrind",
            "--out",
            str(callgrind_run_json),
        ],
        cores,
        nice_level,
    )
    proc = subprocess.run(cmd, capture_output=True, text=True)
    result["callgrind"] = _outcome(proc, callgrind_out)

    walltime_out = commit_dir / f"{mode}-{suite}-walltime.json"
    cmd = noise.wrap_affinity(
        [
            str(venv_python),
            str(BENCH_RUNNER),
            "--suite",
            suite,
            "--mode",
            mode,
            "--fixtures-dir",
            str(fixtures_dir),
            "--method",
            "walltime",
            "--out",
            str(walltime_out),
        ],
        cores,
        nice_level,
    )
    proc = subprocess.run(cmd, capture_output=True, text=True)
    result["walltime"] = _outcome(proc, walltime_out)

    return result


def _outcome(proc: subprocess.CompletedProcess, out_path: Path) -> dict:
    from .bench_runner import NATIVE_AST_UNAVAILABLE

    if proc.returncode == NATIVE_AST_UNAVAILABLE:
        return {
            "status": "not_applicable",
            "reason": "native_ast toggle not present at this commit",
        }
    if proc.returncode != 0:
        return {
            "status": "error",
            "returncode": proc.returncode,
            "stderr": proc.stderr[-4000:],
        }
    return {"status": "ok", "output_file": str(out_path)}


if __name__ == "__main__":
    try:
        sys.exit(main())
    except rustbuild.BuildError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

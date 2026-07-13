#!/usr/bin/env python3
"""Standalone benchmark runner.

Parses a TPC-H/TPC-DS suite via Linter.parse_string, in one of three parser
modes, either once (for a valgrind callgrind wrapper to instrument) or in an
adaptive-walltime loop.

Deliberately self-contained (no import of the rest of utils/perf_sweep) and
frozen in behaviour across the sweep: it is always invoked with *this
commit's* installed sqlfluff/sqlfluffrs in the per-commit venv, so the only
thing that varies run to run is the installed package under test, never this
script's own logic.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import time
from pathlib import Path

NATIVE_AST_UNAVAILABLE = 42


def load_queries(fixtures_dir: Path, suite: str) -> list:
    """Read a suite's numbered .sql fixtures into a list, in order."""
    sub_dir, count = {"tpch": ("tpc-h", 22), "tpcds": ("tpc-ds", 99)}[suite]
    d = fixtures_dir / sub_dir
    return [(d / f"{n}.sql").read_text() for n in range(1, count + 1)]


def configure_mode(mode: str) -> None:
    """Set up the module-global native_ast toggle for this process.

    native_ast only exists from #7983 onward. For rust_native_ast on an
    older commit we exit distinctly (NATIVE_AST_UNAVAILABLE) so the caller
    records "not applicable" rather than a genuine failure. rust_legacy on
    an older commit is fine as-is: legacy is the only Rust path there.
    """
    if mode == "python":
        return
    if mode == "rust_legacy":
        try:
            from sqlfluff.core.parser import rust_parser

            rust_parser.set_native_ast(False)
        except (ImportError, AttributeError):
            pass
        return
    if mode == "rust_native_ast":
        try:
            from sqlfluff.core.parser import rust_parser

            rust_parser.set_native_ast(True)
        except (ImportError, AttributeError):
            print("NATIVE_AST_UNAVAILABLE", file=sys.stderr)
            sys.exit(NATIVE_AST_UNAVAILABLE)
        return
    raise ValueError(f"unknown mode {mode!r}")


def build_linter(mode: str):
    """Build a Linter configured for the given parser mode."""
    from sqlfluff.core import Linter
    from sqlfluff.core.config import FluffConfig

    cfg = FluffConfig(
        overrides={"dialect": "ansi", "use_rust_parser": mode != "python"},
        ignore_local_config=True,
    )
    return Linter(config=cfg)


def main() -> int:
    """Parse CLI args and run one callgrind or adaptive-walltime measurement."""
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--suite", choices=["tpch", "tpcds"], required=True)
    p.add_argument(
        "--mode", choices=["python", "rust_legacy", "rust_native_ast"], required=True
    )
    p.add_argument("--fixtures-dir", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--method", choices=["callgrind", "walltime"], required=True)
    p.add_argument("--warmup-rounds", type=int, default=2)
    p.add_argument("--floor-rounds", type=int, default=10)
    p.add_argument("--batch-rounds", type=int, default=10)
    p.add_argument("--target-rme", type=float, default=0.02)
    p.add_argument("--max-rounds", type=int, default=100)
    args = p.parse_args()

    configure_mode(args.mode)
    queries = load_queries(args.fixtures_dir, args.suite)
    linter = build_linter(args.mode)

    def run_once() -> None:
        for sql in queries:
            linter.parse_string(sql)

    if args.method == "callgrind":
        # Single deterministic run; valgrind instruments the whole process
        # from outside. No JSON stats needed beyond a marker that it ran.
        run_once()
        args.out.write_text(
            json.dumps({"mode": args.mode, "suite": args.suite, "method": "callgrind"})
        )
        return 0

    for _ in range(args.warmup_rounds):
        run_once()

    rounds = []
    rme = float("inf")
    while True:
        t0 = time.perf_counter()
        run_once()
        rounds.append(time.perf_counter() - t0)

        if len(rounds) >= args.floor_rounds and len(rounds) % args.batch_rounds == 0:
            mean = statistics.mean(rounds)
            stdev = statistics.stdev(rounds)
            sem = stdev / math.sqrt(len(rounds))
            rme = (1.96 * sem / mean) if mean > 0 else float("inf")
            if rme <= args.target_rme:
                break
        if len(rounds) >= args.max_rounds:
            break

    mean = statistics.mean(rounds)
    result = {
        "mode": args.mode,
        "suite": args.suite,
        "method": "walltime",
        "rounds_seconds": rounds,
        "warmup_rounds": args.warmup_rounds,
        "mean_seconds": mean,
        "median_seconds": statistics.median(rounds),
        "stdev_seconds": statistics.stdev(rounds) if len(rounds) > 1 else 0.0,
        "relative_margin_of_error": rme,
        "converged": rme <= args.target_rme,
    }
    args.out.write_text(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

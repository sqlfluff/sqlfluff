#!/usr/bin/env python3
"""Benchmark SQLFluff parsing with and without Rust parser using Python API.

This script runs parsing benchmarks on fixture SQL files to compare:
- Python parser performance
- Rust parser performance
- Identify queries where Rust parser has most/least impact

Usage:
    python benchmark_parsing.py --dialect tsql --limit 100
    python benchmark_parsing.py --all-dialects --limit 10
    python benchmark_parsing.py --compare  # Run both parsers
    python benchmark_parsing.py --dialect ansi --rust-only --profile  # stage breakdown

The --profile flag breaks the Rust parse down by internal stage
(rust_core/convert/apply/apply_as_tree); it requires the Rust parser
(--compare or --rust-only) and has no effect on the pure-Python parser.
"""

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Optional

from sqlfluff.core.config import FluffConfig
from sqlfluff.core.linter import Linter
from sqlfluff.core.parser.rust_parser import (
    get_parse_profile,
    reset_parse_profile,
    set_profiling,
)

# Stages reported by the Rust parser's per-stage profiler, in execution order.
_PROFILE_STAGES = ("rust_core", "convert", "apply", "apply_as_tree")


def find_sql_files(
    dialect: Optional[str] = None, limit: Optional[int] = None
) -> list[Path]:
    """Find SQL fixture files for benchmarking.

    Args:
        dialect: Specific dialect to test (e.g., 'ansi', 'tsql'). None = all dialects
        limit: Maximum number of files to test per dialect

    Returns:
        List of Path objects to SQL files
    """
    fixtures_dir = Path(__file__).parent.parent / "test" / "fixtures" / "dialects"

    if dialect:
        dialect_dir = fixtures_dir / dialect
        if not dialect_dir.exists():
            print(f"Error: Dialect '{dialect}' not found in fixtures")
            sys.exit(1)
        sql_files = sorted(dialect_dir.glob("*.sql"))
    else:
        # All dialects
        sql_files = sorted(fixtures_dir.glob("*/*.sql"))

    if limit:
        sql_files = sql_files[:limit]

    return sql_files


def parse_with_sqlfluff(
    sql_file: Path,
    use_rust: bool = False,
    iterations: int = 10,
    warmup: int = 2,
    profile: bool = False,
) -> dict:
    """Parse a SQL file using sqlfluff and measure timing.

    Args:
        sql_file: Path to SQL file
        use_rust: Whether to use Rust parser
        iterations: Number of timed iterations for stable timing
        warmup: Number of warmup iterations (not timed)
        profile: Collect the Rust parser's per-stage breakdown (Rust only)

    Returns:
        Dict with timing info and status
    """
    # Detect dialect from path
    dialect = sql_file.parent.name

    # Read SQL file
    try:
        sql_content = sql_file.read_text(encoding="utf-8")
    except Exception as e:
        return {
            "file": str(sql_file.relative_to(Path(__file__).parent.parent)),
            "dialect": dialect,
            "success": False,
            "error": f"Failed to read file: {e}",
            "lexing_times": [],
            "parsing_times": [],
            "mean_lexing_time": 0,
            "mean_parsing_time": 0,
            "iterations": 0,
        }

    # Configure linter with Rust parser option
    config = FluffConfig(
        overrides={
            "dialect": dialect,
            "use_rust_parser": use_rust,
        }
    )
    linter = Linter(config=config)

    lexing_times = []
    parsing_times = []
    stage_times: dict[str, list[float]] = {stage: [] for stage in _PROFILE_STAGES}
    success = True
    error_msg = None

    # Warmup iterations (not timed)
    for _ in range(warmup):
        try:
            linter.parse_string(sql_content, fname=str(sql_file))
        except Exception:
            # Ignore warmup errors, will be caught in timed iterations
            pass

    # Timed iterations
    for _ in range(iterations):
        try:
            # Reset so the profile is scoped to this parse (summed across any
            # rendered variants), matching this iteration's parse time.
            if profile and use_rust:
                reset_parse_profile()
            result = linter.parse_string(sql_content, fname=str(sql_file))

            # Extract timing from result.time_dict
            # time_dict contains: "templating", "lexing", "parsing"
            lexing_time = result.time_dict.get("lexing", 0)
            parsing_time = result.time_dict.get("parsing", 0)
            lexing_times.append(lexing_time)
            parsing_times.append(parsing_time)

            # Pull the per-stage breakdown of the parse we just timed.
            # Record every stage on every timed iteration (0.0 when a stage is
            # absent) so each stage's samples share the same denominator as
            # parsing_times. Appending only present stages would average a
            # sometimes-missing stage over fewer iterations, biasing its mean
            # upward relative to the per-iteration parse time it is compared to.
            if profile and use_rust:
                stage_profile = get_parse_profile()
                for stage in _PROFILE_STAGES:
                    stage_times[stage].append(stage_profile.get(stage, 0.0))

            # Check for parse violations
            if not result.parsed_variants or not result.parsed_variants[0].tree:
                success = False
                error_msg = "Parse returned None"
            elif result.violations:
                # Has parse violations but still succeeded
                pass
        except Exception as e:
            success = False
            error_msg = str(e)[:200]
            break

    if not lexing_times:
        lexing_times = [0]
    if not parsing_times:
        parsing_times = [0]

    result_dict = {
        "file": str(sql_file.relative_to(Path(__file__).parent.parent)),
        "dialect": dialect,
        "success": success,
        "error": error_msg,
        "lexing_times": lexing_times,
        "parsing_times": parsing_times,
        "mean_lexing_time": statistics.mean(lexing_times),
        "mean_parsing_time": statistics.mean(parsing_times),
        "mean_total_time": statistics.mean(
            [lex + parse for lex, parse in zip(lexing_times, parsing_times)]
        ),
        "iterations": len(lexing_times),
    }

    # Mean per-stage parse timings (Rust only, when profiling is requested).
    if profile and use_rust:
        result_dict["stage_profile"] = {
            stage: (statistics.mean(times) if times else 0.0)
            for stage, times in stage_times.items()
        }

    return result_dict


def benchmark_files(
    sql_files: list[Path],
    use_rust: bool = False,
    iterations: int = 10,
    warmup: int = 2,
    profile: bool = False,
) -> list[dict]:
    """Benchmark a list of SQL files.

    Args:
        sql_files: List of SQL files to benchmark
        use_rust: Whether to use Rust parser
        iterations: Number of timed iterations per file
        warmup: Number of warmup iterations per file
        profile: Collect the Rust parser's per-stage breakdown (Rust only)

    Returns:
        List of benchmark results
    """
    results = []
    parser_name = "Rust" if use_rust else "Python"

    print(f"\nBenchmarking {len(sql_files)} files with {parser_name} parser...")
    print(f"Iterations per file: {iterations}")

    for i, sql_file in enumerate(sql_files, 1):
        if i % 10 == 0 or i == len(sql_files):
            print(f"  Progress: {i}/{len(sql_files)} ({i * 100 // len(sql_files)}%)")

        result = parse_with_sqlfluff(sql_file, use_rust, iterations, warmup, profile)
        results.append(result)

    return results


def compare_results(python_results: list[dict], rust_results: list[dict]) -> None:
    """Compare Python and Rust parser results and show statistics.

    Args:
        python_results: Benchmark results from Python parser
        rust_results: Benchmark results from Rust parser
    """
    print("\n" + "=" * 80)
    print("COMPARISON: Python vs Rust Parser")
    print("=" * 80)

    # Overall statistics (convert totals to milliseconds for display)
    py_lex_times_s = [r["mean_lexing_time"] for r in python_results if r["success"]]
    rust_lex_times_s = [r["mean_lexing_time"] for r in rust_results if r["success"]]
    py_parse_times_s = [r["mean_parsing_time"] for r in python_results if r["success"]]
    rust_parse_times_s = [r["mean_parsing_time"] for r in rust_results if r["success"]]

    py_lex_total_s = sum(py_lex_times_s)
    rust_lex_total_s = sum(rust_lex_times_s)
    py_parse_total_s = sum(py_parse_times_s)
    rust_parse_total_s = sum(rust_parse_times_s)

    lex_speedup = (
        (py_lex_total_s - rust_lex_total_s) / py_lex_total_s * 100
        if py_lex_total_s > 0
        else 0
    )
    parse_speedup = (
        (py_parse_total_s - rust_parse_total_s) / py_parse_total_s * 100
        if py_parse_total_s > 0
        else 0
    )

    # Convert to milliseconds for human-friendly display
    py_lex_total = py_lex_total_s * 1000
    rust_lex_total = rust_lex_total_s * 1000
    py_parse_total = py_parse_total_s * 1000
    rust_parse_total = rust_parse_total_s * 1000

    print("\nOverall Performance:")
    print("  Lexing:")
    print(f"    Python total: {py_lex_total:.3f}ms")
    print(f"    Rust total:   {rust_lex_total:.3f}ms")
    print(f"    Speedup:      {lex_speedup:+.1f}%")
    print("  Parsing:")
    print(f"    Python total: {py_parse_total:.3f}ms")
    print(f"    Rust total:   {rust_parse_total:.3f}ms")
    print(f"    Speedup:      {parse_speedup:+.1f}%")
    print(f"  Files tested: {len(py_lex_times_s)}")

    # Success rates
    py_success = sum(1 for r in python_results if r["success"])
    rust_success = sum(1 for r in rust_results if r["success"])

    print("\nSuccess Rates:")
    print(
        f"  Python: {py_success}/{len(python_results)}"
        f" ({py_success * 100 // len(python_results)}%)"
    )
    print(
        f"  Rust:   {rust_success}/{len(rust_results)}"
        f" ({rust_success * 100 // len(rust_results)}%)"
    )

    # Per-file comparison
    comparisons = []
    for py_r, rust_r in zip(python_results, rust_results):
        if py_r["success"] and rust_r["success"]:
            # Convert per-file times to milliseconds for diffs/display
            py_lex_ms = py_r["mean_lexing_time"] * 1000
            rust_lex_ms = rust_r["mean_lexing_time"] * 1000
            py_parse_ms = py_r["mean_parsing_time"] * 1000
            rust_parse_ms = rust_r["mean_parsing_time"] * 1000

            lex_diff_ms = rust_lex_ms - py_lex_ms
            lex_speedup_pct = (
                (py_r["mean_lexing_time"] - rust_r["mean_lexing_time"])
                / py_r["mean_lexing_time"]
                * 100
                if py_r["mean_lexing_time"] > 0
                else 0
            )
            parse_diff_ms = rust_parse_ms - py_parse_ms
            parse_speedup_pct = (
                (py_r["mean_parsing_time"] - rust_r["mean_parsing_time"])
                / py_r["mean_parsing_time"]
                * 100
                if py_r["mean_parsing_time"] > 0
                else 0
            )

            comparisons.append(
                {
                    "file": py_r["file"],
                    "dialect": py_r["dialect"],
                    "python_lex_time": py_lex_ms,
                    "rust_lex_time": rust_lex_ms,
                    "python_parse_time": py_parse_ms,
                    "rust_parse_time": rust_parse_ms,
                    "lex_diff_ms": lex_diff_ms,
                    "lex_speedup_pct": lex_speedup_pct,
                    "parse_diff_ms": parse_diff_ms,
                    "parse_speedup_pct": parse_speedup_pct,
                }
            )

    # Sort by absolute time difference for true slowdowns
    # Filter out tiny files where FFI overhead dominates (< 5ms Python parse time)
    MIN_PARSE_TIME_MS = 5.0
    significant_comparisons = [
        c for c in comparisons if c["python_parse_time"] >= MIN_PARSE_TIME_MS
    ]

    comparisons_by_diff = sorted(
        significant_comparisons, key=lambda x: x["parse_diff_ms"], reverse=True
    )

    print(f"\n{'=' * 80}")
    print("TOP 10 SLOWEST PARSING QUERIES (Largest Absolute Slowdown in ms)")
    print(f"Filtered: Only queries with Python parse time >= {MIN_PARSE_TIME_MS}ms")
    print("(Excludes trivial queries where FFI overhead dominates)")
    print(f"{'=' * 80}")
    print(
        f"{'File':<50} {'Python (ms)':<12} {'Rust (ms)':<12} {'Diff (ms)':<12} {'%':<8}"
    )
    print("-" * 80)

    # Show top 10 with largest absolute slowdown (positive parse_diff_ms)
    for comp in comparisons_by_diff[: min(10, len(comparisons_by_diff))]:
        print(
            f"{comp['file'][-47:]:<50} "
            f"{comp['python_parse_time']:>10.1f}ms "
            f"{comp['rust_parse_time']:>10.1f}ms "
            f"{comp['parse_diff_ms']:>+10.1f}ms "
            f"{comp['parse_speedup_pct']:>+6.1f}%"
        )

    print(f"\n{'=' * 80}")
    print("TOP 10 FASTEST PARSING QUERIES (Largest Absolute Speedup in ms)")
    print(f"Filtered: Only queries with Python parse time >= {MIN_PARSE_TIME_MS}ms")
    print(f"{'=' * 80}")
    print(
        f"{'File':<50} {'Python (ms)':<12} {'Rust (ms)':<12} {'Diff (ms)':<12} {'%':<8}"
    )
    print("-" * 80)

    # Show top 10 with largest absolute speedup (negative parse_diff_ms)
    for comp in comparisons_by_diff[-min(10, len(comparisons_by_diff)) :]:
        print(
            f"{comp['file'][-47:]:<50} "
            f"{comp['python_parse_time']:>10.1f}ms "
            f"{comp['rust_parse_time']:>10.1f}ms "
            f"{comp['parse_diff_ms']:>+10.1f}ms "
            f"{comp['parse_speedup_pct']:>+6.1f}%"
        )

    # Dialect breakdown
    print(f"\n{'=' * 80}")
    print("PARSE PERFORMANCE BY DIALECT")
    print(f"{'=' * 80}")
    print(
        f"{'Dialect':<15} {'Count':<8} {'Python (ms)':<15}"
        f" {'Rust (ms)':<15} {'Speedup':<10}"
    )
    print("-" * 80)

    dialect_stats = {}
    for comp in comparisons:
        dialect = comp["dialect"]
        if dialect not in dialect_stats:
            dialect_stats[dialect] = []
        dialect_stats[dialect].append(comp)

    for dialect in sorted(dialect_stats.keys()):
        comps = dialect_stats[dialect]
        avg_py = statistics.mean([c["python_parse_time"] for c in comps])
        avg_rust = statistics.mean([c["rust_parse_time"] for c in comps])
        avg_speedup = statistics.mean([c["parse_speedup_pct"] for c in comps])

        print(
            f"{dialect:<15} "
            f"{len(comps):<8} "
            f"{avg_py:>12.1f}ms "
            f"{avg_rust:>12.1f}ms "
            f"{avg_speedup:>+8.1f}%"
        )

    # FFI overhead analysis
    print(f"\n{'=' * 80}")
    print("FFI OVERHEAD ANALYSIS")
    print(f"{'=' * 80}")

    # Categorize files by Python parse time (actual complexity)
    tiny_files = [c for c in comparisons if c["python_parse_time"] < 5]
    small_files = [c for c in comparisons if 5 <= c["python_parse_time"] < 20]
    medium_files = [c for c in comparisons if 20 <= c["python_parse_time"] < 100]
    large_files = [c for c in comparisons if c["python_parse_time"] >= 100]

    # Compute stats outside f-strings for clarity and to avoid line length issues
    tiny_count = len(tiny_files)
    tiny_diff = (
        statistics.mean([c["parse_diff_ms"] for c in tiny_files]) if tiny_files else 0
    )
    tiny_pct = (
        statistics.mean([c["parse_speedup_pct"] for c in tiny_files])
        if tiny_files
        else 0
    )

    small_count = len(small_files)
    small_diff = (
        statistics.mean([c["parse_diff_ms"] for c in small_files]) if small_files else 0
    )
    small_pct = (
        statistics.mean([c["parse_speedup_pct"] for c in small_files])
        if small_files
        else 0
    )

    medium_count = len(medium_files)
    medium_diff = (
        statistics.mean([c["parse_diff_ms"] for c in medium_files])
        if medium_files
        else 0
    )
    medium_pct = (
        statistics.mean([c["parse_speedup_pct"] for c in medium_files])
        if medium_files
        else 0
    )

    large_count = len(large_files)
    large_diff = (
        statistics.mean([c["parse_diff_ms"] for c in large_files]) if large_files else 0
    )
    large_pct = (
        statistics.mean([c["parse_speedup_pct"] for c in large_files])
        if large_files
        else 0
    )

    print(
        f"Tiny files (<5ms):          {tiny_count:>4} files,"
        f" avg Rust diff:     {tiny_diff:+6.2f}ms ({tiny_pct:+5.1f}%)"
    )
    print(
        f"Small files (5-20ms):       {small_count:>4} files,"
        f" avg Rust diff:     {small_diff:+6.2f}ms ({small_pct:+5.1f}%)"
    )
    print(
        f"Medium files (20-100ms):    {medium_count:>4} files,"
        f" avg Rust speedup:  {medium_diff:+6.2f}ms ({medium_pct:+5.1f}%)"
    )
    print(
        f"Large files (>100ms):       {large_count:>4} files,"
        f" avg Rust speedup:  {large_diff:+6.2f}ms ({large_pct:+5.1f}%)"
    )
    if tiny_files:
        print(
            f"\nNote: {len(tiny_files)} tiny files (<5ms) may show FFI overhead "
            "dominating."
        )
        print("For real-world usage, focus on small/medium/large file performance.")


def save_results(results: dict, output_file: Path) -> None:
    """Save benchmark results to JSON file.

    Args:
        results: Benchmark results dictionary
        output_file: Path to output JSON file
    """
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_file}")


def _print_stage_table(label: str, results: list[dict]) -> None:
    """Print a per-stage breakdown for a set of profiled Rust results."""
    profiled = [
        r for r in results if r.get("success") and r.get("stage_profile") is not None
    ]
    if not profiled:
        print(f"  {label}: no profiled results")
        return

    # Sum each stage across the files in this group (convert to ms).
    stage_totals = {
        stage: sum(r["stage_profile"].get(stage, 0.0) for r in profiled) * 1000
        for stage in _PROFILE_STAGES
    }
    grand_total = sum(stage_totals.values())
    parse_total = sum(r["mean_parsing_time"] for r in profiled) * 1000

    print(f"\n  {label} ({len(profiled)} files)")
    print(f"  {'stage':<16}{'total (ms)':>14}{'% of stages':>14}")
    print(f"  {'-' * 44}")
    for stage in _PROFILE_STAGES:
        total = stage_totals[stage]
        pct = (total / grand_total * 100) if grand_total else 0.0
        print(f"  {stage:<16}{total:>14.3f}{pct:>13.1f}%")
    print(f"  {'-' * 44}")
    print(f"  {'stages sum':<16}{grand_total:>14.3f}")
    # Sanity check: the four stages should account for ~all of parse() time.
    print(f"  {'parse() total':<16}{parse_total:>14.3f}  (timed externally)")


def print_profile_summary(rust_results: list[dict]) -> None:
    """Show where time goes inside the Rust parser, overall and by file size."""
    print("\n" + "=" * 80)
    print("RUST PARSER PER-STAGE PROFILE")
    print("=" * 80)
    print(
        "Stages: rust_core (Rust parse) | convert (Python MatchResult rebuild) |\n"
        "        apply (build BaseSegment tree) | apply_as_tree (build _rs_tree)"
    )

    ok = [r for r in rust_results if r.get("success") and r.get("stage_profile")]
    if not ok:
        print("\nNo profiled results to report.")
        return

    _print_stage_table("OVERALL", ok)

    # Bucket by parse complexity (terciles of mean parse time) so we can see how
    # the boundary cost scales with file size.
    by_parse = sorted(ok, key=lambda r: r["mean_parsing_time"])
    n = len(by_parse)
    if n >= 3:
        third = n // 3
        buckets = [
            ("SMALL files (fastest third)", by_parse[:third]),
            ("MEDIUM files (middle third)", by_parse[third : 2 * third]),
            ("LARGE files (slowest third)", by_parse[2 * third :]),
        ]
        for label, group in buckets:
            _print_stage_table(label, group)


def main():
    """Main benchmark runner."""
    parser = argparse.ArgumentParser(
        description="Benchmark SQLFluff parsing performance"
    )
    parser.add_argument(
        "--dialect",
        help="Specific dialect to test (e.g., tsql, bigquery)",
    )
    parser.add_argument(
        "--all-dialects",
        action="store_true",
        help="Test all dialects",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of files to test",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=10,
        help="Number of timed iterations per file (default: 10)",
    )
    parser.add_argument(
        "--warmup",
        type=int,
        default=2,
        help="Number of warmup iterations per file (default: 2)",
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare Python and Rust parsers",
    )
    parser.add_argument(
        "--rust-only",
        action="store_true",
        help="Only benchmark Rust parser",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Save results to JSON file",
    )
    parser.add_argument(
        "--profile",
        action="store_true",
        help="Break down Rust parse time by internal stage "
        "(rust_core/convert/apply/apply_as_tree)",
    )

    args = parser.parse_args()

    # Enable the Rust parser's per-stage profiler if requested.
    if args.profile:
        set_profiling(True)

    # Find files
    if args.all_dialects:
        sql_files = find_sql_files(limit=args.limit)
    elif args.dialect:
        sql_files = find_sql_files(args.dialect, args.limit)
    else:
        print("Error: Specify --dialect <name> or --all-dialects")
        sys.exit(1)

    print(f"Found {len(sql_files)} SQL files to benchmark")

    # Run benchmarks
    if args.compare:
        # Test both parsers
        python_results = benchmark_files(
            sql_files, use_rust=False, iterations=args.iterations, warmup=args.warmup
        )
        rust_results = benchmark_files(
            sql_files,
            use_rust=True,
            iterations=args.iterations,
            warmup=args.warmup,
            profile=args.profile,
        )

        compare_results(python_results, rust_results)
        if args.profile:
            print_profile_summary(rust_results)

        if args.output:
            save_results(
                {
                    "python": python_results,
                    "rust": rust_results,
                },
                args.output,
            )
    elif args.rust_only:
        # Rust parser only
        results = benchmark_files(
            sql_files,
            use_rust=True,
            iterations=args.iterations,
            warmup=args.warmup,
            profile=args.profile,
        )

        if args.profile:
            print_profile_summary(results)

        if args.output:
            save_results({"rust": results}, args.output)
    else:
        # Python parser only (default)
        results = benchmark_files(
            sql_files, use_rust=False, iterations=args.iterations, warmup=args.warmup
        )

        if args.output:
            save_results({"python": results}, args.output)


if __name__ == "__main__":
    main()

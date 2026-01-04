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
"""

import argparse
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Optional

from sqlfluff.core.config import FluffConfig
from sqlfluff.core.linter import Linter


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
    sql_file: Path, use_rust: bool = False, iterations: int = 3
) -> dict:
    """Parse a SQL file using sqlfluff and measure timing.

    Args:
        sql_file: Path to SQL file
        use_rust: Whether to use Rust parser
        iterations: Number of iterations for stable timing

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
            "mean_time": 0,
            "min_time": 0,
            "max_time": 0,
            "stdev": 0,
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

    times = []
    success = True
    error_msg = None

    for _ in range(iterations):
        start = time.perf_counter()
        try:
            result = linter.parse_string(sql_content, fname=str(sql_file))
            elapsed = time.perf_counter() - start
            times.append(elapsed)

            # Check for parse violations
            if result.tree is None:
                success = False
                error_msg = "Parse returned None"
            elif result.violations:
                # Has parse violations but still succeeded
                pass
        except Exception as e:
            elapsed = time.perf_counter() - start
            times.append(elapsed)
            success = False
            error_msg = str(e)[:200]
            break

    if not times:
        times = [float("inf")]

    return {
        "file": str(sql_file.relative_to(Path(__file__).parent.parent)),
        "dialect": dialect,
        "success": success,
        "error": error_msg,
        "mean_time": statistics.mean(times),
        "min_time": min(times),
        "max_time": max(times),
        "stdev": statistics.stdev(times) if len(times) > 1 else 0,
        "iterations": len(times),
    }


def benchmark_files(
    sql_files: list[Path],
    use_rust: bool = False,
    iterations: int = 3,
) -> list[dict]:
    """Benchmark a list of SQL files.

    Args:
        sql_files: List of SQL files to benchmark
        use_rust: Whether to use Rust parser
        iterations: Number of iterations per file

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

        result = parse_with_sqlfluff(sql_file, use_rust, iterations)
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

    # Overall statistics
    py_times = [r["mean_time"] for r in python_results if r["success"]]
    rust_times = [r["mean_time"] for r in rust_results if r["success"]]

    py_total = sum(py_times)
    rust_total = sum(rust_times)
    speedup = (py_total - rust_total) / py_total * 100 if py_total > 0 else 0

    print("\nOverall Performance:")
    print(f"  Python total: {py_total:.3f}s")
    print(f"  Rust total:   {rust_total:.3f}s")
    print(f"  Speedup:      {speedup:+.1f}%")
    print(f"  Files tested: {len(py_times)}")

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
            speedup_pct = (
                (py_r["mean_time"] - rust_r["mean_time"]) / py_r["mean_time"] * 100
            )
            comparisons.append(
                {
                    "file": py_r["file"],
                    "dialect": py_r["dialect"],
                    "python_time": py_r["mean_time"],
                    "rust_time": rust_r["mean_time"],
                    "speedup_pct": speedup_pct,
                }
            )

    # Sort by speedup
    comparisons.sort(key=lambda x: x["speedup_pct"])

    print(f"\n{'=' * 80}")
    print("TOP 10 SLOWEST QUERIES (Least Speedup / Potential Regressions)")
    print(f"{'=' * 80}")
    print(f"{'File':<50} {'Python':<10} {'Rust':<10} {'Speedup':<10}")
    print("-" * 80)

    # Show slowest 10 (least speedup, possibly regressions)
    for comp in comparisons[: min(10, len(comparisons))]:
        print(
            f"{comp['file'][-47:]:<50} "
            f"{comp['python_time'] * 1000:>8.1f}ms "
            f"{comp['rust_time'] * 1000:>8.1f}ms "
            f"{comp['speedup_pct']:>+8.1f}%"
        )

    print(f"\n{'=' * 80}")
    print("TOP 10 FASTEST QUERIES (Best Speedup)")
    print(f"{'=' * 80}")
    print(f"{'File':<50} {'Python':<10} {'Rust':<10} {'Speedup':<10}")
    print("-" * 80)

    # Show fastest 10 (most speedup)
    for comp in comparisons[-min(10, len(comparisons)) :]:
        print(
            f"{comp['file'][-47:]:<50} "
            f"{comp['python_time'] * 1000:>8.1f}ms "
            f"{comp['rust_time'] * 1000:>8.1f}ms "
            f"{comp['speedup_pct']:>+8.1f}%"
        )

    # Dialect breakdown
    print(f"\n{'=' * 80}")
    print("PERFORMANCE BY DIALECT")
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
        avg_py = statistics.mean([c["python_time"] for c in comps])
        avg_rust = statistics.mean([c["rust_time"] for c in comps])
        avg_speedup = statistics.mean([c["speedup_pct"] for c in comps])

        print(
            f"{dialect:<15} "
            f"{len(comps):<8} "
            f"{avg_py * 1000:>12.1f}ms "
            f"{avg_rust * 1000:>12.1f}ms "
            f"{avg_speedup:>+8.1f}%"
        )


def save_results(results: dict, output_file: Path) -> None:
    """Save benchmark results to JSON file.

    Args:
        results: Benchmark results dictionary
        output_file: Path to output JSON file
    """
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_file}")


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
        default=3,
        help="Number of iterations per file (default: 3)",
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

    args = parser.parse_args()

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
            sql_files, use_rust=False, iterations=args.iterations
        )
        rust_results = benchmark_files(
            sql_files, use_rust=True, iterations=args.iterations
        )

        compare_results(python_results, rust_results)

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
        results = benchmark_files(sql_files, use_rust=True, iterations=args.iterations)

        if args.output:
            save_results({"rust": results}, args.output)
    else:
        # Python parser only (default)
        results = benchmark_files(sql_files, use_rust=False, iterations=args.iterations)

        if args.output:
            save_results({"python": results}, args.output)


if __name__ == "__main__":
    main()

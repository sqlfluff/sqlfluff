#!/usr/bin/env python3
"""Benchmark Python and Rust lexer/parser without Linter overhead."""

import argparse
import sys
import time
from pathlib import Path
from typing import Optional

import sqlfluffrs
from sqlfluff.core import FluffConfig
from sqlfluff.core.dialects import dialect_selector
from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.lexer import PyLexer


def benchmark_python_lexer(sql: str, config: FluffConfig, runs: int = 50) -> dict:
    """Benchmark Python lexer."""
    lexer = PyLexer(config=config)

    # Warm up
    for _ in range(3):
        _, _ = lexer.lex(sql)

    # Benchmark
    times = []
    for _ in range(runs):
        start = time.perf_counter()
        tokens, _ = lexer.lex(sql)
        _ = list(tokens)
        elapsed = time.perf_counter() - start
        times.append(elapsed * 1000)

    return {
        "min": min(times),
        "avg": sum(times) / len(times),
        "max": max(times),
        "median": sorted(times)[len(times) // 2],
    }


def benchmark_rust_lexer(sql: str, dialect: str, runs: int = 50) -> dict:
    """Benchmark Rust lexer."""
    lexer = sqlfluffrs.RsLexer(dialect=dialect)

    # Warm up
    for _ in range(3):
        _, _ = lexer._lex(sql)

    # Benchmark
    times = []
    for _ in range(runs):
        start = time.perf_counter()
        tokens, _ = lexer._lex(sql)
        _ = list(tokens)
        elapsed = time.perf_counter() - start
        times.append(elapsed * 1000)

    return {
        "min": min(times),
        "avg": sum(times) / len(times),
        "max": max(times),
        "median": sorted(times)[len(times) // 2],
    }


def benchmark_python_parser(sql: str, config: FluffConfig, runs: int = 50) -> dict:
    """Benchmark Python parser (lex + parse)."""
    dialect = dialect_selector(config.get("dialect"))
    lexer = PyLexer(config=config)
    root_segment = dialect.get_root_segment()

    # Warm up
    for _ in range(3):
        tokens, _ = lexer.lex(sql)
        token_list = tuple(tokens)
        parse_context = ParseContext(dialect=dialect)
        _ = root_segment.root_parse(token_list, parse_context)

    # Benchmark
    times = []
    for _ in range(runs):
        start = time.perf_counter()
        tokens, _ = lexer.lex(sql)
        token_list = tuple(tokens)
        parse_context = ParseContext(dialect=dialect)
        _ = root_segment.root_parse(token_list, parse_context)
        elapsed = time.perf_counter() - start
        times.append(elapsed * 1000)

    return {
        "min": min(times),
        "avg": sum(times) / len(times),
        "max": max(times),
        "median": sorted(times)[len(times) // 2],
    }


def benchmark_rust_parser(sql: str, dialect: str, runs: int = 50) -> dict:
    """Benchmark Rust parser (lex + parse)."""
    lexer = sqlfluffrs.RsLexer(dialect=dialect)
    parser = sqlfluffrs.RsParser(dialect)

    # Warm up
    for _ in range(3):
        tokens, _ = lexer._lex(sql)
        _, _ = parser.parse_match_result_with_stats(list(tokens))

    # Benchmark
    times = []
    stats = None
    for _ in range(runs):
        start = time.perf_counter()
        tokens, _ = lexer._lex(sql)
        result, stats = parser.parse_match_result_with_stats(list(tokens))
        elapsed = time.perf_counter() - start
        times.append(elapsed * 1000)

    return {
        "min": min(times),
        "avg": sum(times) / len(times),
        "max": max(times),
        "median": sorted(times)[len(times) // 2],
        "stats": stats,
    }


def print_results(name: str, results: dict, baseline: Optional[dict] = None):
    """Print benchmark results."""
    print(f"\n{name}:")
    print(f"  Min:    {results['min']:8.2f}ms")
    print(f"  Avg:    {results['avg']:8.2f}ms")
    print(f"  Median: {results['median']:8.2f}ms")
    print(f"  Max:    {results['max']:8.2f}ms")

    if baseline:
        speedup = baseline["avg"] / results["avg"]
        if speedup > 1:
            print(
                f"  Speedup: {speedup:6.2f}x faster than {baseline.get('name', 'baseline')}"
            )
        else:
            print(
                f"  Speedup: {1 / speedup:6.2f}x slower than {baseline.get('name', 'baseline')}"
            )


def print_stats(stats: dict):
    """Print Rust parser statistics."""
    print("\nRust Parser Statistics:")
    for key in [
        "cache_hits",
        "cache_misses",
        "cache_entries",
        "pruning_calls",
        "pruning_kept",
        "pruning_total",
    ]:
        if key in stats:
            print(f"  {key:20s}: {stats[key]:,}")

    # Derived metrics
    cache_total = stats.get("cache_hits", 0) + stats.get("cache_misses", 0)
    if cache_total > 0:
        hit_rate = stats.get("cache_hits", 0) / cache_total * 100
        print(f"  {'cache_hit_rate':20s}: {hit_rate:.1f}%")

    pruning_total = stats.get("pruning_total", 0)
    pruning_kept = stats.get("pruning_kept", 0)
    if pruning_total > 0:
        kept_rate = pruning_kept / pruning_total * 100
        print(f"  {'pruning_kept_rate':20s}: {kept_rate:.1f}%")


def main():
    """Run benchmarks."""
    parser = argparse.ArgumentParser(
        description="Benchmark SQLFluff lexer/parser without Linter overhead"
    )
    parser.add_argument("file", help="SQL file to benchmark")
    parser.add_argument("-d", "--dialect", default="ansi", help="SQL dialect")
    parser.add_argument("-r", "--runs", type=int, default=50, help="Number of runs")
    parser.add_argument(
        "--lexer-only", action="store_true", help="Benchmark lexer only"
    )
    parser.add_argument(
        "--parser-only", action="store_true", help="Benchmark parser only"
    )
    parser.add_argument(
        "--python-only", action="store_true", help="Benchmark Python only"
    )
    parser.add_argument("--rust-only", action="store_true", help="Benchmark Rust only")
    parser.add_argument("--stats", action="store_true", help="Show detailed stats")

    args = parser.parse_args()

    # Read SQL file
    sql_path = Path(args.file)
    if not sql_path.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    sql = sql_path.read_text()
    config = FluffConfig(overrides={"dialect": args.dialect})

    print("=" * 80)
    print(f"BENCHMARK: {sql_path.name}")
    print("=" * 80)
    print(f"File:    {args.file}")
    print(f"Size:    {len(sql)} chars")
    print(f"Dialect: {args.dialect}")
    print(f"Runs:    {args.runs}")
    print("=" * 80)

    # Lexer benchmarks
    if not args.parser_only:
        print("\n" + "=" * 80)
        print("LEXER BENCHMARKS")
        print("=" * 80)

        if not args.rust_only:
            py_lex = benchmark_python_lexer(sql, config, args.runs)
            py_lex["name"] = "Python"
            print_results("Python Lexer", py_lex)

        if not args.python_only:
            rs_lex = benchmark_rust_lexer(sql, args.dialect, args.runs)
            rs_lex["name"] = "Rust"
            baseline = py_lex if not args.rust_only else None
            print_results("Rust Lexer", rs_lex, baseline)

    # Parser benchmarks (lex + parse)
    if not args.lexer_only:
        print("\n" + "=" * 80)
        print("PARSER BENCHMARKS (lex + parse)")
        print("=" * 80)

        if not args.rust_only:
            py_parse = benchmark_python_parser(sql, config, args.runs)
            py_parse["name"] = "Python"
            print_results("Python Parser", py_parse)

        if not args.python_only:
            rs_parse = benchmark_rust_parser(sql, args.dialect, args.runs)
            rs_parse["name"] = "Rust"
            baseline = py_parse if not args.rust_only else None
            print_results("Rust Parser", rs_parse, baseline)

            if args.stats and "stats" in rs_parse:
                print_stats(rs_parse["stats"])

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    if not args.lexer_only and not args.rust_only and not args.python_only:
        py_total = py_parse["avg"]
        rs_total = rs_parse["avg"]
        speedup = py_total / rs_total

        print(f"\nTotal time (lex + parse):")
        print(f"  Python: {py_total:8.2f}ms")
        print(f"  Rust:   {rs_total:8.2f}ms")

        if speedup > 1:
            print(f"\n✓ Rust is {speedup:.2f}x FASTER")
        else:
            print(f"\n✗ Rust is {1 / speedup:.2f}x SLOWER")

    print()


if __name__ == "__main__":
    main()

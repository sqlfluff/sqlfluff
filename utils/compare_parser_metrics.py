#!/usr/bin/env python3
"""Compare Python and Rust parser metrics to verify optimization parity."""

import argparse
import time
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ParserMetrics:
    """Container for parser metrics."""

    name: str
    parse_time_ms: float = 0.0
    token_count: int = 0

    # Cache metrics
    cache_hits: int = 0
    cache_misses: int = 0
    cache_entries: int = 0

    # Pruning metrics
    pruning_calls: int = 0
    pruning_total_options: int = 0
    pruning_kept_options: int = 0
    pruning_hinted: int = 0
    pruning_complex: int = 0

    # Match attempt metrics
    match_attempts: int = 0
    match_successes: int = 0

    # Terminator metrics
    terminator_hits: int = 0
    terminator_checks: int = 0

    # Depth metrics
    max_parse_depth: int = 0
    max_match_depth: int = 0

    @property
    def cache_hit_rate(self) -> float:
        """Return cache hit rate as float 0-1."""
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0

    @property
    def pruning_rate(self) -> float:
        """Return pruning rate (% of options dropped)."""
        if self.pruning_total_options == 0:
            return 0.0
        return 1.0 - (self.pruning_kept_options / self.pruning_total_options)

    @property
    def match_success_rate(self) -> float:
        """Return match success rate."""
        if self.match_attempts == 0:
            return 0.0
        return self.match_successes / self.match_attempts

    @property
    def terminator_hit_rate(self) -> float:
        """Return terminator hit rate."""
        if self.terminator_checks == 0:
            return 0.0
        return self.terminator_hits / self.terminator_checks

    @property
    def ms_per_token(self) -> float:
        """Return parse time per token in ms."""
        return self.parse_time_ms / self.token_count if self.token_count > 0 else 0.0


# Global metrics storage for Python instrumentation
class PythonMetricsCollector:
    """Collects metrics from Python parser via instrumentation."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        """Reset all metrics."""
        self.pruning_calls = 0
        self.pruning_total = 0
        self.pruning_kept = 0
        self.pruning_hinted = 0
        self.pruning_complex = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.cache_entries = 0
        self.match_attempts = 0
        self.match_successes = 0
        self.terminator_hits = 0
        self.terminator_checks = 0
        self.max_parse_depth = 0
        self.max_match_depth = 0
        self.current_match_depth = 0  # Track current recursion depth


_collector = PythonMetricsCollector()


def instrument_python_parser() -> None:
    """Instrument Python parser to collect metrics."""
    # Import here to avoid circular imports
    from sqlfluff.core.parser import context, match_algorithms

    # Instrument prune_options
    original_prune = match_algorithms.prune_options

    def instrumented_prune(options, segments, parse_context, start_idx=0):
        _collector.pruning_calls += 1
        _collector.pruning_total += len(options)

        result = original_prune(options, segments, parse_context, start_idx)

        _collector.pruning_kept += len(result)

        # Count hinted vs complex
        for opt in options:
            simple = opt.simple(parse_context=parse_context)
            if simple is None:
                _collector.pruning_complex += 1
            else:
                _collector.pruning_hinted += 1

        return result

    # Patch the module attribute
    match_algorithms.prune_options = instrumented_prune

    # IMPORTANT: Also patch the globals of all functions that call prune_options
    for name, func in match_algorithms.__dict__.items():
        if callable(func) and hasattr(func, "__globals__"):
            if "prune_options" in func.__globals__:
                func.__globals__["prune_options"] = instrumented_prune

    # Instrument cache
    original_check = context.ParseContext.check_parse_cache
    original_put = context.ParseContext.put_parse_cache

    def instrumented_check(self, loc_key, matcher_key):
        result = original_check(self, loc_key, matcher_key)
        if result is not None:
            _collector.cache_hits += 1
        else:
            _collector.cache_misses += 1
        return result

    def instrumented_put(self, loc_key, matcher_key, match):
        original_put(self, loc_key, matcher_key, match)
        # Access via the dict to get current size
        _collector.cache_entries = len(self._parse_cache)

    context.ParseContext.check_parse_cache = instrumented_check
    context.ParseContext.put_parse_cache = instrumented_put

    # Instrument longest_match for better match tracking
    original_longest_match = match_algorithms.longest_match

    def instrumented_longest_match(segments, matchers, idx, parse_context):
        _collector.match_attempts += len(matchers)

        # Track depth via recursion counter
        _collector.current_match_depth += 1
        _collector.max_match_depth = max(
            _collector.max_match_depth, _collector.current_match_depth
        )

        try:
            result, matcher = original_longest_match(
                segments, matchers, idx, parse_context
            )

            if result and result.matched_slice.stop > idx:
                _collector.match_successes += 1

            return result, matcher
        finally:
            _collector.current_match_depth -= 1

    match_algorithms.longest_match = instrumented_longest_match

    # Patch globals in match_algorithms module
    for name, func in match_algorithms.__dict__.items():
        if callable(func) and hasattr(func, "__globals__"):
            if "longest_match" in func.__globals__:
                func.__globals__["longest_match"] = instrumented_longest_match

    # Also patch the grammar modules that import longest_match directly
    from sqlfluff.core.parser.grammar import anyof, delimited, sequence

    anyof.longest_match = instrumented_longest_match
    delimited.longest_match = instrumented_longest_match

    # Patch all functions in those modules too
    for mod in [anyof, delimited, sequence]:
        for name, func in mod.__dict__.items():
            if callable(func) and hasattr(func, "__globals__"):
                if "longest_match" in func.__globals__:
                    func.__globals__["longest_match"] = instrumented_longest_match

    # Instrument terminator checking
    original_trim = match_algorithms.trim_to_terminator

    def instrumented_trim(segments, idx, terminators, parse_context):
        if terminators:
            _collector.terminator_checks += 1

        result = original_trim(segments, idx, terminators, parse_context)

        # If result is less than len(segments), we hit a terminator
        if result < len(segments):
            _collector.terminator_hits += 1

        return result

    match_algorithms.trim_to_terminator = instrumented_trim

    # Patch globals in match_algorithms for trim_to_terminator
    for name, func in match_algorithms.__dict__.items():
        if callable(func) and hasattr(func, "__globals__"):
            if "trim_to_terminator" in func.__globals__:
                func.__globals__["trim_to_terminator"] = instrumented_trim

    # Patch trim_to_terminator in grammar modules too
    for mod in [anyof, delimited, sequence]:
        if hasattr(mod, "trim_to_terminator"):
            mod.trim_to_terminator = instrumented_trim
        for name, func in mod.__dict__.items():
            if callable(func) and hasattr(func, "__globals__"):
                if "trim_to_terminator" in func.__globals__:
                    func.__globals__["trim_to_terminator"] = instrumented_trim


# Instrument before any parsing happens
instrument_python_parser()


def parse_with_python(sql: str, dialect: str = "ansi") -> ParserMetrics:
    """Parse SQL with Python parser and collect metrics."""
    from sqlfluff.core import Linter
    from sqlfluff.core.config import FluffConfig

    _collector.reset()

    # Force Python parser by disabling Rust parser
    config = FluffConfig(overrides={"dialect": dialect, "use_rust_parser": False})
    linter = Linter(config=config)

    start = time.perf_counter()
    parsed = linter.parse_string(sql)
    end = time.perf_counter()

    metrics = ParserMetrics(name="Python")
    metrics.parse_time_ms = (end - start) * 1000

    # Count tokens - exclude meta segments (indent/dedent) for fair comparison with Rust
    if parsed.tree:
        # Meta segments (indent, dedent) are added by the parser, not lexer
        # For apples-to-apples comparison with Rust lexer token count,
        # exclude them
        non_meta_segments = [seg for seg in parsed.tree.raw_segments if not seg.is_meta]
        metrics.token_count = len(non_meta_segments)

    # Copy collected metrics
    metrics.pruning_calls = _collector.pruning_calls
    metrics.pruning_total_options = _collector.pruning_total
    metrics.pruning_kept_options = _collector.pruning_kept
    metrics.pruning_hinted = _collector.pruning_hinted
    metrics.pruning_complex = _collector.pruning_complex
    metrics.cache_hits = _collector.cache_hits
    metrics.cache_misses = _collector.cache_misses
    metrics.cache_entries = _collector.cache_entries
    metrics.match_attempts = _collector.match_attempts
    metrics.match_successes = _collector.match_successes
    metrics.terminator_hits = _collector.terminator_hits
    metrics.terminator_checks = _collector.terminator_checks
    metrics.max_parse_depth = _collector.max_parse_depth
    metrics.max_match_depth = _collector.max_match_depth

    return metrics


def parse_with_rust(sql: str, dialect: str = "ansi") -> ParserMetrics:
    """Parse SQL with Rust parser and collect metrics."""
    import sqlfluffrs

    metrics = ParserMetrics(name="Rust")

    # Get lexer and tokens using dialect parameter
    lexer = sqlfluffrs.RsLexer(dialect=dialect)
    tokens, _ = lexer._lex(sql)  # noqa: SLF001
    metrics.token_count = len(tokens)

    # Create parser and parse with stats
    parser = sqlfluffrs.RsParser(dialect)

    start = time.perf_counter()
    _, stats = parser.parse_match_result_with_stats(list(tokens))
    end = time.perf_counter()

    metrics.parse_time_ms = (end - start) * 1000

    # Extract stats
    metrics.cache_hits = stats.get("cache_hits", 0)
    metrics.cache_misses = stats.get("cache_misses", 0)
    metrics.cache_entries = stats.get("cache_entries", 0)
    metrics.pruning_calls = stats.get("pruning_calls", 0)
    metrics.pruning_total_options = stats.get("pruning_total", 0)
    metrics.pruning_kept_options = stats.get("pruning_kept", 0)
    metrics.pruning_hinted = stats.get("pruning_hinted", 0)
    metrics.pruning_complex = stats.get("pruning_complex", 0)
    metrics.match_attempts = stats.get("match_attempts", 0)
    metrics.match_successes = stats.get("match_successes", 0)
    metrics.terminator_hits = stats.get("terminator_hits", 0)
    metrics.terminator_checks = stats.get("terminator_checks", 0)
    metrics.max_parse_depth = stats.get("max_parse_depth", 0)
    metrics.max_match_depth = stats.get("max_match_depth", 0)

    return metrics


def parse_with_rust_fallback(
    sql: str, dialect: str = "ansi"
) -> Optional[ParserMetrics]:
    """Parse with Rust, returning None if not available."""
    try:
        return parse_with_rust(sql, dialect)
    except (ImportError, AttributeError) as e:
        print(f"Note: Rust parser not available: {e}")
        return None


def print_comparison(
    python_metrics: ParserMetrics, rust_metrics: Optional[ParserMetrics]
) -> None:
    """Print side-by-side comparison of metrics."""
    print("\n" + "=" * 80)
    print("PYTHON vs RUST PARSER METRICS COMPARISON")
    print("=" * 80)

    def fmt(val: Any, width: int = 12) -> str:
        if isinstance(val, float):
            return f"{val:>{width}.2f}"
        return f"{val:>{width}}"

    def pct(val: float) -> str:
        return f"{val:>6.1f}%"

    print(f"\n{'Metric':<35} {'Python':>12} {'Rust':>12} {'Diff':>12}")
    print("-" * 75)

    # Timing
    print(f"{'Parse Time (ms)':<35} {fmt(python_metrics.parse_time_ms)}", end="")
    if rust_metrics:
        diff = rust_metrics.parse_time_ms - python_metrics.parse_time_ms
        diff_pct = (
            (diff / python_metrics.parse_time_ms * 100)
            if python_metrics.parse_time_ms > 0
            else 0
        )
        print(f" {fmt(rust_metrics.parse_time_ms)} {diff:>+12.2f} ({diff_pct:+.1f}%)")
    else:
        print(" N/A")

    print(f"{'ms per Token':<35} {fmt(python_metrics.ms_per_token, 12)}", end="")
    if rust_metrics:
        diff = rust_metrics.ms_per_token - python_metrics.ms_per_token
        print(f" {fmt(rust_metrics.ms_per_token, 12)} {diff:>+12.4f}")
    else:
        print(" N/A")

    print(f"{'Token Count':<35} {fmt(python_metrics.token_count)}", end="")
    if rust_metrics:
        print(f" {fmt(rust_metrics.token_count)}")
    else:
        print(" N/A")

    # Cache metrics
    print(f"\n{'--- Cache Metrics ---':<35}")
    print(f"{'Cache Hits':<35} {fmt(python_metrics.cache_hits)}", end="")
    if rust_metrics:
        diff = rust_metrics.cache_hits - python_metrics.cache_hits
        print(f" {fmt(rust_metrics.cache_hits)} {diff:>+12}")
    else:
        print(" N/A")

    print(f"{'Cache Misses':<35} {fmt(python_metrics.cache_misses)}", end="")
    if rust_metrics:
        diff = rust_metrics.cache_misses - python_metrics.cache_misses
        print(f" {fmt(rust_metrics.cache_misses)} {diff:>+12}")
    else:
        print(" N/A")

    print(f"{'Cache Entries':<35} {fmt(python_metrics.cache_entries)}", end="")
    if rust_metrics:
        diff = rust_metrics.cache_entries - python_metrics.cache_entries
        print(f" {fmt(rust_metrics.cache_entries)} {diff:>+12}")
    else:
        print(" N/A")

    print(
        f"{'Cache Hit Rate':<35} {pct(python_metrics.cache_hit_rate * 100):>12}", end=""
    )
    if rust_metrics:
        diff = (rust_metrics.cache_hit_rate - python_metrics.cache_hit_rate) * 100
        print(f" {pct(rust_metrics.cache_hit_rate * 100):>12} {diff:>+12.1f}pp")
    else:
        print(" N/A")

    # Pruning metrics
    print(f"\n{'--- Pruning Metrics ---':<35}")
    print(f"{'Pruning Calls':<35} {fmt(python_metrics.pruning_calls)}", end="")
    if rust_metrics:
        diff = rust_metrics.pruning_calls - python_metrics.pruning_calls
        print(f" {fmt(rust_metrics.pruning_calls)} {diff:>+12}")
    else:
        print(" N/A")

    print(
        f"{'Total Options Considered':<35} {fmt(python_metrics.pruning_total_options)}",
        end="",
    )
    if rust_metrics:
        diff = rust_metrics.pruning_total_options - python_metrics.pruning_total_options
        print(f" {fmt(rust_metrics.pruning_total_options)} {diff:>+12}")
    else:
        print(" N/A")

    print(
        f"{'Options Kept After Pruning':<35} {fmt(python_metrics.pruning_kept_options)}",
        end="",
    )
    if rust_metrics:
        diff = rust_metrics.pruning_kept_options - python_metrics.pruning_kept_options
        print(f" {fmt(rust_metrics.pruning_kept_options)} {diff:>+12}")
    else:
        print(" N/A")

    print(
        f"{'Pruning Rate (% dropped)':<35} {pct(python_metrics.pruning_rate * 100):>12}",
        end="",
    )
    if rust_metrics:
        diff = (rust_metrics.pruning_rate - python_metrics.pruning_rate) * 100
        print(f" {pct(rust_metrics.pruning_rate * 100):>12} {diff:>+12.1f}pp")
    else:
        print(" N/A")

    print(f"{'Options with Hints':<35} {fmt(python_metrics.pruning_hinted)}", end="")
    if rust_metrics:
        diff = rust_metrics.pruning_hinted - python_metrics.pruning_hinted
        print(f" {fmt(rust_metrics.pruning_hinted)} {diff:>+12}")
    else:
        print(" N/A")

    print(
        f"{'Complex Options (no hint)':<35} {fmt(python_metrics.pruning_complex)}",
        end="",
    )
    if rust_metrics:
        diff = rust_metrics.pruning_complex - python_metrics.pruning_complex
        print(f" {fmt(rust_metrics.pruning_complex)} {diff:>+12}")
    else:
        print(" N/A")

    # Match attempt metrics
    print(f"\n{'--- Match Attempt Metrics ---':<35}")
    print(f"{'Match Attempts':<35} {fmt(python_metrics.match_attempts)}", end="")
    if rust_metrics:
        diff = rust_metrics.match_attempts - python_metrics.match_attempts
        print(f" {fmt(rust_metrics.match_attempts)} {diff:>+12}")
    else:
        print(" N/A")

    print(f"{'Match Successes':<35} {fmt(python_metrics.match_successes)}", end="")
    if rust_metrics:
        diff = rust_metrics.match_successes - python_metrics.match_successes
        print(f" {fmt(rust_metrics.match_successes)} {diff:>+12}")
    else:
        print(" N/A")

    print(
        f"{'Match Success Rate':<35} {pct(python_metrics.match_success_rate * 100):>12}",
        end="",
    )
    if rust_metrics:
        diff = (
            rust_metrics.match_success_rate - python_metrics.match_success_rate
        ) * 100
        print(f" {pct(rust_metrics.match_success_rate * 100):>12} {diff:>+12.1f}pp")
    else:
        print(" N/A")

    # Terminator metrics
    print(f"\n{'--- Terminator Metrics ---':<35}")
    print(f"{'Terminator Checks':<35} {fmt(python_metrics.terminator_checks)}", end="")
    if rust_metrics:
        diff = rust_metrics.terminator_checks - python_metrics.terminator_checks
        print(f" {fmt(rust_metrics.terminator_checks)} {diff:>+12}")
    else:
        print(" N/A")

    print(
        f"{'Terminator Hits (early exit)':<35} {fmt(python_metrics.terminator_hits)}",
        end="",
    )
    if rust_metrics:
        diff = rust_metrics.terminator_hits - python_metrics.terminator_hits
        print(f" {fmt(rust_metrics.terminator_hits)} {diff:>+12}")
    else:
        print(" N/A")

    print(
        f"{'Terminator Hit Rate':<35} {pct(python_metrics.terminator_hit_rate * 100):>12}",
        end="",
    )
    if rust_metrics:
        diff = (
            rust_metrics.terminator_hit_rate - python_metrics.terminator_hit_rate
        ) * 100
        print(f" {pct(rust_metrics.terminator_hit_rate * 100):>12} {diff:>+12.1f}pp")
    else:
        print(" N/A")

    # Depth metrics
    print(f"\n{'--- Depth Metrics ---':<35}")
    print(f"{'Max Parse Depth':<35} {fmt(python_metrics.max_parse_depth)}", end="")
    if rust_metrics:
        diff = rust_metrics.max_parse_depth - python_metrics.max_parse_depth
        print(f" {fmt(rust_metrics.max_parse_depth)} {diff:>+12}")
    else:
        print(" N/A")

    print(f"{'Max Match Depth':<35} {fmt(python_metrics.max_match_depth)}", end="")
    if rust_metrics:
        diff = rust_metrics.max_match_depth - python_metrics.max_match_depth
        print(f" {fmt(rust_metrics.max_match_depth)} {diff:>+12}")
    else:
        print(" N/A")

    print("\n" + "=" * 80)

    # Summary
    if rust_metrics:
        print("\nSUMMARY:")
        if rust_metrics.parse_time_ms < python_metrics.parse_time_ms:
            speedup = python_metrics.parse_time_ms / rust_metrics.parse_time_ms
            print(f"  ✅ Rust is {speedup:.2f}x faster than Python")
        else:
            slowdown = rust_metrics.parse_time_ms / python_metrics.parse_time_ms
            print(f"  ⚠️  Rust is {slowdown:.2f}x slower than Python")

        cache_diff = rust_metrics.cache_hit_rate - python_metrics.cache_hit_rate
        if abs(cache_diff) > 0.05:
            if cache_diff > 0:
                print(f"  ✅ Rust has {cache_diff*100:.1f}pp higher cache hit rate")
            else:
                print(f"  ⚠️  Rust has {abs(cache_diff)*100:.1f}pp lower cache hit rate")
        else:
            print(f"  ✅ Cache hit rates are similar (diff: {cache_diff*100:.1f}pp)")

        prune_diff = rust_metrics.pruning_rate - python_metrics.pruning_rate
        if abs(prune_diff) > 0.05:
            if prune_diff > 0:
                print(f"  ✅ Rust prunes {prune_diff*100:.1f}pp more options")
            else:
                print(f"  ⚠️  Rust prunes {abs(prune_diff)*100:.1f}pp fewer options")
        else:
            print(f"  ✅ Pruning rates are similar (diff: {prune_diff*100:.1f}pp)")

        # Analysis
        print("\nANALYSIS:")
        if python_metrics.pruning_calls > 0 and rust_metrics.pruning_calls > 0:
            py_opt_per_call = (
                python_metrics.pruning_total_options / python_metrics.pruning_calls
            )
            rs_opt_per_call = (
                rust_metrics.pruning_total_options / rust_metrics.pruning_calls
            )
            print(f"  Python avg options/call: {py_opt_per_call:.1f}")
            print(f"  Rust avg options/call: {rs_opt_per_call:.1f}")

            if abs(py_opt_per_call - rs_opt_per_call) > 1:
                print(
                    "  ⚠️  Different average options per call - "
                    "parsers may be making different decisions"
                )

        # Match attempt analysis
        if python_metrics.match_attempts > 0 and rust_metrics.match_attempts > 0:
            match_diff = rust_metrics.match_attempts - python_metrics.match_attempts
            match_pct = (match_diff / python_metrics.match_attempts) * 100

            if abs(match_pct) > 10:
                if match_diff > 0:
                    print(
                        f"  ⚠️  Rust makes {match_pct:.1f}% MORE match attempts than Python"
                    )
                    print(
                        "      → Possible missing optimization: early termination or caching"
                    )
                else:
                    print(
                        f"  ✅ Rust makes {abs(match_pct):.1f}% FEWER match attempts than Python"
                    )
                    print(
                        "      → Better pruning or different grammar matching strategy"
                    )

        # Terminator effectiveness
        if python_metrics.terminator_checks > 0 and rust_metrics.terminator_checks > 0:
            py_term_rate = python_metrics.terminator_hit_rate
            rs_term_rate = rust_metrics.terminator_hit_rate

            if abs(py_term_rate - rs_term_rate) > 0.1:
                if rs_term_rate < py_term_rate:
                    print(
                        f"  ⚠️  Rust terminator hit rate is {(py_term_rate - rs_term_rate)*100:.1f}pp lower"
                    )
                    print(
                        "      → Possible issue: terminators not being checked or configured correctly"
                    )
                else:
                    print(
                        f"  ✅ Rust terminator hit rate is {(rs_term_rate - py_term_rate)*100:.1f}pp higher"
                    )

        # Cache effectiveness comparison
        if python_metrics.cache_hits > 0 and rust_metrics.cache_hits > 0:
            # Cache reuse per match attempt
            py_cache_per_match = (
                python_metrics.cache_hits / python_metrics.match_attempts
                if python_metrics.match_attempts > 0
                else 0
            )
            rs_cache_per_match = (
                rust_metrics.cache_hits / rust_metrics.match_attempts
                if rust_metrics.match_attempts > 0
                else 0
            )

            if abs(py_cache_per_match - rs_cache_per_match) > 0.05:
                if rs_cache_per_match < py_cache_per_match:
                    print(
                        f"  ⚠️  Rust cache efficiency is lower ({rs_cache_per_match:.2f} vs {py_cache_per_match:.2f} hits/attempt)"
                    )
                    print(
                        "      → Possible issue: different cache key strategy or granularity"
                    )

        # Depth analysis
        if python_metrics.max_parse_depth > 0 and rust_metrics.max_parse_depth > 0:
            depth_diff = rust_metrics.max_parse_depth - python_metrics.max_parse_depth
            if abs(depth_diff) > 5:
                if depth_diff > 0:
                    print(f"  ⚠️  Rust parse depth is {depth_diff} levels deeper")
                    print(
                        "      → May indicate less efficient recursion or different grammar structure"
                    )
                else:
                    print(
                        f"  ✅ Rust parse depth is {abs(depth_diff)} levels shallower"
                    )


def main() -> None:
    """Run the parser comparison."""
    parser = argparse.ArgumentParser(
        description="Compare Python and Rust parser metrics"
    )
    parser.add_argument("--sql", type=str, help="SQL to parse")
    parser.add_argument("--file", type=str, help="SQL file to parse")
    parser.add_argument(
        "--dialect", type=str, default="ansi", help="SQL dialect (default: ansi)"
    )

    args = parser.parse_args()

    # Get SQL
    if args.sql:
        sql = args.sql
    elif args.file:
        with open(args.file, encoding="utf-8") as f:
            sql = f.read()
    else:
        # Default test SQL
        sql = """
SELECT
    a.id,
    b.name,
    CASE
        WHEN a.status = 1 THEN 'Active'
        WHEN a.status = 2 THEN 'Inactive'
        ELSE 'Unknown'
    END AS status_text,
    (SELECT COUNT(*) FROM orders o WHERE o.customer_id = a.id) AS order_count
FROM customers a
LEFT JOIN customer_details b ON a.id = b.customer_id
WHERE a.created_at > '2024-01-01'
    AND (a.type = 'premium' OR a.total_spent > 1000)
ORDER BY a.created_at DESC
LIMIT 100
"""

    print(f"SQL ({len(sql)} chars):")
    print("-" * 40)
    if len(sql) > 500:
        print(sql[:500] + "...")
    else:
        print(sql)
    print("-" * 40)
    print(f"Dialect: {args.dialect}")

    # Parse with both
    python_metrics = parse_with_python(sql, args.dialect)
    rust_metrics = parse_with_rust_fallback(sql, args.dialect)

    # Print comparison
    print_comparison(python_metrics, rust_metrics)


if __name__ == "__main__":
    main()

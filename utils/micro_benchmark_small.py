#!/usr/bin/env python3
"""Micro-benchmark to investigate Rust parser overhead on small SQL files."""
import time

import sqlfluffrs
from sqlfluff.core import Linter
from sqlfluff.core.config import FluffConfig

# Test files that show regression
test_cases = [
    ("test/fixtures/dialects/bigquery/drop_materialized_view.sql", "bigquery"),
    ("test/fixtures/dialects/trino/commit.sql", "trino"),
    ("test/fixtures/dialects/ansi/truncate_table_a.sql", "ansi"),
    ("test/fixtures/dialects/ansi/arithmetic_a.sql", "ansi"),
    ("test/fixtures/dialects/ansi/expression_recursion.sql", "ansi"),
]


def time_python_parser(sql, dialect, iterations=100):
    """Time Python parser."""
    config = FluffConfig(overrides={"dialect": dialect, "use_rust_parser": False})
    linter = Linter(config=config)

    start = time.perf_counter()
    for _ in range(iterations):
        linter.parse_string(sql)
    elapsed = time.perf_counter() - start
    return elapsed / iterations


def time_rust_parser(sql, dialect, iterations=100):
    """Time Rust parser."""
    lexer = sqlfluffrs.RsLexer(dialect=dialect)
    parser = sqlfluffrs.RsParser(dialect)

    # Lex once outside timing (reused for all iterations)
    tokens, _ = lexer._lex(sql)
    token_list = list(tokens)

    start = time.perf_counter()
    for _ in range(iterations):
        result, _ = parser.parse_match_result_with_stats(token_list)
    elapsed = time.perf_counter() - start
    return elapsed / iterations


def time_rust_with_lex(sql, dialect, iterations=100):
    """Time Rust parser including lexing."""
    lexer = sqlfluffrs.RsLexer(dialect=dialect)
    parser = sqlfluffrs.RsParser(dialect)

    start = time.perf_counter()
    for _ in range(iterations):
        tokens, _ = lexer._lex(sql)
        result, _ = parser.parse_match_result_with_stats(list(tokens))
    elapsed = time.perf_counter() - start
    return elapsed / iterations


print("=" * 80)
print("MICRO-BENCHMARK: Small SQL Files (100 iterations)")
print("=" * 80)

for filepath, dialect in test_cases:
    with open(filepath) as f:
        sql = f.read()

    print(f"\n{filepath}")
    print(f"Dialect: {dialect}, SQL length: {len(sql)} chars")
    print(f"SQL: {sql.strip()[:60]}...")

    py_time = time_python_parser(sql, dialect)
    rust_time = time_rust_parser(sql, dialect)
    rust_with_lex_time = time_rust_with_lex(sql, dialect)

    print(f"  Python:              {py_time * 1000:.3f}ms")
    print(f"  Rust (parse only):   {rust_time * 1000:.3f}ms")
    print(f"  Rust (lex + parse):  {rust_with_lex_time * 1000:.3f}ms")
    print(f"  Speedup (parse):     {py_time / rust_time:.2f}x")
    print(f"  Speedup (total):     {py_time / rust_with_lex_time:.2f}x")

    # Check if lexing dominates
    lex_overhead = rust_with_lex_time - rust_time
    print(
        f"  Lex overhead:        {lex_overhead * 1000:.3f}ms "
        f"({lex_overhead / rust_with_lex_time * 100:.1f}%)"
    )

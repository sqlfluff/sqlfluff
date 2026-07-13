"""CodSpeed benchmark: parse the TPC-H/TPC-DS query suites via all 3 parser modes.

Six benchmarks are exposed to pytest-codspeed, each parsing the full query
suite once per benchmark iteration through `Linter.parse_string`:

- `test_parse_tpch` / `test_parse_tpcds`: the Rust parser's default
  (legacy convert+apply) path (`use_rust_parser=True`).
- `test_native_ast_tpch` / `test_native_ast_tpcds`: the Rust parser's native
  AST path (`use_rust_parser=True`, `set_native_ast(True)`), which builds the
  BaseSegment tree in a single fused pass over the Rust match result.
- `test_parse_tpch_python` / `test_parse_tpcds_python`: the pure-Python
  parser (`use_rust_parser=False`).

These mirror the 3 parser modes measured by the local historical sweep in
`utils/perf_sweep` (python / rust_legacy / rust_native_ast).

Run instrumented (as CI does):
    pytest test/test_codspeed_tpc_parse.py --codspeed

Run as a plain correctness check (the `benchmark` fixture just calls the
wrapped function once when not run under `--codspeed`):
    pytest test/test_codspeed_tpc_parse.py
"""

import pathlib
import urllib.request
from collections.abc import Iterator
from urllib.error import URLError

import pytest

from sqlfluff.core import Linter
from sqlfluff.core.config import FluffConfig
from sqlfluff.core.parser import rust_parser

# TPC-H/TPC-DS query fixtures, mirroring sqlfluffrs_benchmarks/build.rs so the
# query text matches the Rust criterion benches (tpc_bench.rs) exactly. Not
# committed to the repo; downloaded on first run and cached under `.cache`
# (gitignored).
_DORIS_SHA = "3a2d9d55f1e8e2d74187179ef89c36c8562815fd"
_DORIS_RAW_BASE = "https://raw.githubusercontent.com/apache/doris"
_TPCH_N = 22
_TPCDS_N = 99
_TPCDS_SPLIT = (14, 23, 24, 39)
_PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
_TPC_CACHE_DIR = _PROJECT_ROOT / "test" / ".cache" / "tpc"


def _normalize_tpc_sql(raw: str) -> str:
    # Mirrors sqlfluffrs_benchmarks/build.rs's `normalize`: Unix line endings,
    # trailing whitespace stripped per line, ending with a single newline.
    lines = raw.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return "\n".join(line.rstrip() for line in lines).rstrip("\n") + "\n"


def _download_tpc_sql(url: str) -> str:
    with urllib.request.urlopen(url, timeout=30) as resp:
        return resp.read().decode("utf-8")


def _ensure_tpc_fixtures() -> bool:
    """Download and cache the TPC-H/TPC-DS query fixtures if not already present.

    Mirrors sqlfluffrs_benchmarks/build.rs so the query text matches the Rust
    benchmarks exactly. Returns False if the fixtures are unavailable and
    couldn't be fetched (e.g. no network), in which case the caller should skip.
    """
    marker = _TPC_CACHE_DIR / ".doris-sha"
    if marker.exists() and marker.read_text().strip() == _DORIS_SHA:
        return True

    tpch_dir = _TPC_CACHE_DIR / "tpc-h"
    tpcds_dir = _TPC_CACHE_DIR / "tpc-ds"
    tpch_dir.mkdir(parents=True, exist_ok=True)
    tpcds_dir.mkdir(parents=True, exist_ok=True)

    try:
        for n in range(1, _TPCH_N + 1):
            url = f"{_DORIS_RAW_BASE}/{_DORIS_SHA}/tools/tpch-tools/queries/q{n}.sql"
            sql = _normalize_tpc_sql(_download_tpc_sql(url))
            (tpch_dir / f"{n}.sql").write_text(sql)

        for n in range(1, _TPCDS_N + 1):
            url = (
                f"{_DORIS_RAW_BASE}/{_DORIS_SHA}/tools/tpcds-tools/queries/"
                f"sf1/query{n}.sql"
            )
            sql = _normalize_tpc_sql(_download_tpc_sql(url))
            if n in _TPCDS_SPLIT:
                url2 = (
                    f"{_DORIS_RAW_BASE}/{_DORIS_SHA}/tools/tpcds-tools/queries/"
                    f"sf1/query{n}_1.sql"
                )
                part2 = _normalize_tpc_sql(_download_tpc_sql(url2))
                sql = f"{sql}\n{part2}"
            (tpcds_dir / f"{n}.sql").write_text(sql)
    except (OSError, URLError):
        return False

    marker.write_text(f"{_DORIS_SHA}\n")
    return True


def _load_tpc_queries(sub_dir: str, count: int) -> list[str]:
    d = _TPC_CACHE_DIR / sub_dir
    return [(d / f"{n}.sql").read_text() for n in range(1, count + 1)]


@pytest.fixture(scope="session")
def rust_linter() -> Linter:
    """Return a Linter configured to use the Rust parser."""
    cfg = FluffConfig(
        overrides={"dialect": "ansi", "use_rust_parser": True},
        ignore_local_config=True,
    )
    return Linter(config=cfg)


@pytest.fixture(scope="session")
def python_linter() -> Linter:
    """Return a Linter configured to use the pure-Python parser."""
    cfg = FluffConfig(
        overrides={"dialect": "ansi", "use_rust_parser": False},
        ignore_local_config=True,
    )
    return Linter(config=cfg)


@pytest.fixture
def native_ast_enabled() -> Iterator[None]:
    """Enable the native AST path for the duration of a test.

    native_ast only exists from upstream PR #7983 onward. On an older
    checked-out commit, skip rather than error, since an AttributeError here
    would otherwise fail the whole pytest invocation (and thus the
    CodSpeed upload) for that commit, same reasoning as
    utils/perf_sweep/bench_runner.py's NATIVE_AST_UNAVAILABLE handling.
    """
    if not hasattr(rust_parser, "set_native_ast"):
        pytest.skip("native_ast toggle not present at this commit")
    previous = rust_parser._NATIVE_AST_ENABLED
    rust_parser.set_native_ast(True)
    yield
    rust_parser.set_native_ast(previous)


@pytest.fixture(scope="session")
def tpch_queries() -> list[str]:
    """Return the cached TPC-H query fixtures, fetching them if needed."""
    if not _ensure_tpc_fixtures():
        pytest.skip("could not fetch TPC-H/TPC-DS fixtures and no cache present")
    return _load_tpc_queries("tpc-h", _TPCH_N)


@pytest.fixture(scope="session")
def tpcds_queries() -> list[str]:
    """Return the cached TPC-DS query fixtures, fetching them if needed."""
    if not _ensure_tpc_fixtures():
        pytest.skip("could not fetch TPC-H/TPC-DS fixtures and no cache present")
    return _load_tpc_queries("tpc-ds", _TPCDS_N)


def test_parse_tpch(benchmark, rust_linter: Linter, tpch_queries: list[str]) -> None:
    """Benchmark parsing the TPC-H query set with the Rust parser."""

    @benchmark
    def _run() -> None:
        for sql in tpch_queries:
            rust_linter.parse_string(sql)


def test_parse_tpcds(benchmark, rust_linter: Linter, tpcds_queries: list[str]) -> None:
    """Benchmark parsing the TPC-DS query set with the Rust parser."""

    @benchmark
    def _run() -> None:
        for sql in tpcds_queries:
            rust_linter.parse_string(sql)


def test_native_ast_tpch(
    benchmark,
    rust_linter: Linter,
    tpch_queries: list[str],
    native_ast_enabled: None,
) -> None:
    """Benchmark parsing the TPC-H query set with the native AST path."""

    @benchmark
    def _run() -> None:
        for sql in tpch_queries:
            rust_linter.parse_string(sql)


def test_native_ast_tpcds(
    benchmark,
    rust_linter: Linter,
    tpcds_queries: list[str],
    native_ast_enabled: None,
) -> None:
    """Benchmark parsing the TPC-DS query set with the native AST path."""

    @benchmark
    def _run() -> None:
        for sql in tpcds_queries:
            rust_linter.parse_string(sql)


def test_parse_tpch_python(
    benchmark, python_linter: Linter, tpch_queries: list[str]
) -> None:
    """Benchmark parsing the TPC-H query set with the pure-Python parser."""

    @benchmark
    def _run() -> None:
        for sql in tpch_queries:
            python_linter.parse_string(sql)


def test_parse_tpcds_python(
    benchmark, python_linter: Linter, tpcds_queries: list[str]
) -> None:
    """Benchmark parsing the TPC-DS query set with the pure-Python parser."""

    @benchmark
    def _run() -> None:
        for sql in tpcds_queries:
            python_linter.parse_string(sql)

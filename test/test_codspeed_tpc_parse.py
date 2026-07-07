"""CodSpeed benchmark: parse the TPC-H/TPC-DS query suites via the Rust parser.

Two benchmarks are exposed to pytest-codspeed: `test_parse_tpch` and
`test_parse_tpcds`, each parsing the full query suite once per benchmark
iteration through `Linter.parse_string` with `use_rust_parser` enabled.

Run instrumented (as CI does):
    pytest test/test_codspeed_tpc_parse.py --codspeed

Run as a plain correctness check (the `benchmark` fixture just calls the
wrapped function once when not run under `--codspeed`):
    pytest test/test_codspeed_tpc_parse.py
"""

import pathlib
import urllib.request
from urllib.error import URLError

import pytest

from sqlfluff.core import Linter
from sqlfluff.core.config import FluffConfig

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

"""Download & cache the TPC-H/TPC-DS query fixtures.

Same pinned source and normalization as test/test_codspeed_tpc_parse.py, so
the query text is identical - fetched once and reused across the whole
commit sweep, independent of whichever commit is currently checked out.
"""

from __future__ import annotations

import pathlib
import urllib.request
from urllib.error import URLError

DORIS_SHA = "3a2d9d55f1e8e2d74187179ef89c36c8562815fd"
DORIS_RAW_BASE = "https://raw.githubusercontent.com/apache/doris"
TPCH_N = 22
TPCDS_N = 99
TPCDS_SPLIT = (14, 23, 24, 39)

SUITES = {"tpch": ("tpc-h", TPCH_N), "tpcds": ("tpc-ds", TPCDS_N)}


def _normalize(raw: str) -> str:
    lines = raw.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return "\n".join(line.rstrip() for line in lines).rstrip("\n") + "\n"


def _download(url: str) -> str:
    with urllib.request.urlopen(url, timeout=30) as resp:
        return resp.read().decode("utf-8")


def ensure_fixtures(cache_dir: pathlib.Path) -> bool:
    """Download and cache the fixtures if not already present.

    Returns False (caller should abort) if they're unavailable and
    couldn't be fetched.
    """
    marker = cache_dir / ".doris-sha"
    if marker.exists() and marker.read_text().strip() == DORIS_SHA:
        return True

    tpch_dir = cache_dir / "tpc-h"
    tpcds_dir = cache_dir / "tpc-ds"
    tpch_dir.mkdir(parents=True, exist_ok=True)
    tpcds_dir.mkdir(parents=True, exist_ok=True)

    try:
        for n in range(1, TPCH_N + 1):
            url = f"{DORIS_RAW_BASE}/{DORIS_SHA}/tools/tpch-tools/queries/q{n}.sql"
            (tpch_dir / f"{n}.sql").write_text(_normalize(_download(url)))

        for n in range(1, TPCDS_N + 1):
            url = f"{DORIS_RAW_BASE}/{DORIS_SHA}/tools/tpcds-tools/queries/sf1/query{n}.sql"
            sql = _normalize(_download(url))
            if n in TPCDS_SPLIT:
                url2 = (
                    f"{DORIS_RAW_BASE}/{DORIS_SHA}/tools/tpcds-tools/queries/"
                    f"sf1/query{n}_1.sql"
                )
                sql = f"{sql}\n{_normalize(_download(url2))}"
            (tpcds_dir / f"{n}.sql").write_text(sql)
    except (OSError, URLError):
        return False

    marker.write_text(f"{DORIS_SHA}\n")
    return True


def load_queries(cache_dir: pathlib.Path, suite: str) -> list:
    """Read a suite's numbered .sql fixtures into a list, in order."""
    sub_dir, count = SUITES[suite]
    d = cache_dir / sub_dir
    return [(d / f"{n}.sql").read_text() for n in range(1, count + 1)]

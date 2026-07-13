"""Per-iteration performance summary.

Callgrind instruction counts and walltime mean/p95/p99, compared against
the previous benchmarked commit and against the 4.2.2 baseline.
Deliberately reads the same output files bench_runner.py/cli.py already
write (`<mode>-<suite>-callgrind.out`, `<mode>-<suite>-walltime.json`) rather
than threading extra state through the measurement path.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Point:
    """One mode/suite measurement: callgrind Ir plus walltime mean/p95/p99."""

    status: str  # "ok" | "not_applicable" | "error" | "missing"
    ir: Optional[int] = None
    mean: Optional[float] = None
    p95: Optional[float] = None
    p99: Optional[float] = None


def parse_callgrind_ir(path: Path) -> Optional[int]:
    """Sum the `summary:` line(s) of a callgrind output file.

    That total is the instruction count for the instrumented run.
    """
    if not path.exists():
        return None
    total = 0
    found = False
    for line in path.read_text(errors="replace").splitlines():
        if line.startswith("summary:"):
            total += int(line.split(":", 1)[1].strip())
            found = True
    return total if found else None


def percentile(data: list, pct: float) -> Optional[float]:
    """Linear-interpolated percentile (pct in [0, 100]) of data."""
    if not data:
        return None
    ordered = sorted(data)
    k = (len(ordered) - 1) * (pct / 100)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return ordered[int(k)]
    return ordered[f] + (ordered[c] - ordered[f]) * (k - f)


def points_from_meta(meta: dict) -> Optional[dict]:
    """Build {mode: {suite: Point}} from one commit's meta.json.

    Returns None if the commit was skipped, a dry run, or failed to build -
    none of which carry real measurements.
    """
    if meta.get("skipped") or meta.get("dry_run") or meta.get("build_failed"):
        return None
    points: dict = {}
    for mode, suites in meta.get("modes", {}).items():
        points[mode] = {
            suite: read_point(mode_result) for suite, mode_result in suites.items()
        }
    return points


def read_point(mode_result: dict) -> Point:
    """Build a Point from one mode/suite result dict.

    `mode_result` is `{"callgrind": outcome, "walltime": outcome}`, the per
    mode/suite dict `_measure` returns in cli.py.
    """
    cg = mode_result.get("callgrind", {})
    wt = mode_result.get("walltime", {})
    status = cg.get("status") or wt.get("status") or "missing"

    ir = None
    if cg.get("status") == "ok":
        ir = parse_callgrind_ir(Path(cg["output_file"]))

    mean = p95 = p99 = None
    if wt.get("status") == "ok":
        data = json.loads(Path(wt["output_file"]).read_text())
        rounds = data.get("rounds_seconds", [])
        mean = data.get("mean_seconds")
        p95 = percentile(rounds, 95)
        p99 = percentile(rounds, 99)

    return Point(status=status, ir=ir, mean=mean, p95=p95, p99=p99)


def pct_delta(new: Optional[float], old: Optional[float]) -> Optional[float]:
    """Percent change of new relative to old, or None if either is missing/zero."""
    if new is None or old is None or old == 0:
        return None
    return (new - old) / old * 100


def _fmt_delta(pct: Optional[float]) -> str:
    if pct is None:
        return "n/a"
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.2f}%"


def _fmt_ir(ir: Optional[int]) -> str:
    return "n/a" if ir is None else f"{ir:,}"


def _fmt_seconds(s: Optional[float]) -> str:
    return "n/a" if s is None else f"{s:.4f}s"


def render_summary_table(
    modes: list,
    suites: list,
    current: dict,
    previous: Optional[dict],
    baseline: Optional[dict],
) -> str:
    """Render a per-mode/suite table of current Ir/walltime vs previous and baseline.

    current/previous/baseline are {mode: {suite: Point}}; previous/baseline
    may be None (no prior real commit yet / baseline not available).
    """
    lines = ["  --- performance summary (vs previous commit, vs 4.2.2 baseline) ---"]
    for mode in modes:
        for suite in suites:
            cur = current.get(mode, {}).get(suite)
            if cur is None:
                continue
            if cur.status != "ok":
                lines.append(f"  {mode} / {suite}: {cur.status}")
                continue
            prev = previous.get(mode, {}).get(suite) if previous else None
            base = baseline.get(mode, {}).get(suite) if baseline else None
            prev = prev if (prev and prev.status == "ok") else None
            base = base if (base and base.status == "ok") else None

            lines.append(f"  {mode} / {suite}:")
            lines.append(
                f"    callgrind Ir:  {_fmt_ir(cur.ir):>15}   "
                f"(prev {_fmt_delta(pct_delta(cur.ir, prev.ir if prev else None))}, "
                f"4.2.2 {_fmt_delta(pct_delta(cur.ir, base.ir if base else None))})"
            )
            lines.append(
                f"    walltime mean: {_fmt_seconds(cur.mean):>15}   "
                f"(prev {_fmt_delta(pct_delta(cur.mean, prev.mean if prev else None))}, "
                f"4.2.2 {_fmt_delta(pct_delta(cur.mean, base.mean if base else None))})"
            )
            lines.append(
                f"    walltime p95:  {_fmt_seconds(cur.p95):>15}   "
                f"(prev {_fmt_delta(pct_delta(cur.p95, prev.p95 if prev else None))}, "
                f"4.2.2 {_fmt_delta(pct_delta(cur.p95, base.p95 if base else None))})"
            )
            lines.append(
                f"    walltime p99:  {_fmt_seconds(cur.p99):>15}   "
                f"(prev {_fmt_delta(pct_delta(cur.p99, prev.p99 if prev else None))}, "
                f"4.2.2 {_fmt_delta(pct_delta(cur.p99, base.p99 if base else None))})"
            )
    return "\n".join(lines)

"""Cross-commit trend report over a perf_sweep output directory.

Reads `manifest.jsonl` for commit identity and each commit's `meta.json` for
its measurements (via `perf_summary.read_point`, the same per-commit parser
cli.py already uses) - nothing here is pre-aggregated by the sweep itself,
per README.md. Commit order is derived from `--repo`'s actual git ancestry
(manifest.jsonl's append order isn't reliable once a sweep has been re-run
over more than one range). Prints a terminal summary table and writes a
self-contained HTML page with one line chart per (suite, metric).

Usage:
    python -m utils.perf_sweep.trend --output bench-results
    python -m utils.perf_sweep.trend --output bench-results --repo /path/to/sqlfluff
    python -m utils.perf_sweep.trend --output bench-results --no-html
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

from . import gitrange, perf_summary
from . import manifest as manifest_mod

MODES = ["python", "rust_legacy", "rust_native_ast"]
MODE_LABELS = {"python": "python", "rust_legacy": "legacy", "rust_native_ast": "native"}
SUITES = ["tpch", "tpcds"]


class CommitRow:
    """One commit's measurements, as {mode: {suite: Point}}."""

    def __init__(self, sha: str, subject: str, author_date: str, points: dict) -> None:
        self.sha = sha
        self.subject = subject
        self.author_date = author_date
        self.points = points  # {mode: {suite: Point}}


def _order_by_ancestry(repo_dir: Path, shas: list) -> list:
    """Sort shas oldest-first by real git ancestry, not by manifest append order.

    manifest.jsonl's append order only matches chronology when the whole file
    was produced by one contiguous resolve_commits() call. A sweep re-run over
    a different or overlapping --start-ref/--end-ref appends its commits after
    whatever is already there, regardless of where they actually sit in
    history - so a later append can be an ancestor of an earlier one.
    `git rev-list --topo-order --reverse` walks the real commit graph and is
    the source of truth here.
    """
    if not shas:
        return []
    out = gitrange.run_git(
        repo_dir, "rev-list", "--topo-order", "--reverse", *shas
    ).stdout
    wanted = set(shas)
    ordered = [line for line in out.splitlines() if line in wanted]
    # Any sha rev-list didn't surface (e.g. its history was rewritten/removed
    # from repo_dir since the sweep ran) still needs to be reported somewhere.
    missing = [s for s in shas if s not in ordered]
    return ordered + missing


def load_rows(output_dir: Path, repo_dir: Path) -> list:
    """Oldest-first list of CommitRow for every real commit in manifest.jsonl.

    "Real" excludes skipped, dry-run, and build-failed commits. Ordering is
    derived from actual git ancestry via _order_by_ancestry(), not from
    manifest.jsonl's append order - see its docstring for why that matters.
    """
    entries = manifest_mod.load_manifest(output_dir / "manifest.jsonl")
    row_by_sha = {}
    for sha, entry in entries.items():
        meta_path = output_dir / sha / "meta.json"
        if not meta_path.exists():
            continue
        points = perf_summary.points_from_meta(json.loads(meta_path.read_text()))
        if points is None:
            continue
        row_by_sha[sha] = CommitRow(
            sha, entry.get("subject", ""), entry.get("author_date", ""), points
        )

    ordered_shas = _order_by_ancestry(repo_dir, list(row_by_sha.keys()))
    return [row_by_sha[sha] for sha in ordered_shas]


# ---------------------------------------------------------------------------
# Terminal table
# ---------------------------------------------------------------------------


def _fmt_ir(ir: Optional[int]) -> str:
    return "n/a" if ir is None else f"{ir:,}"


def _fmt_seconds(s: Optional[float]) -> str:
    return "n/a" if s is None else f"{s:.4f}s"


def _fmt_delta(pct: Optional[float]) -> str:
    if pct is None:
        return "n/a"
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.2f}%"


def render_terminal_report(rows: list) -> str:
    """Render one table per (mode, suite) with Ir/walltime vs prev and vs base.

    rows[0] doubles as the "vs base" reference - resolve_commits' inclusive
    start_ref makes it the range's first commit, same one cli.py treats as
    the baseline (see gitrange.resolve_commits).
    """
    lines = []
    lines.append("commits in range:")
    for i, row in enumerate(rows):
        lines.append(
            f"  {i:>3}  {row.sha[:10]}  {row.author_date[:10]}  {row.subject[:70]}"
        )
    lines.append("")

    for mode in MODES:
        for suite in SUITES:
            series = [row.points[mode][suite] for row in rows]
            if not any(p and p.status == "ok" for p in series):
                continue

            base = next((p for p in series if p and p.status == "ok"), None)

            lines.append(f"=== {mode} / {suite} ===")
            header = (
                f"  {'#':>3}  {'Ir':>15}  {'vs prev':>9}  {'vs base':>9}  "
                f"{'mean':>9}  {'vs prev':>9}  {'vs base':>9}  {'p95':>9}  {'p99':>9}"
            )
            lines.append(header)
            prev: Optional[perf_summary.Point] = None
            for i, p in enumerate(series):
                if p is None or p.status != "ok":
                    lines.append(f"  {i:>3}  {p.status if p else 'missing'}")
                    continue
                lines.append(
                    f"  {i:>3}  {_fmt_ir(p.ir):>15}  "
                    f"{_fmt_delta(perf_summary.pct_delta(p.ir, prev.ir if prev else None)):>9}  "
                    f"{_fmt_delta(perf_summary.pct_delta(p.ir, base.ir if base else None)):>9}  "
                    f"{_fmt_seconds(p.mean):>9}  "
                    f"{_fmt_delta(perf_summary.pct_delta(p.mean, prev.mean if prev else None)):>9}  "
                    f"{_fmt_delta(perf_summary.pct_delta(p.mean, base.mean if base else None)):>9}  "
                    f"{_fmt_seconds(p.p95):>9}  {_fmt_seconds(p.p99):>9}"
                )
                prev = p
            lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# HTML chart
# ---------------------------------------------------------------------------

CHART_W, CHART_H = 720, 300
MARGIN = {"left": 70, "right": 100, "top": 24, "bottom": 36}
PLOT_W = CHART_W - MARGIN["left"] - MARGIN["right"]
PLOT_H = CHART_H - MARGIN["top"] - MARGIN["bottom"]


def _y_ticks(y_min: float, y_max: float, n: int = 4) -> list:
    return [y_min + (y_max - y_min) * i / n for i in range(n + 1)]


def _x_tick_indices(n: int, target: int = 6) -> list:
    if n <= target:
        return list(range(n))
    step = (n - 1) / (target - 1)
    return sorted({round(i * step) for i in range(target)})


def _build_chart(chart_id: str, title: str, rows: list, value_fn, fmt_fn) -> str:
    """One line chart: value_fn(row, mode) -> Optional[float], fmt_fn(value) -> str.

    Renders points server-side (a static SVG needs no JS to be readable);
    a JS-driven crosshair + tooltip is layered on top for hover detail, per
    the dataviz skill's interaction spec.
    """
    n = len(rows)
    xs = [
        MARGIN["left"] + (i * PLOT_W / (n - 1) if n > 1 else PLOT_W / 2)
        for i in range(n)
    ]

    all_vals = [
        value_fn(r, mode)
        for mode in MODES
        for r in rows
        if value_fn(r, mode) is not None
    ]
    if not all_vals:
        return f'<div class="chart-empty">{title}: no data</div>'
    y_min, y_max = min(all_vals), max(all_vals)
    if y_min == y_max:
        y_min, y_max = y_min - 1, y_max + 1
    else:
        pad = (y_max - y_min) * 0.08
        y_min, y_max = y_min - pad, y_max + pad

    def y_px(v: float) -> float:
        return MARGIN["top"] + PLOT_H - (v - y_min) / (y_max - y_min) * PLOT_H

    svg_parts = []
    ticks = _y_ticks(y_min, y_max)
    for t in ticks:
        y = y_px(t)
        svg_parts.append(
            f'<line class="gridline" x1="{MARGIN["left"]}" y1="{y:.1f}" '
            f'x2="{CHART_W - MARGIN["right"]}" y2="{y:.1f}"/>'
        )
        svg_parts.append(
            f'<text class="axis-label" x="{MARGIN["left"] - 8}" y="{y + 4:.1f}" text-anchor="end">{fmt_fn(t)}</text>'
        )

    for idx in _x_tick_indices(n):
        svg_parts.append(
            f'<text class="axis-label" x="{xs[idx]:.1f}" y="{CHART_H - MARGIN["bottom"] + 16}" '
            f'text-anchor="middle">{rows[idx].author_date[:10]}</text>'
        )

    tooltips = []
    for i, row in enumerate(rows):
        parts = [f"<strong>{row.author_date[:10]}</strong> {row.sha[:10]}"]
        for mode in MODES:
            v = value_fn(row, mode)
            parts.append(
                f'<span class="tt-row"><i style="background:var(--series-{mode})"></i>{MODE_LABELS[mode]}: {fmt_fn(v) if v is not None else "n/a"}</span>'
            )
        tooltips.append("".join(f"<div>{p}</div>" for p in parts))

    for mode in MODES:
        color_var = f"var(--series-{mode})"
        segment: list = []
        segments = []
        for i, row in enumerate(rows):
            v = value_fn(row, mode)
            if v is None:
                if segment:
                    segments.append(segment)
                    segment = []
                continue
            segment.append((xs[i], y_px(v)))
        if segment:
            segments.append(segment)

        for seg in segments:
            d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in seg)
            svg_parts.append(
                f'<path d="{d}" fill="none" stroke="{color_var}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
            )
        for x, y in [p for seg in segments for p in seg]:
            svg_parts.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{color_var}" stroke="var(--surface-1)" stroke-width="2"/>'
            )

        if segments:
            lx, ly = segments[-1][-1]
            svg_parts.append(
                f'<circle cx="{lx + 12:.1f}" cy="{ly:.1f}" r="4" fill="{color_var}"/>'
            )
            svg_parts.append(
                f'<text class="end-label" x="{lx + 20:.1f}" y="{ly + 4:.1f}">{MODE_LABELS[mode]}</text>'
            )

    plot_left, plot_right = MARGIN["left"], CHART_W - MARGIN["right"]
    plot_top, plot_bottom = MARGIN["top"], CHART_H - MARGIN["bottom"]

    return f"""
<div class="chart-block">
  <div class="chart-title">{title}</div>
  <div class="chart-wrap">
    <svg viewBox="0 0 {CHART_W} {CHART_H}" class="chart-svg" id="{chart_id}"
         data-left="{plot_left}" data-right="{plot_right}" data-n="{n}">
      {"".join(svg_parts)}
      <line class="crosshair" x1="0" y1="{plot_top}" x2="0" y2="{plot_bottom}" style="display:none"/>
      <rect class="hover-rect" x="{plot_left}" y="{plot_top}" width="{plot_right - plot_left}" height="{plot_bottom - plot_top}" fill="transparent"/>
    </svg>
    <div class="tooltip" style="display:none"></div>
  </div>
</div>
<script type="application/json" id="{chart_id}-tooltips">{json.dumps(tooltips)}</script>
"""


def _data_table(rows: list, suite: str) -> str:
    head = "".join(
        f"<th>{MODE_LABELS[m]} Ir</th><th>{MODE_LABELS[m]} mean</th><th>{MODE_LABELS[m]} p95</th><th>{MODE_LABELS[m]} p99</th>"
        for m in MODES
    )
    body = []
    for i, row in enumerate(rows):
        cells = []
        for mode in MODES:
            p = row.points[mode][suite]
            if p is None or p.status != "ok":
                cells.append("<td>n/a</td><td>n/a</td><td>n/a</td><td>n/a</td>")
            else:
                cells.append(
                    f"<td>{_fmt_ir(p.ir)}</td><td>{_fmt_seconds(p.mean)}</td>"
                    f"<td>{_fmt_seconds(p.p95)}</td><td>{_fmt_seconds(p.p99)}</td>"
                )
        body.append(
            f"<tr><td>{i}</td><td>{row.author_date[:10]}</td><td>{row.sha[:10]}</td>{''.join(cells)}</tr>"
        )
    return f"""
<details class="data-table">
  <summary>Show data table ({suite})</summary>
  <div class="table-scroll">
    <table>
      <thead><tr><th>#</th><th>date</th><th>commit</th>{head}</tr></thead>
      <tbody>{"".join(body)}</tbody>
    </table>
  </div>
</details>
"""


PAGE_CSS = """
:root {
  --surface-1: #fcfcfb; --page: #f9f9f7; --text-primary: #0b0b0b;
  --text-secondary: #52514e; --text-muted: #898781; --gridline: #e1e0d9;
  --baseline: #c3c2b7; --series-python: #2a78d6; --series-rust_legacy: #1baf7a;
  --series-rust_native_ast: #eda100;
}
@media (prefers-color-scheme: dark) {
  :root {
    --surface-1: #1a1a19; --page: #0d0d0d; --text-primary: #ffffff;
    --text-secondary: #c3c2b7; --text-muted: #898781; --gridline: #2c2c2a;
    --baseline: #383835; --series-python: #3987e5; --series-rust_legacy: #199e70;
    --series-rust_native_ast: #c98500;
  }
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--page); color: var(--text-primary);
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif; }
main { max-width: 1080px; margin: 0 auto; padding: 24px 16px 64px; }
h1 { font-size: 1.3rem; margin: 0 0 4px; }
.subtitle { color: var(--text-secondary); margin: 0 0 24px; font-size: 0.9rem; }
h2 { font-size: 1rem; color: var(--text-primary); margin: 32px 0 8px; }
.legend { display: flex; gap: 16px; margin: 8px 0 4px; flex-wrap: wrap; }
.legend-item { display: flex; align-items: center; gap: 6px; font-size: 0.85rem; color: var(--text-secondary); }
.legend-item i { width: 12px; height: 2px; display: inline-block; }
.chart-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
@media (max-width: 720px) { .chart-grid { grid-template-columns: 1fr; } }
.chart-block { background: var(--surface-1); border: 1px solid var(--gridline); border-radius: 8px; padding: 12px; }
.chart-title { font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 4px; }
.chart-wrap { position: relative; }
.chart-svg { width: 100%; height: auto; overflow: visible; }
.gridline { stroke: var(--gridline); stroke-width: 1; }
.axis-label { fill: var(--text-muted); font-size: 9px; }
.end-label { fill: var(--text-primary); font-size: 10px; }
.crosshair { stroke: var(--baseline); stroke-width: 1; pointer-events: none; }
.hover-rect { cursor: crosshair; }
.tooltip { position: absolute; pointer-events: none; background: var(--surface-1);
  border: 1px solid var(--gridline); border-radius: 6px; padding: 6px 8px; font-size: 0.78rem;
  color: var(--text-primary); box-shadow: 0 2px 8px rgba(0,0,0,0.15); white-space: nowrap; z-index: 2; }
.tt-row { display: flex; align-items: center; gap: 4px; }
.tt-row i { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.chart-empty { color: var(--text-muted); font-size: 0.85rem; padding: 24px; text-align: center; }
.data-table { margin: 12px 0 0; font-size: 0.8rem; color: var(--text-secondary); }
.data-table summary { cursor: pointer; }
.table-scroll { overflow-x: auto; margin-top: 8px; }
table { border-collapse: collapse; width: 100%; font-variant-numeric: tabular-nums; }
th, td { padding: 4px 8px; text-align: right; border-bottom: 1px solid var(--gridline); white-space: nowrap; }
th:nth-child(1), td:nth-child(1), th:nth-child(2), td:nth-child(2), th:nth-child(3), td:nth-child(3) { text-align: left; }
"""

PAGE_JS = """
document.querySelectorAll('.chart-svg').forEach(function (svg) {
  var id = svg.id;
  var tooltipsEl = document.getElementById(id + '-tooltips');
  if (!tooltipsEl) return;
  var tooltips = JSON.parse(tooltipsEl.textContent);
  var left = parseFloat(svg.dataset.left), right = parseFloat(svg.dataset.right), n = parseInt(svg.dataset.n, 10);
  var crosshair = svg.querySelector('.crosshair');
  var hoverRect = svg.querySelector('.hover-rect');
  var wrap = svg.closest('.chart-wrap');
  var tooltip = wrap.querySelector('.tooltip');

  function indexFromClientX(clientX) {
    var rect = svg.getBoundingClientRect();
    var scale = rect.width / svg.viewBox.baseVal.width;
    var svgX = (clientX - rect.left) / scale;
    if (n <= 1) return 0;
    var frac = (svgX - left) / (right - left);
    var idx = Math.round(frac * (n - 1));
    return Math.max(0, Math.min(n - 1, idx));
  }

  hoverRect.addEventListener('mousemove', function (evt) {
    var idx = indexFromClientX(evt.clientX);
    var x = n > 1 ? left + (idx * (right - left) / (n - 1)) : (left + right) / 2;
    crosshair.setAttribute('x1', x);
    crosshair.setAttribute('x2', x);
    crosshair.style.display = 'block';
    tooltip.innerHTML = tooltips[idx];
    tooltip.style.display = 'block';
    var rect = svg.getBoundingClientRect();
    var scale = rect.width / svg.viewBox.baseVal.width;
    tooltip.style.left = Math.min(x * scale + 12, rect.width - 160) + 'px';
    tooltip.style.top = '4px';
  });
  hoverRect.addEventListener('mouseleave', function () {
    crosshair.style.display = 'none';
    tooltip.style.display = 'none';
  });
});
"""


def build_html(rows: list) -> str:
    """Render the full self-contained trend.html page for rows."""
    legend = "".join(
        f'<div class="legend-item"><i style="background:var(--series-{m})"></i>{MODE_LABELS[m]}</div>'
        for m in MODES
    )
    sections = []
    for suite in SUITES:
        ir_chart = _build_chart(
            f"ir-{suite}",
            f"callgrind Ir - {suite}",
            rows,
            lambda r, m, s=suite: (
                r.points[m][s].ir
                if r.points[m][s] and r.points[m][s].status == "ok"
                else None
            ),
            lambda v: f"{v / 1e6:.1f}M" if v >= 1e6 else f"{v:,.0f}",
        )
        wt_chart = _build_chart(
            f"wt-{suite}",
            f"walltime mean - {suite}",
            rows,
            lambda r, m, s=suite: (
                r.points[m][s].mean
                if r.points[m][s] and r.points[m][s].status == "ok"
                else None
            ),
            lambda v: f"{v:.3f}s",
        )
        sections.append(f"""
<h2>{suite}</h2>
<div class="legend">{legend}</div>
<div class="chart-grid">{ir_chart}{wt_chart}</div>
{_data_table(rows, suite)}
""")

    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<title>perf_sweep trend</title>
<style>{PAGE_CSS}</style>
</head>
<body>
<main>
  <h1>perf_sweep trend</h1>
  <p class="subtitle">{len(rows)} measured commits, {SUITES[0]}/{SUITES[1]}, 3 parser modes.</p>
  {"".join(sections)}
</main>
<script>{PAGE_JS}</script>
</body>
</html>"""


def main(argv=None) -> int:
    """Load rows from --output, print the terminal report, write the HTML chart."""
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument(
        "--output",
        type=Path,
        default=Path("bench-results"),
        help="perf_sweep output directory",
    )
    p.add_argument(
        "--repo",
        type=Path,
        default=Path("."),
        help="Path to the sqlfluff git repo, used to order commits by ancestry",
    )
    p.add_argument(
        "--html",
        type=Path,
        default=None,
        help="Where to write the HTML chart (default: <output>/trend.html)",
    )
    p.add_argument(
        "--no-html",
        action="store_true",
        help="Skip writing the HTML chart, terminal report only",
    )
    args = p.parse_args(argv)

    output_dir = args.output.resolve()
    rows = load_rows(output_dir, args.repo.resolve())
    if not rows:
        print(f"No measured commits found under {output_dir}.")
        return 1

    print(render_terminal_report(rows))

    if not args.no_html:
        html_path = args.html.resolve() if args.html else output_dir / "trend.html"
        html_path.write_text(build_html(rows), encoding="utf-8")
        print(f"Wrote {html_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

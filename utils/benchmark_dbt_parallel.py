#!/usr/bin/env python3
"""Benchmark SQLFluff parallel linting with the dbt templater.

Generates a synthetic dbt project with configurable model count and
measures wall-clock time across different --processes values to quantify
the impact of parallel vs sequential templating.

Usage:
    # Quick test (50 models, processes 1 and 4)
    python utils/benchmark_dbt_parallel.py --models 50 --processes 1,4

    # Full benchmark
    python utils/benchmark_dbt_parallel.py --models 200 --processes 1,2,4,8

    # Compare standard vs warm worker pool performance
    python utils/benchmark_dbt_parallel.py --models 200 --processes 1,4,8 --compare

    # Test fix mode: inject violations, fix them, verify
    python utils/benchmark_dbt_parallel.py --processes 1,8 --violation-pct 50 --fix

    # Export results as CSV for regression tracking
    python utils/benchmark_dbt_parallel.py --processes 1,4,8 --reuse-linter --csv results.csv

    # Reuse a previously generated project
    python utils/benchmark_dbt_parallel.py --project-dir /tmp/bench_dbt --no-clean

    # Use an existing real dbt project
    python utils/benchmark_dbt_parallel.py --project-dir /path/to/dbt/project \
        --profiles-dir /path/to/profiles --skip-generate

Requirements:
    pip install sqlfluff sqlfluff-templater-dbt dbt-duckdb
"""

import argparse
import csv
import os
import platform
import random
import shutil
import statistics
import subprocess
import sys
import tempfile
import textwrap
import time
from pathlib import Path
from typing import Optional

from sqlfluff.core import FluffConfig, Linter

_PROFILES_YML = textwrap.dedent("""\
    benchmark:
      target: dev
      outputs:
        dev:
          type: duckdb
          path: ':memory:'
          threads: 1
""")

_DBT_PROJECT_YML = textwrap.dedent("""\
    name: benchmark_project
    version: '1.0.0'
    config-version: 2
    profile: benchmark

    model-paths: ["models"]
    macro-paths: ["macros"]
    target-path: "target"
    clean-targets: ["target"]

    vars:
      benchmark_date: '2024-01-01'
      apply_filter: false
""")

_SQLFLUFF_CFG = textwrap.dedent("""\
    [sqlfluff]
    templater = dbt
    dialect = duckdb
    rules = LT01, LT02, LT04, LT09, CP01, CP02

    [sqlfluff:templater:dbt]
    project_dir = {project_dir}
    profiles_dir = {profiles_dir}
""")

_SOURCES_YML = """\
version: 2
sources:
  - name: raw
    schema: main
    tables:
{tables}
"""

_CUSTOM_MACROS_SQL = textwrap.dedent("""\
    {% macro safe_divide(numerator, denominator) %}
        CASE
            WHEN {{ denominator }} = 0 THEN NULL
            ELSE {{ numerator }} / {{ denominator }}
        END
    {% endmacro %}

    {% macro generate_surrogate_key(field_list) %}
        MD5(CONCAT(
            {%- for field in field_list %}
            COALESCE(CAST({{ field }} AS VARCHAR), '_null_')
            {%- if not loop.last %}, '|',{% endif %}
            {%- endfor %}
        ))
    {% endmacro %}

    {% macro cents_to_dollars(column_name) %}
        ROUND(CAST({{ column_name }} AS DECIMAL(18, 2)) / 100, 2)
    {% endmacro %}
""")


def _staging_model(idx: int) -> str:
    cols = [
        f"    id_{idx} AS id",
        f"    'name_{idx}' AS name",
        "    CURRENT_TIMESTAMP AS created_at",
        f"    {random.randint(100, 99999)} AS amount",
        f"    {random.randint(1, 100)} AS quantity",
        f"    'category_{random.randint(1, 20)}' AS category",
    ]
    return textwrap.dedent(f"""\
        {{{{ config(materialized='view') }}}}

        SELECT
        {("," + chr(10)).join(cols)}
        FROM (SELECT {idx} AS id_{idx})
    """)


def _intermediate_model(idx: int, stg_count: int) -> str:
    ref_a = random.randint(0, stg_count - 1)
    ref_b = random.randint(0, stg_count - 1)
    while ref_b == ref_a and stg_count > 1:
        ref_b = random.randint(0, stg_count - 1)
    return textwrap.dedent(f"""\
        {{{{ config(materialized='table') }}}}

        WITH base AS (
            SELECT * FROM {{{{ ref('stg_{ref_a:04d}') }}}}
        ),

        joined AS (
            SELECT
                base.id,
                base.name,
                base.amount,
                secondary.category AS secondary_category,
                base.amount * base.quantity AS total_value,
                {{{{ safe_divide('base.amount', 'base.quantity') }}}} AS unit_price
            FROM base
            LEFT JOIN {{{{ ref('stg_{ref_b:04d}') }}}} AS secondary
                ON base.id = secondary.id
            {{% if var('apply_filter', false) %}}
            WHERE base.amount > 0
            {{% endif %}}
        )

        SELECT
            *,
            '{{{{ var("benchmark_date") }}}}' AS snapshot_date
        FROM joined
    """)


def _mart_model(idx: int, int_count: int) -> str:
    num_sources = min(random.randint(2, 4), int_count)
    refs = random.sample(range(int_count), num_sources)
    cte_parts = []
    for i, ref_idx in enumerate(refs):
        cte_parts.append(
            textwrap.dedent(f"""\
            source_{i} AS (
                SELECT
                    id,
                    name,
                    amount,
                    total_value
                FROM {{{{ ref('int_{ref_idx:04d}') }}}}
            )""")
        )

    ctes = ",\n\n".join(cte_parts)
    unions = "\n    UNION ALL\n".join(
        f"    SELECT * FROM source_{i}" for i in range(num_sources)
    )

    return textwrap.dedent(f"""\
        {{{{ config(materialized='table', tags=['marts']) }}}}

        WITH
        {ctes},

        combined AS (
        {unions}
        )

        SELECT
            id,
            name,
            COUNT(*) AS record_count,
            SUM(amount) AS total_amount,
            AVG(amount) AS avg_amount,
            MAX(total_value) AS max_total_value,
            {{{{ cents_to_dollars('SUM(amount)') }}}} AS total_dollars
        FROM combined
        GROUP BY id, name
    """)


def _ephemeral_model(idx: int, stg_count: int) -> str:
    ref_idx = random.randint(0, stg_count - 1)
    return textwrap.dedent(f"""\
        {{{{ config(materialized='ephemeral') }}}}

        SELECT
            *,
            CURRENT_TIMESTAMP AS processed_at,
            'batch_{idx}' AS batch_id
        FROM {{{{ ref('stg_{ref_idx:04d}') }}}}
        WHERE amount > 0
    """)


def generate_dbt_project(
    target_dir: str, model_count: int = 200, violation_pct: int = 0
) -> Path:
    """Generate a synthetic dbt project for benchmarking.

    Args:
        target_dir: Directory to create the project in.
        model_count: Total number of models to generate (minimum 4, one per tier).
        violation_pct: Percentage of models to inject fixable violations into
            (0-100). Violations are CP01 (lowercase keywords).

    Returns:
        Path to the project root.
    """
    project = Path(target_dir)

    # Enforce minimum of 4 models (one per tier)
    model_count = max(model_count, 4)

    # Tier distribution
    n_staging = max(int(model_count * 0.40), 1)
    n_intermediate = max(int(model_count * 0.30), 1)
    n_marts = max(int(model_count * 0.20), 1)
    n_ephemeral = max(model_count - n_staging - n_intermediate - n_marts, 1)

    # Create directories
    for subdir in [
        "models/staging",
        "models/intermediate",
        "models/marts",
        "models/ephemeral",
        "macros",
        "profiles_yml",
    ]:
        (project / subdir).mkdir(parents=True, exist_ok=True)

    # Write configs
    (project / "dbt_project.yml").write_text(_DBT_PROJECT_YML)
    (project / "profiles_yml" / "profiles.yml").write_text(_PROFILES_YML)
    (project / "macros" / "custom_macros.sql").write_text(_CUSTOM_MACROS_SQL)

    # Write .sqlfluff
    profiles_dir = (project / "profiles_yml").as_posix()
    project_str = project.as_posix()
    (project / ".sqlfluff").write_text(
        _SQLFLUFF_CFG.format(project_dir=project_str, profiles_dir=profiles_dir)
    )

    # Write sources.yml
    tables = "\n".join(f"      - name: table_{i:04d}" for i in range(n_staging))
    (project / "models" / "staging" / "sources.yml").write_text(
        _SOURCES_YML.format(tables=tables)
    )

    # Seed the random number generator for reproducibility
    random.seed(42)

    # Generate staging models
    for i in range(n_staging):
        (project / "models" / "staging" / f"stg_{i:04d}.sql").write_text(
            _staging_model(i)
        )

    # Generate intermediate models
    for i in range(n_intermediate):
        (project / "models" / "intermediate" / f"int_{i:04d}.sql").write_text(
            _intermediate_model(i, n_staging)
        )

    # Generate mart models
    for i in range(n_marts):
        (project / "models" / "marts" / f"mart_{i:04d}.sql").write_text(
            _mart_model(i, n_intermediate)
        )

    # Generate ephemeral models
    for i in range(n_ephemeral):
        (project / "models" / "ephemeral" / f"eph_{i:04d}.sql").write_text(
            _ephemeral_model(i, n_staging)
        )

    total = n_staging + n_intermediate + n_marts + n_ephemeral

    # Inject fixable violations (CP01: lowercase keywords) into a
    # percentage of models to simulate real-world fix workloads.
    n_violations = 0
    if violation_pct > 0:
        all_models = sorted((project / "models").rglob("*.sql"))
        n_to_break = max(1, int(len(all_models) * violation_pct / 100))
        targets = random.sample(all_models, min(n_to_break, len(all_models)))
        for model_path in targets:
            content = model_path.read_text()
            # Lowercase FROM/WHERE while keeping SELECT uppercase to
            # create CP01 (inconsistent capitalisation) violations.
            broken = content.replace("FROM", "from").replace("WHERE", "where")
            if broken != content:
                model_path.write_text(broken)
                n_violations += 1

    msg = (
        f"Generated {total} models: "
        f"{n_staging} staging, {n_intermediate} intermediate, "
        f"{n_marts} marts, {n_ephemeral} ephemeral"
    )
    if n_violations:
        msg += f" ({n_violations} with injected violations)"
    print(msg)
    return project


def _find_dbt_executable() -> str:
    """Locate the dbt CLI in the current venv or on PATH."""
    venv_bin = Path(sys.executable).parent
    dbt_exe = venv_bin / ("dbt.exe" if sys.platform == "win32" else "dbt")
    if dbt_exe.exists():
        return str(dbt_exe)
    found = shutil.which("dbt")
    if found:
        return found
    print("Error: dbt CLI not found. Ensure dbt-core is installed.", file=sys.stderr)
    sys.exit(1)


def compile_dbt_project(project_dir: Path, profiles_dir: Path) -> None:
    """Run dbt compile to pre-warm the manifest and partial parse cache."""
    env = os.environ.copy()
    env["DBT_SEND_ANONYMOUS_USAGE_STATS"] = "false"
    dbt_exe = _find_dbt_executable()

    print("Running dbt compile (pre-warming manifest)...")
    t0 = time.perf_counter()
    result = subprocess.run(
        [
            dbt_exe,
            "compile",
            "--project-dir",
            str(project_dir),
            "--profiles-dir",
            str(profiles_dir),
        ],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(project_dir),
    )
    elapsed = time.perf_counter() - t0

    if result.returncode != 0:
        print(f"Error: dbt compile failed (exit {result.returncode}):", file=sys.stderr)
        print(
            result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr,
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"dbt compile completed in {elapsed:.1f}s")


def _get_peak_memory_mb() -> float:
    """Get peak memory usage of the current process in MB."""
    if platform.system() == "Windows":
        import ctypes
        from ctypes import wintypes

        class _PMC(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        pmc = _PMC()
        pmc.cb = ctypes.sizeof(_PMC)
        get_process = ctypes.windll.kernel32.GetCurrentProcess
        get_process.restype = wintypes.HANDLE
        k32_mem = ctypes.windll.kernel32.K32GetProcessMemoryInfo
        k32_mem.argtypes = [
            wintypes.HANDLE,
            ctypes.POINTER(_PMC),
            wintypes.DWORD,
        ]
        k32_mem.restype = wintypes.BOOL
        if k32_mem(get_process(), ctypes.byref(pmc), pmc.cb):
            return pmc.PeakWorkingSetSize / (1024 * 1024)
        return 0.0
    else:
        import resource

        # ru_maxrss is in KB on Linux, bytes on macOS
        rusage = resource.getrusage(resource.RUSAGE_SELF)
        if platform.system() == "Darwin":
            return rusage.ru_maxrss / (1024 * 1024)
        return rusage.ru_maxrss / 1024


def run_benchmark(
    project_dir: Path,
    profiles_dir: Path,
    process_counts: list[int],
    iterations: int = 3,
    warmup: int = 1,
    reuse_linter: bool = False,
    mode: str = "standard",
) -> list[dict]:
    """Run sqlfluff lint with different process counts and measure timings.

    Args:
        project_dir: Path to the dbt project directory.
        profiles_dir: Path to the directory containing profiles.yml.
        process_counts: List of process counts to benchmark.
        iterations: Number of timed iterations per process count.
        warmup: Number of warmup iterations to discard.
        reuse_linter: When True, reuse the same Linter instance across
            iterations for each process count. This enables persistent
            warm worker pools (workers stay alive with dbt imported and
            adapter registered). Measures steady-state performance.
        mode: Label for the benchmark mode (e.g. "standard", "warm").

    Returns:
        List of result dicts with keys: mode, processes, iteration,
        wall_clock, files, violations, phase.
    """
    models_dir = str(project_dir / "models")
    results = []

    for n_procs in process_counts:
        mode_label = "persistent pool" if reuse_linter and n_procs > 1 else "standard"
        print(f"\n--- Benchmarking with --processes {n_procs} ({mode_label}) ---")

        config = FluffConfig(
            overrides={
                "templater": "dbt",
                "dialect": "duckdb",
            },
            configs={
                "templater": {
                    "dbt": {
                        "project_dir": str(project_dir),
                        "profiles_dir": str(profiles_dir),
                    }
                }
            },
        )

        # In reuse mode, create linter once and reuse across all iterations.
        # This allows persistent warm worker pools.
        linter = Linter(config=config) if reuse_linter else None

        for i in range(warmup + iterations):
            is_warmup = i < warmup
            label = (
                f"warmup {i + 1}/{warmup}"
                if is_warmup
                else (f"iter {i - warmup + 1}/{iterations}")
            )

            if not reuse_linter:
                config = FluffConfig(
                    overrides={
                        "templater": "dbt",
                        "dialect": "duckdb",
                    },
                    configs={
                        "templater": {
                            "dbt": {
                                "project_dir": str(project_dir),
                                "profiles_dir": str(profiles_dir),
                            }
                        }
                    },
                )
                linter = Linter(config=config)

            t0 = time.perf_counter()
            result = linter.lint_paths(
                (models_dir,),
                processes=n_procs,
                # retain_files=True so num_violations() works correctly.
                retain_files=True,
            )
            wall_clock = time.perf_counter() - t0
            peak_mem = _get_peak_memory_mb()

            n_files = sum(p.stats()["files"] for p in result.paths)
            n_violations = result.num_violations()

            phase = "cold" if (reuse_linter and i == 0) else "warm"

            if is_warmup:
                print(
                    f"  {label}: {wall_clock:.1f}s "
                    f"({n_files} files, {n_violations} violations, "
                    f"{peak_mem:.0f}MB) [{phase}, discarded]"
                )
            else:
                print(
                    f"  {label}: {wall_clock:.1f}s "
                    f"({n_files} files, {n_violations} violations, "
                    f"{peak_mem:.0f}MB) [{phase}]"
                )
                results.append(
                    {
                        "mode": mode,
                        "processes": n_procs,
                        "iteration": i - warmup + 1,
                        "wall_clock": wall_clock,
                        "files": n_files,
                        "violations": n_violations,
                        "peak_memory_mb": round(peak_mem, 1),
                        "phase": phase,
                    }
                )

    return results


def run_fix_benchmark(
    project_dir: Path,
    profiles_dir: Path,
    process_counts: list[int],
    reuse_linter: bool = False,
) -> None:
    """Run sqlfluff fix, then verify by re-linting.

    For each process count: fix all files, then re-lint to confirm
    violations are resolved. Restores original files between iterations.
    """
    models_dir = project_dir / "models"

    # Save original file contents for restoration after each fix.
    originals: dict[Path, str] = {}
    for sql_file in models_dir.rglob("*.sql"):
        originals[sql_file] = sql_file.read_text()

    def _restore() -> None:
        for path, content in originals.items():
            path.write_text(content)

    for n_procs in process_counts:
        mode_label = "persistent pool" if reuse_linter and n_procs > 1 else "standard"
        print(f"\n--- Fix mode with --processes {n_procs} ({mode_label}) ---")

        config = FluffConfig(
            overrides={"templater": "dbt", "dialect": "duckdb"},
            configs={
                "templater": {
                    "dbt": {
                        "project_dir": str(project_dir),
                        "profiles_dir": str(profiles_dir),
                    }
                }
            },
        )
        linter = Linter(config=config)

        # Restore originals before fixing.
        _restore()

        # Step 1: Lint to count violations before fixing.
        pre_result = linter.lint_paths(
            (str(models_dir),), processes=n_procs, retain_files=True
        )
        violations_before = pre_result.num_violations()
        fixable = pre_result.num_violations(fixable=True)
        print(f"  pre-fix:  {violations_before} violations ({fixable} fixable)")

        # Step 2: Fix in a loop until no violations remain or no
        # progress is made. Each pass may resolve cascading violations.
        _restore()
        max_passes = 10
        total_fix_time = 0.0
        pass_num = 0
        remaining = violations_before

        for pass_num in range(1, max_passes + 1):
            fix_linter = Linter(config=config)
            t0 = time.perf_counter()
            fix_result = fix_linter.lint_paths(
                (str(models_dir),),
                processes=n_procs,
                fix=True,
                apply_fixes=True,
                retain_files=True,
            )
            pass_time = time.perf_counter() - t0
            total_fix_time += pass_time
            fixed_count = fix_result.num_violations(fixable=True)

            # Re-lint to count remaining violations.
            verify_linter = Linter(config=config)
            verify_result = verify_linter.lint_paths(
                (str(models_dir),), processes=n_procs, retain_files=True
            )
            new_remaining = verify_result.num_violations()

            print(
                f"  pass {pass_num}:   {pass_time:.1f}s "
                f"({fixed_count} fixed, {new_remaining} remaining)"
            )

            if new_remaining == 0:
                remaining = 0
                break
            if new_remaining >= remaining:
                # No progress — remaining violations are unfixable.
                remaining = new_remaining
                break
            remaining = new_remaining

        resolved = violations_before - remaining
        print(
            f"  total:    {total_fix_time:.1f}s over {pass_num} passes, "
            f"{resolved}/{violations_before} resolved"
        )
        if remaining == 0:
            print("  result:   PASS — all violations resolved")
        else:
            print(f"  result:   {remaining} unfixable violations remain")

    # Restore originals at the end.
    _restore()


def print_results(results: list[dict]) -> None:
    """Print a summary table of benchmark results with efficiency stats."""
    by_procs: dict[int, list[float]] = {}
    for r in results:
        by_procs.setdefault(r["processes"], []).append(r["wall_clock"])

    print("\n" + "=" * 78)
    print("  dbt Parallel Templating Benchmark Results")
    print("=" * 78)

    baseline: Optional[float] = None
    print(
        f"\n{'Processes':>10} | {'Mean (s)':>10} | {'Std (s)':>10} | "
        f"{'Min (s)':>10} | {'Speedup':>8} | {'Efficiency':>10}"
    )
    print("-" * 78)

    for n_procs in sorted(by_procs.keys()):
        times = by_procs[n_procs]
        mean_t = statistics.mean(times)
        min_t = min(times)
        std_t = statistics.stdev(times) if len(times) > 1 else 0.0

        if baseline is None:
            baseline = mean_t

        speedup = baseline / mean_t if mean_t > 0 else 0
        efficiency = (baseline / (mean_t * n_procs)) * 100 if mean_t > 0 else 0
        print(
            f"{n_procs:>10} | {mean_t:>10.1f} | {std_t:>10.2f} | "
            f"{min_t:>10.1f} | {speedup:>7.2f}x | {efficiency:>9.0f}%"
        )

    print()
    if baseline and len(by_procs) > 1:
        max_procs = max(by_procs.keys())
        max_speedup = baseline / statistics.mean(by_procs[max_procs])
        print(
            f"  With {max_procs} processes: {max_speedup:.2f}x actual speedup "
            f"(theoretical max: {max_procs:.1f}x)"
        )
    print()


def print_comparison(standard_results: list[dict], warm_results: list[dict]) -> None:
    """Print a side-by-side comparison of standard vs warm worker results."""
    std_by_procs: dict[int, list[float]] = {}
    for r in standard_results:
        std_by_procs.setdefault(r["processes"], []).append(r["wall_clock"])

    warm_by_procs: dict[int, list[float]] = {}
    for r in warm_results:
        warm_by_procs.setdefault(r["processes"], []).append(r["wall_clock"])

    all_procs = sorted(set(std_by_procs) | set(warm_by_procs))

    # Baseline from sequential run (either mode).
    baseline: Optional[float] = None
    for n in all_procs:
        if n == 1:
            times = std_by_procs.get(n) or warm_by_procs.get(n, [])
            if times:
                baseline = statistics.mean(times)
            break

    print("\n" + "=" * 85)
    print("  Comparison: Standard vs Persistent Warm Pool")
    print("=" * 85)
    print(
        f"\n{'Processes':>10} | {'Standard (s)':>12} | {'Std Eff':>8} | "
        f"{'Warm (s)':>12} | {'Warm Eff':>9} | {'Warm Gain':>10}"
    )
    print("-" * 85)

    for n_procs in all_procs:
        std_mean = (
            statistics.mean(std_by_procs[n_procs]) if n_procs in std_by_procs else None
        )
        warm_mean = (
            statistics.mean(warm_by_procs[n_procs])
            if n_procs in warm_by_procs
            else None
        )

        std_str = f"{std_mean:>12.1f}" if std_mean else f"{'—':>12}"
        warm_str = f"{warm_mean:>12.1f}" if warm_mean else f"{'—':>12}"

        if baseline and std_mean:
            std_eff_str = f"{(baseline / (std_mean * n_procs)) * 100:>8.0f}%"
        else:
            std_eff_str = f"{'—':>9}"

        if baseline and warm_mean:
            warm_eff_str = f"{(baseline / (warm_mean * n_procs)) * 100:>8.0f}%"
        else:
            warm_eff_str = f"{'—':>9}"

        if std_mean and warm_mean:
            gain_str = f"{std_mean / warm_mean:>9.2f}x"
        else:
            gain_str = f"{'—':>10}"

        print(
            f"{n_procs:>10} | {std_str} | {std_eff_str} | "
            f"{warm_str} | {warm_eff_str} | {gain_str}"
        )

    print()


def write_csv(results: list[dict], output_path: Optional[str] = None) -> None:
    """Write benchmark results to CSV (file or stdout)."""
    fieldnames = [
        "mode",
        "processes",
        "iteration",
        "wall_clock",
        "files",
        "violations",
        "peak_memory_mb",
        "phase",
    ]

    if output_path:
        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"\nCSV results written to {output_path}")
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def main():
    """Run the dbt parallel templating benchmark."""
    parser = argparse.ArgumentParser(
        description="Benchmark SQLFluff parallel linting with dbt templater",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--models",
        type=int,
        default=200,
        help="Number of models to generate (default: 200)",
    )
    parser.add_argument(
        "--processes",
        type=str,
        default="1,4",
        help="Comma-separated list of process counts to test (default: 1,4)",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=3,
        help="Number of timed iterations per process count (default: 3)",
    )
    parser.add_argument(
        "--warmup",
        type=int,
        default=1,
        help="Number of warmup iterations to discard (default: 1)",
    )
    parser.add_argument(
        "--project-dir",
        type=str,
        default=None,
        help="Directory for the dbt project (default: temp directory)",
    )
    parser.add_argument(
        "--profiles-dir",
        type=str,
        default=None,
        help="Directory containing profiles.yml (default: generated inside project)",
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Don't delete the project directory after benchmarking",
    )
    parser.add_argument(
        "--skip-generate",
        action="store_true",
        help="Skip project generation (use with --project-dir for existing projects)",
    )
    parser.add_argument(
        "--skip-compile",
        action="store_true",
        help="Skip dbt compile (reuse existing target/)",
    )
    parser.add_argument(
        "--reuse-linter",
        action="store_true",
        help="Reuse the same Linter across iterations (enables persistent warm "
        "worker pools). Measures steady-state performance with amortized "
        "pool initialization.",
    )
    parser.add_argument(
        "--violation-pct",
        type=int,
        default=0,
        metavar="PCT",
        help="Percentage of models to inject fixable violations into "
        "(0-100, default: 0). Useful for benchmarking --fix mode.",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Run fix mode: apply fixes then re-lint to verify. "
        "Original files are restored after each run. "
        "Best used with --violation-pct to inject fixable violations.",
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Run both standard and warm worker modes and show a side-by-side "
        "comparison with warm gain and efficiency metrics.",
    )
    parser.add_argument(
        "--csv",
        type=str,
        nargs="?",
        const="-",
        default=None,
        metavar="FILE",
        help="Output results as CSV. Writes to FILE if given, stdout if "
        "flag used without a path.",
    )
    args = parser.parse_args()

    process_counts = [int(x.strip()) for x in args.processes.split(",")]
    if any(c < 1 for c in process_counts):
        print("Error: --processes values must be positive integers.", file=sys.stderr)
        sys.exit(1)

    # Only require dbt-duckdb when generating a synthetic project
    if not args.skip_generate:
        try:
            import dbt.adapters.duckdb  # noqa: F401
        except Exception as e:
            print(
                f"Error: dbt-duckdb is required but failed to import: {e}\n"
                "Install with: pip install dbt-duckdb",
                file=sys.stderr,
            )
            sys.exit(1)

    # Determine project directory
    tmpdir = None
    if args.project_dir:
        project_dir = Path(args.project_dir)
        if args.skip_generate:
            if not project_dir.exists():
                print(
                    f"Error: --project-dir {project_dir} does not exist "
                    "(required with --skip-generate).",
                    file=sys.stderr,
                )
                sys.exit(1)
        else:
            project_dir.mkdir(parents=True, exist_ok=True)
    else:
        tmpdir = tempfile.mkdtemp(prefix="sqlfluff_bench_dbt_")
        project_dir = Path(tmpdir)

    try:
        # Generate project
        if not args.skip_generate:
            generate_dbt_project(
                str(project_dir),
                model_count=args.models,
                violation_pct=args.violation_pct,
            )

        if args.profiles_dir:
            profiles_dir = Path(args.profiles_dir)
            if not profiles_dir.exists():
                print(
                    f"Error: --profiles-dir {profiles_dir} does not exist.",
                    file=sys.stderr,
                )
                sys.exit(1)
        else:
            profiles_dir = project_dir / "profiles_yml"

        # Compile dbt project
        if not args.skip_compile:
            compile_dbt_project(project_dir, profiles_dir)

        # Run benchmarks
        if args.fix:
            run_fix_benchmark(
                project_dir=project_dir,
                profiles_dir=profiles_dir,
                process_counts=process_counts,
                reuse_linter=args.reuse_linter,
            )
            all_results = []
        elif args.compare:
            print("\n*** Running standard mode (no persistent pool) ***")
            standard_results = run_benchmark(
                project_dir=project_dir,
                profiles_dir=profiles_dir,
                process_counts=process_counts,
                iterations=args.iterations,
                warmup=args.warmup,
                reuse_linter=False,
                mode="standard",
            )

            print("\n*** Running warm worker mode (persistent pool) ***")
            warm_results = run_benchmark(
                project_dir=project_dir,
                profiles_dir=profiles_dir,
                process_counts=process_counts,
                iterations=args.iterations,
                warmup=args.warmup,
                reuse_linter=True,
                mode="warm",
            )

            print_comparison(standard_results, warm_results)
            all_results = standard_results + warm_results
        else:
            mode = "warm" if args.reuse_linter else "standard"
            all_results = run_benchmark(
                project_dir=project_dir,
                profiles_dir=profiles_dir,
                process_counts=process_counts,
                iterations=args.iterations,
                warmup=args.warmup,
                reuse_linter=args.reuse_linter,
                mode=mode,
            )
            print_results(all_results)

        # CSV output
        if args.csv is not None:
            csv_path = None if args.csv == "-" else args.csv
            write_csv(all_results, csv_path)

    finally:
        if tmpdir and not args.no_clean:
            print(f"Cleaning up {tmpdir}")
            shutil.rmtree(tmpdir, ignore_errors=True)
        elif tmpdir:
            print(f"Project kept at: {tmpdir}")


if __name__ == "__main__":
    main()

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

    # Reuse a previously generated project
    python utils/benchmark_dbt_parallel.py --project-dir /tmp/bench_dbt --no-clean

    # Use an existing real dbt project
    python utils/benchmark_dbt_parallel.py --project-dir /path/to/dbt/project \
        --profiles-dir /path/to/profiles --skip-generate

Requirements:
    pip install sqlfluff sqlfluff-templater-dbt dbt-duckdb
"""

import argparse
import os
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


def _mart_model(idx: int, int_count: int, int_offset: int) -> str:
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


def generate_dbt_project(target_dir: str, model_count: int = 200) -> Path:
    """Generate a synthetic dbt project for benchmarking.

    Args:
        target_dir: Directory to create the project in.
        model_count: Total number of models to generate.

    Returns:
        Path to the project root.
    """
    project = Path(target_dir)

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
    profiles_dir = str(project / "profiles_yml").replace("\\", "/")
    project_str = str(project).replace("\\", "/")
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
            _mart_model(i, n_intermediate, 0)
        )

    # Generate ephemeral models
    for i in range(n_ephemeral):
        (project / "models" / "ephemeral" / f"eph_{i:04d}.sql").write_text(
            _ephemeral_model(i, n_staging)
        )

    total = n_staging + n_intermediate + n_marts + n_ephemeral
    print(
        f"Generated {total} models: "
        f"{n_staging} staging, {n_intermediate} intermediate, "
        f"{n_marts} marts, {n_ephemeral} ephemeral"
    )
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


def compile_dbt_project(project_dir: Path) -> None:
    """Run dbt compile to pre-warm the manifest and partial parse cache."""
    profiles_dir = project_dir / "profiles_yml"
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


def run_benchmark(
    project_dir: Path,
    profiles_dir: Path,
    process_counts: list[int],
    iterations: int = 3,
    warmup: int = 1,
) -> list[dict]:
    """Run sqlfluff lint with different process counts and measure timings.

    Returns:
        List of result dicts with keys: processes, iteration, wall_clock,
        files, violations.
    """
    models_dir = str(project_dir / "models")
    results = []

    for n_procs in process_counts:
        print(f"\n--- Benchmarking with --processes {n_procs} ---")

        for i in range(warmup + iterations):
            is_warmup = i < warmup
            label = (
                f"warmup {i + 1}/{warmup}"
                if is_warmup
                else (f"iter {i - warmup + 1}/{iterations}")
            )

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
                retain_files=False,
            )
            wall_clock = time.perf_counter() - t0

            n_files = sum(p.stats()["files"] for p in result.paths)
            n_violations = result.num_violations()

            if is_warmup:
                print(
                    f"  {label}: {wall_clock:.1f}s ({n_files} files, {n_violations} violations) [discarded]"
                )
            else:
                print(
                    f"  {label}: {wall_clock:.1f}s ({n_files} files, {n_violations} violations)"
                )
                results.append(
                    {
                        "processes": n_procs,
                        "iteration": i - warmup + 1,
                        "wall_clock": wall_clock,
                        "files": n_files,
                        "violations": n_violations,
                    }
                )

    return results


def print_results(results: list[dict]) -> None:
    """Print a summary table of benchmark results."""
    by_procs: dict[int, list[float]] = {}
    for r in results:
        by_procs.setdefault(r["processes"], []).append(r["wall_clock"])

    print("\n" + "=" * 65)
    print("  dbt Parallel Templating Benchmark Results")
    print("=" * 65)

    baseline: Optional[float] = None
    print(
        f"\n{'Processes':>10} | {'Mean (s)':>10} | {'Std (s)':>10} | {'Min (s)':>10} | {'Speedup':>8}"
    )
    print("-" * 65)

    for n_procs in sorted(by_procs.keys()):
        times = by_procs[n_procs]
        mean_t = statistics.mean(times)
        min_t = min(times)
        std_t = statistics.stdev(times) if len(times) > 1 else 0.0

        if baseline is None:
            baseline = mean_t

        speedup = baseline / mean_t if mean_t > 0 else 0
        print(
            f"{n_procs:>10} | {mean_t:>10.1f} | {std_t:>10.2f} | {min_t:>10.1f} | {speedup:>7.2f}x"
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
    args = parser.parse_args()

    process_counts = [int(x.strip()) for x in args.processes.split(",")]

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
        if not args.skip_generate:
            project_dir.mkdir(parents=True, exist_ok=True)
    else:
        tmpdir = tempfile.mkdtemp(prefix="sqlfluff_bench_dbt_")
        project_dir = Path(tmpdir)

    try:
        # Generate project
        if not args.skip_generate:
            generate_dbt_project(str(project_dir), model_count=args.models)

        profiles_dir = project_dir / "profiles_yml"

        # Compile dbt project
        if not args.skip_compile:
            compile_dbt_project(project_dir)

        # Run benchmarks
        results = run_benchmark(
            project_dir=project_dir,
            profiles_dir=profiles_dir,
            process_counts=process_counts,
            iterations=args.iterations,
            warmup=args.warmup,
        )

        # Print results
        print_results(results)

    finally:
        if tmpdir and not args.no_clean:
            print(f"Cleaning up {tmpdir}")
            shutil.rmtree(tmpdir, ignore_errors=True)
        elif tmpdir:
            print(f"Project kept at: {tmpdir}")


if __name__ == "__main__":
    main()

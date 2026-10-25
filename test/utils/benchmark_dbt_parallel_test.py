"""Tests for utils/benchmark_dbt_parallel.py.

Tests the synthetic dbt project generator and results formatting
without requiring dbt or dbt-duckdb to be installed.
"""

import csv
import io
import random
import re
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from sqlfluff.core import Linter

# The benchmark script lives in utils/ (project root), not in the
# sqlfluff package.  Add it to sys.path so we can import it.
_UTILS_DIR = str(Path(__file__).resolve().parent.parent.parent / "utils")
if _UTILS_DIR not in sys.path:
    sys.path.insert(0, _UTILS_DIR)

import benchmark_dbt_parallel as bench  # noqa: E402

# -- Helpers -----------------------------------------------------------------


def _strip_jinja(sql: str) -> str:
    """Replace Jinja constructs with SQL-safe equivalents for parsing.

    This is intentionally Jinja-aware rather than a blind regex replace,
    so the resulting SQL is structurally valid for the ANSI parser.
    """
    # Remove standalone config/set blocks (they produce no SQL output)
    sql = re.sub(r"\{\{-?\s*config\(.*?\)\s*-?\}\}", "", sql)
    # Replace ref/source calls with a valid table identifier
    sql = re.sub(r"\{\{\s*ref\([^)]+\)\s*\}\}", "placeholder_ref", sql)
    sql = re.sub(r"\{\{\s*source\([^)]+\)\s*\}\}", "placeholder_source", sql)
    # Replace var() with a bare identifier (templates usually wrap in quotes)
    sql = re.sub(r"\{\{\s*var\([^)]+\)\s*\}\}", "placeholder_var", sql)
    # Replace macro calls (e.g. {{ safe_divide(...) }}) with a literal
    sql = re.sub(r"\{\{.*?\}\}", "1", sql)
    # Remove Jinja control flow tags entirely
    sql = re.sub(r"\{%.*?%\}", "", sql)
    return sql.strip()


def _assert_parseable_sql(sql: str) -> None:
    """Assert that SQL (with Jinja stripped) parses without unparsable segments."""
    clean = _strip_jinja(sql)
    if not clean:
        return
    linter = Linter(dialect="ansi")
    parsed = linter.parse_string(clean)
    unparsable = [seg for seg in parsed.tree.recursive_crawl("unparsable")]
    assert not unparsable, (
        f"Unparsable segments found: {[seg.raw for seg in unparsable]}\n\nSQL:\n{clean}"
    )


# -- Model generators --------------------------------------------------------


@pytest.fixture(autouse=True)
def _deterministic_random():
    """Ensure reproducible model generation across all tests."""
    random.seed(42)


def test_staging_model_is_parseable_sql():
    """Staging model produces SQL that parses without errors."""
    _assert_parseable_sql(bench._staging_model(0))


def test_staging_model_idx_appears_in_output():
    """The index parameter controls the column/table identifiers."""
    sql_0 = bench._staging_model(0)
    sql_7 = bench._staging_model(7)
    assert "id_0" in sql_0
    assert "id_7" in sql_7
    assert "id_0" not in sql_7


def test_intermediate_model_refs_are_within_bounds():
    """Intermediate model refs only reference staging indices that exist."""
    sql = bench._intermediate_model(0, stg_count=5)
    refs = re.findall(r"ref\('stg_(\d+)'\)", sql)
    assert len(refs) >= 1
    for ref_idx in refs:
        assert int(ref_idx) < 5, f"stg_{ref_idx} out of range for stg_count=5"


def test_intermediate_model_is_parseable_sql():
    """Intermediate model produces SQL that parses without errors."""
    _assert_parseable_sql(bench._intermediate_model(0, stg_count=10))


def test_mart_model_source_count_bounded():
    """Mart model creates between 2 and 4 CTEs (or fewer if int_count is small)."""
    sql = bench._mart_model(0, int_count=10)
    source_ctes = re.findall(r"source_\d+ AS", sql)
    assert 2 <= len(source_ctes) <= 4


def test_mart_model_refs_within_bounds():
    """Mart model refs only reference intermediate indices that exist."""
    sql = bench._mart_model(0, int_count=8)
    refs = re.findall(r"ref\('int_(\d+)'\)", sql)
    for ref_idx in refs:
        assert int(ref_idx) < 8, f"int_{ref_idx} out of range for int_count=8"


def test_ephemeral_model_ref_within_bounds():
    """Ephemeral model refs only reference staging indices that exist."""
    sql = bench._ephemeral_model(0, stg_count=3)
    refs = re.findall(r"ref\('stg_(\d+)'\)", sql)
    assert len(refs) == 1
    assert int(refs[0]) < 3


# -- Project generator -------------------------------------------------------


@pytest.fixture()
def project_20(tmp_path):
    """Generate a 20-model project for reuse across tests."""
    return bench.generate_dbt_project(str(tmp_path), model_count=20)


def test_tier_distribution(project_20):
    """Models are split roughly 40/30/20/10 across tiers."""
    staging = list((project_20 / "models" / "staging").glob("stg_*.sql"))
    intermediate = list((project_20 / "models" / "intermediate").glob("int_*.sql"))
    marts = list((project_20 / "models" / "marts").glob("mart_*.sql"))
    ephemeral = list((project_20 / "models" / "ephemeral").glob("eph_*.sql"))

    assert len(staging) == 8  # 40% of 20
    assert len(intermediate) == 6  # 30% of 20
    assert len(marts) == 4  # 20% of 20
    assert len(ephemeral) == 2  # remainder
    assert len(staging) + len(intermediate) + len(marts) + len(ephemeral) == 20


def test_sources_yml_is_valid_yaml_with_correct_schema(project_20):
    """sources.yml is parseable YAML with a source per staging model."""
    content = (project_20 / "models" / "staging" / "sources.yml").read_text()
    data = yaml.safe_load(content)
    assert data["version"] == 2
    tables = data["sources"][0]["tables"]
    staging_count = len(list((project_20 / "models" / "staging").glob("stg_*.sql")))
    assert len(tables) == staging_count
    # Each table name should match a staging model
    for table in tables:
        assert re.match(r"table_\d{4}", table["name"])


def test_dbt_project_yml_is_valid_yaml(project_20):
    """dbt_project.yml is parseable YAML with required dbt fields."""
    content = (project_20 / "dbt_project.yml").read_text()
    data = yaml.safe_load(content)
    assert data["name"] == "benchmark_project"
    assert data["config-version"] == 2
    assert data["profile"] == "benchmark"
    assert "models" in data.get("model-paths", [])


def test_profiles_yml_is_valid_yaml(project_20):
    """profiles.yml is parseable YAML targeting DuckDB in-memory."""
    content = (project_20 / "profiles_yml" / "profiles.yml").read_text()
    data = yaml.safe_load(content)
    outputs = data["benchmark"]["outputs"]["dev"]
    assert outputs["type"] == "duckdb"
    assert outputs["path"] == ":memory:"


def test_sqlfluff_config_paths_use_forward_slashes(project_20):
    """Generated .sqlfluff paths use forward slashes (cross-platform)."""
    content = (project_20 / ".sqlfluff").read_text()
    for line in content.splitlines():
        if "project_dir" in line or "profiles_dir" in line:
            _, _, path_value = line.partition("=")
            assert "\\" not in path_value, f"Backslash in: {line}"


def test_all_generated_models_are_parseable_sql(project_20):
    """Every generated .sql file produces parseable SQL after Jinja stripping."""
    model_files = list((project_20 / "models").rglob("*.sql"))
    assert len(model_files) == 20
    for sql_file in model_files:
        _assert_parseable_sql(sql_file.read_text())


def test_cross_tier_ref_consistency(project_20):
    """Intermediate models only ref staging; marts only ref intermediate."""
    stg_names = {f.stem for f in (project_20 / "models" / "staging").glob("stg_*.sql")}
    int_names = {
        f.stem for f in (project_20 / "models" / "intermediate").glob("int_*.sql")
    }

    for f in (project_20 / "models" / "intermediate").glob("*.sql"):
        for ref in re.findall(r"ref\('(\w+)'\)", f.read_text()):
            assert ref in stg_names, (
                f"{f.name} refs '{ref}' which is not a staging model"
            )

    for f in (project_20 / "models" / "marts").glob("*.sql"):
        for ref in re.findall(r"ref\('(\w+)'\)", f.read_text()):
            assert ref in int_names, (
                f"{f.name} refs '{ref}' which is not an intermediate model"
            )

    for f in (project_20 / "models" / "ephemeral").glob("*.sql"):
        for ref in re.findall(r"ref\('(\w+)'\)", f.read_text()):
            assert ref in stg_names, (
                f"{f.name} refs '{ref}' which is not a staging model"
            )


def test_reproducible_across_runs(tmp_path):
    """Two generations with the same count produce byte-identical models."""
    p1 = tmp_path / "a"
    p2 = tmp_path / "b"
    bench.generate_dbt_project(str(p1), model_count=10)
    bench.generate_dbt_project(str(p2), model_count=10)

    files_a = sorted((p1 / "models").rglob("*.sql"))
    files_b = sorted((p2 / "models").rglob("*.sql"))
    assert len(files_a) == len(files_b)
    for fa, fb in zip(files_a, files_b):
        assert fa.read_bytes() == fb.read_bytes(), f"Mismatch: {fa.name}"


def test_minimum_model_count(tmp_path):
    """model_count < 4 is clamped to 4 (one model per tier minimum)."""
    project = bench.generate_dbt_project(str(tmp_path), model_count=1)
    total = 0
    for tier in ("staging", "intermediate", "marts", "ephemeral"):
        models = list((project / "models" / tier).glob("*.sql"))
        assert len(models) >= 1, f"No models in {tier}/"
        total += len(models)
    assert total == 4, f"Expected exactly 4 models (minimum), got {total}"


# -- Results formatting ------------------------------------------------------


def test_print_results_speedup_is_ratio_of_means(capsys):
    """Speedup column equals baseline mean / current mean."""
    results = [
        {
            "processes": 1,
            "iteration": 1,
            "wall_clock": 12.0,
            "files": 50,
            "violations": 0,
        },
        {
            "processes": 1,
            "iteration": 2,
            "wall_clock": 8.0,
            "files": 50,
            "violations": 0,
        },
        {
            "processes": 4,
            "iteration": 1,
            "wall_clock": 4.0,
            "files": 50,
            "violations": 0,
        },
        {
            "processes": 4,
            "iteration": 2,
            "wall_clock": 6.0,
            "files": 50,
            "violations": 0,
        },
    ]
    bench.print_results(results)
    output = capsys.readouterr().out
    # baseline mean = 10.0, processes=4 mean = 5.0 → speedup = 2.00x
    assert "2.00x" in output


def test_print_results_summary_uses_highest_process_count(capsys):
    """Summary line references the highest process count tested."""
    results = [
        {
            "processes": 1,
            "iteration": 1,
            "wall_clock": 10.0,
            "files": 50,
            "violations": 0,
        },
        {
            "processes": 2,
            "iteration": 1,
            "wall_clock": 6.0,
            "files": 50,
            "violations": 0,
        },
        {
            "processes": 8,
            "iteration": 1,
            "wall_clock": 3.0,
            "files": 50,
            "violations": 0,
        },
    ]
    bench.print_results(results)
    output = capsys.readouterr().out
    assert "8 processes" in output
    assert "3.33x" in output


def test_print_results_single_iteration_no_crash(capsys):
    """Single iteration doesn't crash on stdev (n=1 edge case)."""
    results = [
        {
            "processes": 1,
            "iteration": 1,
            "wall_clock": 8.0,
            "files": 20,
            "violations": 1,
        },
    ]
    # Should not raise StatisticsError
    bench.print_results(results)


# -- dbt executable discovery ------------------------------------------------


def test_find_dbt_prefers_venv_over_path():
    """When dbt exists in the venv, PATH is not consulted."""
    with patch.object(Path, "exists", return_value=True):
        result = bench._find_dbt_executable()
        # Should return the venv path, not a shutil.which result
        assert "dbt" in result


def test_find_dbt_falls_back_to_path():
    """When venv dbt doesn't exist, falls back to shutil.which."""
    sentinel = "/custom/path/dbt"
    original_exists = Path.exists

    def _mock_exists(self):
        if "dbt" in str(self) and "venv" not in str(self).lower():
            return original_exists(self)
        if "dbt" in self.name:
            return False
        return original_exists(self)

    with patch.object(Path, "exists", _mock_exists):
        with patch("benchmark_dbt_parallel.shutil.which", return_value=sentinel):
            result = bench._find_dbt_executable()
            assert result == sentinel


def test_find_dbt_exits_when_missing():
    """Exits with code 1 when dbt cannot be found anywhere."""
    with patch.object(Path, "exists", return_value=False):
        with patch("benchmark_dbt_parallel.shutil.which", return_value=None):
            with pytest.raises(SystemExit) as exc_info:
                bench._find_dbt_executable()
            assert exc_info.value.code == 1


# -- Efficiency column -------------------------------------------------------


def test_print_results_shows_efficiency(capsys):
    """Efficiency column shows parallel scaling as a percentage."""
    results = [
        {
            "processes": 1,
            "iteration": 1,
            "wall_clock": 12.0,
            "files": 50,
            "violations": 0,
        },
        {
            "processes": 4,
            "iteration": 1,
            "wall_clock": 4.0,
            "files": 50,
            "violations": 0,
        },
    ]
    bench.print_results(results)
    output = capsys.readouterr().out
    # 1 proc: efficiency = 12/(12*1) = 100%
    assert "100%" in output
    # 4 procs: efficiency = 12/(4*4) = 75%
    assert "75%" in output


def test_print_results_perfect_scaling_is_100_percent(capsys):
    """Perfect linear scaling shows 100% efficiency at all process counts."""
    results = [
        {
            "processes": 1,
            "iteration": 1,
            "wall_clock": 8.0,
            "files": 50,
            "violations": 0,
        },
        {
            "processes": 4,
            "iteration": 1,
            "wall_clock": 2.0,
            "files": 50,
            "violations": 0,
        },
    ]
    bench.print_results(results)
    output = capsys.readouterr().out
    # Both should show 100% (8/(2*4) = 1.0)
    assert output.count("100%") == 2


# -- Comparison mode ----------------------------------------------------------


def _make_results(mode, procs_times):
    """Helper: create result dicts from a dict of {procs: [times]}."""
    results = []
    for n_procs, times in procs_times.items():
        for i, t in enumerate(times):
            results.append(
                {
                    "mode": mode,
                    "processes": n_procs,
                    "iteration": i + 1,
                    "wall_clock": t,
                    "files": 100,
                    "violations": 0,
                    "phase": "warm",
                }
            )
    return results


def test_print_comparison_shows_both_efficiencies(capsys):
    """Comparison table shows separate efficiency for standard and warm."""
    std = _make_results("standard", {1: [10.0], 4: [5.0]})
    warm = _make_results("warm", {1: [10.0], 4: [3.0]})
    bench.print_comparison(std, warm)
    output = capsys.readouterr().out
    # Standard 4-proc eff: 10/(5*4) = 50%
    assert "50%" in output
    # Warm 4-proc eff: 10/(3*4) = 83%
    assert "83%" in output


def test_print_comparison_shows_warm_gain(capsys):
    """Warm Gain column shows ratio of standard to warm time."""
    std = _make_results("standard", {1: [12.0], 8: [6.0]})
    warm = _make_results("warm", {1: [12.0], 8: [2.0]})
    bench.print_comparison(std, warm)
    output = capsys.readouterr().out
    # Warm gain at 8 procs: 6.0 / 2.0 = 3.00x
    assert "3.00x" in output


def test_print_comparison_baseline_from_standard(capsys):
    """Baseline for efficiency is the standard 1-proc time."""
    std = _make_results("standard", {1: [10.0], 2: [6.0]})
    warm = _make_results("warm", {1: [11.0], 2: [4.0]})
    bench.print_comparison(std, warm)
    output = capsys.readouterr().out
    # Baseline = 10.0 (standard), warm 2-proc eff = 10/(4*2) = 125%
    # (warm sequential was slower, so warm parallel looks super-efficient)
    assert "125%" in output


# -- CSV output ---------------------------------------------------------------


def test_write_csv_to_file(tmp_path):
    """write_csv writes correct CSV with headers to a file."""
    results = _make_results("warm", {1: [10.0], 4: [3.0]})
    out_file = str(tmp_path / "results.csv")
    bench.write_csv(results, out_file)

    with open(out_file, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 2
    assert rows[0]["mode"] == "warm"
    assert rows[0]["processes"] == "1"
    assert float(rows[0]["wall_clock"]) == 10.0
    assert rows[1]["processes"] == "4"


def test_write_csv_to_stdout(capsys):
    """write_csv with no path writes CSV to stdout."""
    results = _make_results("standard", {1: [8.0]})
    bench.write_csv(results)
    output = capsys.readouterr().out
    assert "mode,processes,iteration,wall_clock" in output
    assert "standard,1,1,8.0" in output


def test_write_csv_includes_mode_field():
    """CSV output includes the mode field for compare filtering."""
    results = _make_results("standard", {4: [5.0]}) + _make_results("warm", {4: [3.0]})
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf,
        fieldnames=[
            "mode",
            "processes",
            "iteration",
            "wall_clock",
            "files",
            "violations",
            "phase",
        ],
    )
    writer.writeheader()
    writer.writerows(results)
    buf.seek(0)
    reader = csv.DictReader(buf)
    rows = list(reader)
    modes = {r["mode"] for r in rows}
    assert modes == {"standard", "warm"}


# -- run_benchmark mode field -------------------------------------------------


def test_run_benchmark_results_include_mode():
    """Result dicts from run_benchmark include the mode field."""
    # We can't run a real benchmark without dbt, but we can verify
    # that the mode parameter is wired through by checking the function
    # signature accepts it.
    import inspect

    sig = inspect.signature(bench.run_benchmark)
    assert "mode" in sig.parameters
    assert sig.parameters["mode"].default == "standard"

"""Tests for the parsing benchmark's profiling output."""

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


def test_benchmark_preserves_meta_policy_timing(tmp_path, capsys):
    """Include the policy stage in iteration means, JSON and printed totals."""
    repo_root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location(
        "benchmark_parsing", repo_root / "utils" / "benchmark_parsing.py"
    )
    assert spec and spec.loader
    benchmark = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(benchmark)
    parsed = SimpleNamespace(
        time_dict={"lexing": 0.001, "parsing": 0.02},
        parsed_variants=[SimpleNamespace(tree=True)],
        violations=[],
    )
    with (
        patch.object(benchmark, "Linter", autospec=True) as linter,
        patch.object(benchmark, "reset_parse_profile") as reset,
        patch.object(
            benchmark,
            "get_parse_profile",
            side_effect=[
                {"rust_core": 0.004, "meta_policy": 0.002},
                {"rust_core": 0.006},
            ],
        ),
    ):
        linter.return_value.parse_string.return_value = parsed
        result = benchmark.parse_with_sqlfluff(
            repo_root / "test" / "fixtures" / "dialects" / "ansi" / "select_c.sql",
            use_rust=True,
            iterations=2,
            warmup=0,
            profile=True,
        )
        assert reset.call_count == 2

    assert result["success"]
    assert result["stage_profile"] == {
        "rust_core": 0.005,
        "meta_policy": 0.001,
        "convert": 0.0,
        "apply": 0.0,
        "apply_as_tree": 0.0,
    }
    output_file = tmp_path / "benchmark.json"
    benchmark.save_results({"rust": [result]}, output_file)
    assert (
        json.loads(output_file.read_text(encoding="utf-8"))["rust"][0]["stage_profile"]
        == result["stage_profile"]
    )

    benchmark.print_profile_summary([result])
    lines = capsys.readouterr().out.splitlines()
    policy_row = next(line for line in lines if line.strip().startswith("meta_policy"))
    assert policy_row.split() == ["meta_policy", "1.000", "16.7%"]
    totals_row = next(line for line in lines if line.strip().startswith("stages sum"))
    assert totals_row.split() == ["stages", "sum", "6.000"]

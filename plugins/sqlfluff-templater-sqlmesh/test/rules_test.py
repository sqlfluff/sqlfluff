"""Test SQLMesh templater with SQLFluff rules."""

import shutil
from pathlib import Path

import pytest
from sqlfluff_templater_sqlmesh.templater import SQLMeshTemplater

from sqlfluff.core import Linter
from sqlfluff.core.config import FluffConfig


@pytest.fixture
def fixture_dir():
    """Get the path to test fixtures."""
    return Path(__file__).parent / "fixtures" / "sqlmesh"


@pytest.fixture
def sqlmesh_fluff_config(fixture_dir):
    """Returns SQLFluff SQLMesh configuration dictionary."""
    return {
        "core": {
            "templater": "sqlmesh",
            "dialect": "duckdb",
        },
        "templater": {
            "sqlmesh": {
                "project_dir": str(fixture_dir),
                "config": "config",
                "gateway": "local",
            },
        },
    }


class TestSQLMeshRules:
    """Rule tests for the SQLMesh templater plugin."""

    def test_rule_sm01_blocks_one_equals_one(self):
        """SM01 flags `1 = 1`."""
        linted = Linter(
            config=FluffConfig(
                configs={"core": {"dialect": "duckdb"}},
                overrides={"rules": "SM01"},
            )
        ).lint_string("SELECT * FROM foo WHERE 1 = 1")

        violations = linted.check_tuples()
        assert any(code == "SM01" for code, *_ in violations), violations

    def test_rule_sm01_ignores_non_constant_comparison(self):
        """SM01 ignores non-constant comparisons."""
        linted = Linter(
            config=FluffConfig(
                configs={"core": {"dialect": "duckdb"}},
                overrides={"rules": "SM01"},
            )
        ).lint_string("SELECT * FROM foo WHERE id = 1")

        assert linted.check_tuples() == []

    def test_rule_sm01_ignores_join_tautology(self):
        """SM01 only applies to WHERE predicates."""
        linted = Linter(
            config=FluffConfig(
                configs={"core": {"dialect": "duckdb"}},
                overrides={"rules": "SM01"},
            )
        ).lint_string("SELECT * FROM foo JOIN bar ON 1 = 1")

        assert linted.check_tuples() == []

    def test_rule_sm01_ignores_case_tautology(self):
        """SM01 only applies to WHERE predicates."""
        linted = Linter(
            config=FluffConfig(
                configs={"core": {"dialect": "duckdb"}},
                overrides={"rules": "SM01"},
            )
        ).lint_string("SELECT CASE WHEN 1 = 1 THEN 'x' END AS value FROM foo")

        assert linted.check_tuples() == []

    def test_rule_sm02_requires_cast_for_aliased_expression(self):
        """SM02 requires casts for aliased expressions."""
        linted = Linter(
            config=FluffConfig(
                configs={"core": {"dialect": "duckdb"}},
                overrides={"rules": "SM02"},
            )
        ).lint_string("SELECT amount + fee AS total FROM payments")

        violations = linted.check_tuples()
        assert any(code == "SM02" for code, *_ in violations), violations

    def test_rule_sm02_allows_casted_aliased_expression(self):
        """SM02 allows explicitly cast aliased expressions."""
        linted = Linter(
            config=FluffConfig(
                configs={"core": {"dialect": "duckdb"}},
                overrides={"rules": "SM02"},
            )
        ).lint_string("SELECT CAST(amount AS BIGINT) AS amount_bigint FROM payments")

        assert linted.check_tuples() == []

    def test_rule_sm02_rejects_nested_cast_expression(self):
        """SM02 requires the final projected expression to be cast."""
        linted = Linter(
            config=FluffConfig(
                configs={"core": {"dialect": "duckdb"}},
                overrides={"rules": "SM02"},
            )
        ).lint_string(
            "SELECT COALESCE(CAST(amount AS BIGINT), 0) AS amount FROM payments"
        )

        violations = linted.check_tuples()
        assert any(code == "SM02" for code, *_ in violations), violations

    def test_rule_sm02_allows_try_casted_aliased_expression(self):
        """SM02 allows top-level cast-like functions."""
        linted = Linter(
            config=FluffConfig(
                configs={"core": {"dialect": "duckdb"}},
                overrides={"rules": "SM02"},
            )
        ).lint_string(
            "SELECT TRY_CAST(amount AS BIGINT) AS amount_bigint FROM payments"
        )

        assert linted.check_tuples() == []

    def test_rule_sm03_blocks_adhoc_catalog(self):
        """SM03 flags AD_HOC catalog references."""
        linted = Linter(
            config=FluffConfig(
                configs={"core": {"dialect": "duckdb"}},
                overrides={"rules": "SM03"},
            )
        ).lint_string("SELECT * FROM AD_HOC.analytics.orders")

        violations = linted.check_tuples()
        assert any(code == "SM03" for code, *_ in violations), violations

    def test_rule_sm03_blocks_two_part_adhoc_catalog(self):
        """SM03 flags two-part AD_HOC references."""
        linted = Linter(
            config=FluffConfig(
                configs={"core": {"dialect": "duckdb"}},
                overrides={"rules": "SM03"},
            )
        ).lint_string("SELECT * FROM AD_HOC.orders")

        violations = linted.check_tuples()
        assert any(code == "SM03" for code, *_ in violations), violations

    def test_rule_sm03_allows_non_adhoc_catalog(self):
        """SM03 ignores non-AD_HOC catalogs."""
        linted = Linter(
            config=FluffConfig(
                configs={"core": {"dialect": "duckdb"}},
                overrides={"rules": "SM03"},
            )
        ).lint_string("SELECT * FROM PROD.analytics.orders")

        assert linted.check_tuples() == []

    @pytest.mark.parametrize(
        ("rule_code", "model_name"),
        [
            ("LT02", "model_with_macros.sql"),
            ("LT01", "simple_model.sql"),
            ("ST06", "incremental_model.sql"),
        ],
    )
    def test_rule_runs_with_sqlmesh_templater(
        self, sqlmesh_fluff_config, fixture_dir, rule_code, model_name
    ):
        """Standard SQLFluff rules run with SQLMesh templating."""
        model_path = fixture_dir / "models" / model_name
        linter = Linter(
            config=FluffConfig(
                configs=sqlmesh_fluff_config, overrides={"rules": rule_code}
            )
        )

        linted_dir = linter.lint_path(str(model_path))
        linted_file = linted_dir.files[0]

        assert linted_file.templated_file is not None
        assert isinstance(linted_file.check_tuples(), list)

    def test_clean_model_no_violations(self, sqlmesh_fluff_config, fixture_dir):
        """A clean fixture model has no violations."""
        model_path = fixture_dir / "models" / "simple_model.sql"

        linter = Linter(
            config=FluffConfig(
                configs=sqlmesh_fluff_config,
                overrides={"rules": ["LT01", "LT02", "ST06"]},
            )
        )

        linted_dir = linter.lint_path(str(model_path))
        linted_file = linted_dir.files[0]

        violations = linted_file.check_tuples()
        assert len(violations) == 0, (
            f"Clean model should have no violations, found: {violations}"
        )

    def test_rule_cv09_blocks_adhoc_catalog(
        self, sqlmesh_fluff_config, fixture_dir, tmp_path
    ):
        """CV09 blocks AD_HOC via blocked words."""
        temp_project_dir = tmp_path / "sqlmesh_project"
        shutil.copytree(str(fixture_dir), str(temp_project_dir))

        temp_config = {
            "core": sqlmesh_fluff_config["core"].copy(),
            "templater": {
                "sqlmesh": {
                    **sqlmesh_fluff_config["templater"]["sqlmesh"],
                    "project_dir": str(temp_project_dir),
                }
            },
        }

        model_path = temp_project_dir / "models" / "adhoc_model.sql"
        model_source = """MODEL (
  name adhoc_model,
  kind VIEW
);

SELECT *
FROM AD_HOC.analytics.orders
"""
        model_path.write_text(model_source, encoding="utf-8")

        templater = SQLMeshTemplater()
        templated_file, errors = templater.process(
            fname=str(model_path),
            in_str=model_source,
            config=FluffConfig(configs=temp_config),
        )

        assert errors == []
        assert '"ad_hoc"' in templated_file.templated_str.lower()

        linted = Linter(
            config=FluffConfig(
                configs={
                    "core": {"dialect": "duckdb"},
                    "rules": {
                        "convention.blocked_words": {
                            "blocked_regex": "(?i)ad_hoc",
                        }
                    },
                },
                overrides={"rules": "CV09"},
            )
        ).lint_string(templated_file.templated_str)
        violations = linted.check_tuples()

        assert any(code == "CV09" for code, *_ in violations), violations

    def test_rule_with_sqlmesh_macros(self, sqlmesh_fluff_config, fixture_dir):
        """Rules run on SQLMesh macro-expanded SQL."""
        pytest.importorskip("sqlmesh")
        model_path = fixture_dir / "models" / "model_with_macros.sql"

        linter = Linter(
            config=FluffConfig(
                configs=sqlmesh_fluff_config, overrides={"rules": ["LT01", "LT02"]}
            )
        )

        linted_dir = linter.lint_path(str(model_path))
        linted_file = linted_dir.files[0]

        assert isinstance(linted_file.check_tuples(), list)

    def test_linter_integration_multiple_files(self, sqlmesh_fluff_config, fixture_dir):
        """Linter processes multiple SQLMesh files."""
        linter = Linter(
            config=FluffConfig(
                configs=sqlmesh_fluff_config, overrides={"rules": "LT01"}
            )
        )

        models_dir = fixture_dir / "models"
        linted_dir = linter.lint_path(str(models_dir))

        assert len(linted_dir.files) > 0, "Should process multiple model files"

        sql_files = [f for f in linted_dir.files if f.path.endswith(".sql")]
        assert len(sql_files) > 0, "Should find SQL model files"

    def test_sqlmesh_fix_behavior(self, sqlmesh_fluff_config, fixture_dir, tmp_path):
        """Fix mode works with SQLMesh templating."""
        temp_project_dir = tmp_path / "sqlmesh_project"
        shutil.copytree(str(fixture_dir), str(temp_project_dir))

        temp_config = {
            "core": sqlmesh_fluff_config["core"].copy(),
            "templater": {
                "sqlmesh": {
                    **sqlmesh_fluff_config["templater"]["sqlmesh"],
                    "project_dir": str(temp_project_dir),
                }
            },
        }

        test_content = """MODEL (
  name test_fix_behavior,
  kind VIEW
);

SELECT
id,
    name,
  email
FROM source_table   """  # Mixed indentation + trailing whitespace

        test_file_path = temp_project_dir / "models" / "test_fix_behavior.sql"

        with open(test_file_path, "w") as f:
            f.write(test_content)

        linter = Linter(
            config=FluffConfig(
                configs=temp_config,
                overrides={"rules": ["LT01", "LT02"]},
            )
        )

        linted_dir_check = linter.lint_path(str(test_file_path))
        linted_file_check = linted_dir_check.files[0]
        assert isinstance(linted_file_check.check_tuples(), list)

        linted_dir = linter.lint_path(str(test_file_path), fix=True)
        linted_file = linted_dir.files[0]

        fixed_content, _ = linted_file.fix_string()

        if fixed_content != test_content:
            assert "MODEL (" in fixed_content, (
                "Fixed content should preserve SQLMesh MODEL block"
            )
            assert "name test_fix_behavior" in fixed_content, (
                "Fixed content should preserve model name"
            )
            assert "SELECT" in fixed_content, "Fixed content should preserve SELECT"

        assert linted_file.templated_file is not None, (
            "Templated file should be created"
        )

    def test_sqlmesh_fix_slice_mapping_accuracy(
        self, sqlmesh_fluff_config, fixture_dir
    ):
        """Slice mapping remains valid during fixes."""
        model_path = fixture_dir / "models" / "simple_model.sql"

        linter = Linter(
            config=FluffConfig(
                configs=sqlmesh_fluff_config,
                overrides={"rules": ["LT02", "CP01"]},
            )
        )

        linted_dir = linter.lint_path(str(model_path), fix=True)
        linted_file = linted_dir.files[0]

        templated_file = linted_file.templated_file
        assert templated_file is not None, "Should have templated file"

        if templated_file.sliced_file:
            total_source_length = len(templated_file.source_str)
            total_templated_length = len(templated_file.templated_str)

            for i, slice_obj in enumerate(templated_file.sliced_file):
                source_slice = slice_obj.source_slice
                templated_slice = slice_obj.templated_slice

                assert source_slice.start >= 0, f"Slice {i} source start should be >= 0"
                assert source_slice.stop <= total_source_length, (
                    f"Slice {i} source stop should be <= source length"
                )
                assert templated_slice.start >= 0, (
                    f"Slice {i} templated start should be >= 0"
                )
                assert templated_slice.stop <= total_templated_length, (
                    f"Slice {i} templated stop should be <= templated length"
                )

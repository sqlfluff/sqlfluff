"""Test SQLMesh templater with real SQLMesh fixtures."""

from pathlib import Path

import pytest
from sqlfluff_templater_sqlmesh.templater import SQLMeshTemplater

from sqlfluff.core import FluffConfig


@pytest.fixture
def fixture_dir():
    """Get the path to test fixtures."""
    return Path(__file__).parent / "fixtures" / "sqlmesh"


@pytest.fixture
def sqlmesh_templater(fixture_dir):
    """Create and configure SQLMesh templater for tests."""
    templater = SQLMeshTemplater()

    config = FluffConfig(
        configs={
            "core": {"templater": "sqlmesh", "dialect": "duckdb"},
            "templater": {
                "sqlmesh": {
                    "project_dir": str(fixture_dir),
                    "config": "config",
                    "gateway": "local",
                }
            },
        }
    )

    templater.sqlfluff_config = config

    templater.project_dir = str(fixture_dir)

    return templater


class TestSQLMeshFixtures:
    """Fixture tests for SQLMesh templater behavior."""

    def test_simple_model_processing(self, sqlmesh_templater, fixture_dir):
        """Process a simple model without macros."""
        model_path = fixture_dir / "models" / "simple_model.sql"

        with open(model_path, "r") as f:
            model_content = f.read()

        model_name = sqlmesh_templater._get_model_name_from_path(str(model_path))
        assert model_name == "simple_model"

        templated_file, errors = sqlmesh_templater._create_literal_templated_file(
            str(model_path), model_content
        )

        assert errors == []
        assert templated_file.source_str == model_content
        assert templated_file.templated_str == model_content

    def test_macro_model_structure(self, fixture_dir):
        """Macro model fixture has expected structure."""
        model_path = fixture_dir / "models" / "model_with_macros.sql"

        with open(model_path, "r") as f:
            content = f.read()

        assert "@each(" in content
        assert "@if(" in content
        assert "@DEV" in content
        assert "@start_date" in content

    def test_incremental_model_structure(self, fixture_dir):
        """Incremental model fixture has expected structure."""
        model_path = fixture_dir / "models" / "incremental_model.sql"

        with open(model_path, "r") as f:
            content = f.read()

        assert "INCREMENTAL_BY_TIME_RANGE" in content
        assert "time_column" in content
        assert "@start_ds" in content
        assert "@end_ds" in content
        assert "@is_dev" in content

    def test_python_model_structure(self, fixture_dir):
        """Python model fixture has expected structure."""
        model_path = fixture_dir / "models" / "python_model.py"

        with open(model_path, "r") as f:
            content = f.read()

        assert "from sqlmesh import" in content
        assert "@model(" in content
        assert "def execute(" in content
        assert "ExecutionContext" in content

    def test_custom_macros_structure(self, fixture_dir):
        """Custom macro fixture has expected structure."""
        macro_path = fixture_dir / "macros" / "custom_macros.sql"

        with open(macro_path, "r") as f:
            content = f.read()

        assert "@DEF(safe_divide" in content
        assert "@DEF(extract_domain" in content
        assert "@END" in content

    def test_project_config_structure(self, fixture_dir):
        """Project config fixture has expected structure."""
        config_path = fixture_dir / "config.py"

        with open(config_path, "r") as f:
            content = f.read()

        assert "from sqlmesh import Config" in content
        assert "default_gateway" in content
        assert "gateways" in content
        assert "duckdb" in content

    def test_full_sqlmesh_rendering(self, sqlmesh_templater, fixture_dir):
        """Run full SQLMesh rendering when SQLMesh is installed."""
        pytest.importorskip("sqlmesh")
        model_path = fixture_dir / "models" / "simple_model.sql"

        with open(model_path, "r") as f:
            model_content = f.read()

        try:
            templated_file, errors = sqlmesh_templater.process(
                fname=str(model_path),
                in_str=model_content,
                config=sqlmesh_templater.sqlfluff_config,
            )

            assert templated_file is not None
            assert isinstance(errors, list)

        except ImportError:
            pytest.skip("SQLMesh not installed")

    def test_fixture_completeness(self, fixture_dir):
        """All required fixture files exist and are readable."""
        required_files = [
            "models/simple_model.sql",
            "models/model_with_macros.sql",
            "models/incremental_model.sql",
            "models/python_model.py",
            "macros/custom_macros.sql",
            "config.py",
            "templated_output/simple_model.sql",
            "templated_output/model_with_macros.sql",
            "templated_output/incremental_model.sql",
            ".sqlfluff",
        ]

        for file_path in required_files:
            full_path = fixture_dir / file_path
            assert full_path.exists(), f"Missing fixture file: {file_path}"
            assert full_path.is_file(), f"Path is not a file: {file_path}"

            with open(full_path, "r") as f:
                content = f.read()
                assert len(content) > 0, f"Empty fixture file: {file_path}"

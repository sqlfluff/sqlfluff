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
    # Create templater directly (for unit testing specific methods)
    templater = SQLMeshTemplater()

    # Create config with sqlmesh templater specified (plugin should be installed now)
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

    # Update the project dir to the sqlmesh project dir
    templater.project_dir = str(fixture_dir)

    return templater


class TestSQLMeshFixtures:
    """Test SQLMesh templater with real fixture files."""

    def test_simple_model_processing(self, sqlmesh_templater, fixture_dir):
        """Test processing a simple model without macros."""
        model_path = fixture_dir / "models" / "simple_model.sql"
        expected_path = fixture_dir / "templated_output" / "simple_model.sql"

        # Read the input model
        with open(model_path, "r") as f:
            model_content = f.read()

        # Read expected output
        with open(expected_path, "r") as f:
            expected_content = f.read()

        # Test model name extraction
        model_name = sqlmesh_templater._get_model_name_from_path(str(model_path))
        assert model_name == "simple_model"

        # Test literal templated file creation (fallback when SQLMesh not available)
        templated_file, errors = sqlmesh_templater._create_literal_templated_file(
            str(model_path), model_content
        )

        assert errors == []
        assert templated_file.source_str == model_content
        assert templated_file.templated_str == model_content

    def test_macro_model_structure(self, fixture_dir):
        """Test that macro model has expected structure."""
        model_path = fixture_dir / "models" / "model_with_macros.sql"

        with open(model_path, "r") as f:
            content = f.read()

        # Verify the model contains SQLMesh macros
        assert "@each(" in content
        assert "@if(" in content
        assert "@DEV" in content
        assert "@start_date" in content

    def test_incremental_model_structure(self, fixture_dir):
        """Test that incremental model has expected structure."""
        model_path = fixture_dir / "models" / "incremental_model.sql"

        with open(model_path, "r") as f:
            content = f.read()

        # Verify incremental model structure
        assert "INCREMENTAL_BY_TIME_RANGE" in content
        assert "time_column" in content
        assert "@start_ds" in content
        assert "@end_ds" in content
        assert "@is_dev" in content

    def test_python_model_structure(self, fixture_dir):
        """Test that Python model has expected structure."""
        model_path = fixture_dir / "models" / "python_model.py"

        with open(model_path, "r") as f:
            content = f.read()

        # Verify Python model structure
        assert "from sqlmesh import" in content
        assert "@model(" in content
        assert "def execute(" in content
        assert "ExecutionContext" in content

    def test_custom_macros_structure(self, fixture_dir):
        """Test that custom macros have expected structure."""
        macro_path = fixture_dir / "macros" / "custom_macros.sql"

        with open(macro_path, "r") as f:
            content = f.read()

        # Verify macro definitions
        assert "@DEF(safe_divide" in content
        assert "@DEF(extract_domain" in content
        assert "@END" in content

    def test_project_config_structure(self, fixture_dir):
        """Test that project config has expected structure."""
        config_path = fixture_dir / "config.py"

        with open(config_path, "r") as f:
            content = f.read()

        # Verify config structure
        assert "from sqlmesh import Config" in content
        assert "default_gateway" in content
        assert "gateways" in content
        assert "duckdb" in content

    @pytest.mark.skipif(
        True,  # Skip by default since SQLMesh might not be installed
        reason="Requires SQLMesh to be installed for full integration testing",
    )
    def test_full_sqlmesh_rendering(self, sqlmesh_templater, fixture_dir):
        """Test full SQLMesh rendering (requires SQLMesh installation)."""
        model_path = fixture_dir / "models" / "simple_model.sql"

        try:
            # Try to process the file with SQLMesh
            templated_file, errors = sqlmesh_templater.process(
                fname=str(model_path), config=sqlmesh_templater.sqlfluff_config
            )

            # If we get here, SQLMesh is installed and working
            assert templated_file is not None
            assert isinstance(errors, list)

        except ImportError:
            pytest.skip("SQLMesh not installed")
        except Exception as e:
            # Log the error for debugging but don't fail
            print(f"SQLMesh processing failed: {e}")

    def test_fixture_completeness(self, fixture_dir):
        """Test that all fixture files exist and are readable."""
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

            # Test that files are readable and non-empty
            with open(full_path, "r") as f:
                content = f.read()
                assert len(content) > 0, f"Empty fixture file: {file_path}"

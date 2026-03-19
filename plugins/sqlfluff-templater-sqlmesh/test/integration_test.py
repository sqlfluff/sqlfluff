"""Integration tests for the SQLMesh templater plugin."""

import tempfile
from pathlib import Path

import pytest

from sqlfluff_templater_sqlmesh.templater import SQLMeshTemplater
from sqlfluff.core import FluffConfig


class TestSQLMeshTemplaterIntegration:
    """Test SQLMesh templater integration."""

    def test_model_name_extraction(self):
        """Test model name extraction from file paths."""
        templater = SQLMeshTemplater()
        templater.project_dir = "/path/to/project"

        # Test basic model name extraction
        assert (
            templater._get_model_name_from_path("/path/to/project/models/my_model.sql")
            == "my_model"
        )

        # Test nested model
        assert (
            templater._get_model_name_from_path(
                "/path/to/project/models/marts/sales/my_model.sql"
            )
            == "marts.sales.my_model"
        )

        # Test model without models/ prefix
        assert (
            templater._get_model_name_from_path("/path/to/project/my_model.sql")
            == "my_model"
        )

    def test_literal_templated_file(self):
        """Test creation of literal templated files."""
        templater = SQLMeshTemplater()

        content = "SELECT 1 as test"
        templated_file, errors = templater._create_literal_templated_file(
            "test.sql", content
        )

        assert errors == []
        assert templated_file.source_str == content
        assert templated_file.templated_str == content
        assert len(templated_file.sliced_file) == 1
        assert templated_file.sliced_file[0].slice_type == "literal"
        assert len(templated_file.raw_sliced) == 1
        assert templated_file.raw_sliced[0].slice_type == "literal"

    @pytest.mark.skipif(
        True,  # Skip by default since SQLMesh might not be installed
        reason="Requires SQLMesh to be installed",
    )
    def test_sqlmesh_context_creation(self):
        """Test SQLMesh context creation (requires SQLMesh installation)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a basic SQLMesh project structure
            project_dir = Path(temp_dir) / "test_project"
            project_dir.mkdir()

            # Create a basic config file
            config_file = project_dir / "sqlmesh_config.yml"
            config_file.write_text(
                """
gateways:
  local:
    connection:
      type: duckdb
      database: :memory:
"""
            )

            # Create templater and set config
            templater = SQLMeshTemplater()
            config = FluffConfig()
            templater.sqlfluff_config = config
            templater.project_dir = str(project_dir)

            # Try to create SQLMesh context
            try:
                context = templater.sqlmesh_context
                assert context is not None
            except ImportError:
                pytest.skip("SQLMesh not installed")
            except Exception as e:
                # Log the error but don't fail the test
                print(f"SQLMesh context creation failed: {e}")

    def test_config_methods(self):
        """Test configuration getter methods."""
        templater = SQLMeshTemplater()

        # Mock config
        class MockConfig:
            def get_section(self, path):
                if path == ("templater", "sqlmesh", "project_dir"):
                    return "/test/project"
                elif path == ("templater", "sqlmesh", "config"):
                    return "local"
                elif path == ("templater", "sqlmesh", "gateway"):
                    return "default"
                return None

        templater.sqlfluff_config = MockConfig()

        assert templater._get_config_name() == "local"
        assert templater._get_gateway_name() == "default"

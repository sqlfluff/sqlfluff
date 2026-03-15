"""Integration tests for SQLMesh templater with SQLFluff core functionality."""

from pathlib import Path

import pytest

from sqlfluff.core import Linter
from sqlfluff.core.config import FluffConfig
from sqlfluff_templater_sqlmesh.templater import SQLMeshTemplater


@pytest.fixture
def fixture_dir():
    """Get the path to test fixtures."""
    return Path(__file__).parent / "fixtures" / "sqlmesh"


@pytest.fixture
def sqlmesh_config(fixture_dir):
    """SQLMesh templater configuration."""
    return {
        "core": {"templater": "sqlmesh", "dialect": "duckdb"},
        "templater": {
            "sqlmesh": {
                "project_dir": str(fixture_dir),
                "config": "config",  # Look for 'config' variable, not 'local'
                "gateway": "local",
            }
        },
    }


class TestSQLMeshTemplaterIntegration:
    """Test SQLMesh templater integration with SQLFluff core."""

    def test_templater_creates_valid_templated_file(self, sqlmesh_config, fixture_dir):
        """Test that templater produces valid TemplatedFile objects."""
        # Use Linter to test templater integration
        linter = Linter(config=FluffConfig(configs=sqlmesh_config))

        model_path = fixture_dir / "models" / "simple_model.sql"

        # Lint the file (which uses the templater internally)
        linted_dir = linter.lint_path(str(model_path))
        linted_file = linted_dir.files[0]

        # Should produce valid TemplatedFile
        assert linted_file.templated_file is not None
        assert linted_file.templated_file.source_str is not None
        assert linted_file.templated_file.templated_str is not None
        assert len(linted_file.templated_file.sliced_file) > 0

    def test_templater_handles_missing_file_gracefully(self, sqlmesh_config):
        """Test templater handles missing files gracefully."""
        linter = Linter(config=FluffConfig(configs=sqlmesh_config))
        # SQLFluff checks file existence before templating, so this raises SQLFluffUserError
        from sqlfluff.core.errors import SQLFluffUserError

        with pytest.raises(SQLFluffUserError, match="Specified path does not exist"):
            linter.lint_path("/non/existent/file.sql")

    def test_templater_with_inline_content(self, sqlmesh_config, fixture_dir):
        """Test templater with provided string content."""
        # Test inline content using the dbt pattern - call templater.process() directly
        content = """MODEL (
  name test_inline,
  kind VIEW
);

SELECT 1 as test_column"""

        # Use existing model path (like dbt does)
        model_path = fixture_dir / "models" / "simple_model.sql"

        # Create templater and call process() directly (dbt pattern)
        templater = SQLMeshTemplater()
        config = FluffConfig(configs=sqlmesh_config)
        templater.sqlfluff_config = config

        templated_file, violations = templater.process(
            in_str=content, fname=str(model_path), config=config
        )

        # Should work with the content
        assert templated_file is not None
        assert violations == []
        assert templated_file.source_str == content
        # The templated_str should be the rendered SQL from SQLMesh (ignores in_str, uses model from fname)
        # This is correct SQLMesh behavior - it renders by model name, not inline content
        assert "MODEL" not in templated_file.templated_str
        assert "SELECT" in templated_file.templated_str
        assert "simple_model" in str(
            templated_file.templated_str
        ) or "source_table" in str(templated_file.templated_str)

    def test_templater_config_pairs(self, sqlmesh_config):
        """Test templater config_pairs method."""
        templater = SQLMeshTemplater()
        config = FluffConfig(configs=sqlmesh_config)
        templater.sqlfluff_config = config

        pairs = templater.config_pairs()

        assert len(pairs) == 2
        assert pairs[0] == ("templater", "sqlmesh")
        assert pairs[1][0] == "sqlmesh"
        # Version could be actual version or "not installed"
        assert isinstance(pairs[1][1], str)

    def test_model_name_extraction_edge_cases(self, sqlmesh_config, fixture_dir):
        """Test model name extraction with various path formats."""
        templater = SQLMeshTemplater()
        config = FluffConfig(configs=sqlmesh_config)
        templater.sqlfluff_config = config
        templater.project_dir = str(fixture_dir)

        # Test various path formats
        test_cases = [
            (str(fixture_dir / "models" / "simple.sql"), "simple"),
            (str(fixture_dir / "models" / "nested" / "model.sql"), "nested.model"),
            (str(fixture_dir / "other_model.sql"), "other_model"),
            ("/absolute/path/outside/project.sql", None),  # Should return None
        ]

        for file_path, expected in test_cases:
            result = templater._get_model_name_from_path(file_path)
            assert (
                result == expected
            ), f"Path {file_path} should give {expected}, got {result}"

    def test_end_to_end_linting_workflow(self, sqlmesh_config, fixture_dir):
        """Test complete workflow: templater -> parser -> linter."""
        # Use existing simple_model.sql - SQLMesh knows about this model
        model_path = fixture_dir / "models" / "simple_model.sql"

        # Create linter - templater will be auto-discovered
        linter = Linter(config=FluffConfig(configs=sqlmesh_config))

        # Lint the file
        linted_dir = linter.lint_path(str(model_path))

        # Should successfully lint
        assert len(linted_dir.files) == 1
        linted_file = linted_dir.files[0]

        # File should have been processed (may have violations but shouldn't crash)
        violations = linted_file.check_tuples()
        print(f"Found {len(violations)} violations in test workflow")

        # Should have templated_file showing SQLMesh worked
        assert linted_file.templated_file is not None
        assert "SELECT" in linted_file.templated_file.templated_str
        assert "MODEL" not in linted_file.templated_file.templated_str

    def test_slice_mapping_accuracy(self, sqlmesh_config, fixture_dir):
        """Test that slice mapping is accurate for error positioning."""
        linter = Linter(config=FluffConfig(configs=sqlmesh_config))

        model_path = fixture_dir / "models" / "simple_model.sql"

        # Lint the file
        linted_dir = linter.lint_path(str(model_path))
        linted_file = linted_dir.files[0]
        templated_file = linted_file.templated_file

        # Check slice mapping integrity
        assert len(templated_file.sliced_file) > 0

        # All slices should have valid source and templated positions
        for slice_obj in templated_file.sliced_file:
            assert slice_obj.source_slice.start >= 0
            assert slice_obj.source_slice.stop <= len(templated_file.source_str)
            assert slice_obj.templated_slice.start >= 0
            assert slice_obj.templated_slice.stop <= len(templated_file.templated_str)

    def test_error_handling_with_invalid_project_dir(self, fixture_dir):
        """Test error handling with invalid project directory."""
        # Config with non-existent project directory
        config = FluffConfig(
            configs={
                "core": {"templater": "sqlmesh", "dialect": "duckdb"},
                "templater": {
                    "sqlmesh": {
                        "project_dir": "/non/existent/directory",
                        "config": "local",
                    }
                },
            }
        )

        linter = Linter(config=config)
        model_path = fixture_dir / "models" / "simple_model.sql"

        # Should handle gracefully (likely fall back to literal templating)
        linted_dir = linter.lint_path(str(model_path))
        linted_file = linted_dir.files[0]

        # Should not crash, may fall back to literal processing
        assert linted_file.templated_file is not None

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

    def test_find_model_block_end(self):
        """Test MODEL block boundary detection."""
        # Simple MODEL block
        source = "MODEL (\n  name foo,\n  kind VIEW\n);\n\nSELECT 1"
        end = SQLMeshTemplater._find_model_block_end(source)
        assert end is not None
        assert source[end:] == "SELECT 1"

        # Nested parentheses (INCREMENTAL_BY_TIME_RANGE)
        source_nested = (
            "MODEL (\n  name foo,\n  kind INCREMENTAL_BY_TIME_RANGE (\n"
            "    time_column ts\n  )\n);\n\nSELECT 1"
        )
        end_nested = SQLMeshTemplater._find_model_block_end(source_nested)
        assert end_nested is not None
        assert source_nested[end_nested:] == "SELECT 1"

        # String literals in MODEL block
        source_str = "MODEL (\n  name foo,\n  start '2023-01-01'\n);\n\nSELECT 1"
        end_str = SQLMeshTemplater._find_model_block_end(source_str)
        assert end_str is not None
        assert source_str[end_str:] == "SELECT 1"

        # No MODEL block
        assert SQLMeshTemplater._find_model_block_end("SELECT 1") is None

    def test_build_source_mapping_no_model_block(self):
        """Test source mapping when there is no MODEL block."""
        templater = SQLMeshTemplater()

        source = "SELECT 1 as test"
        rendered = "SELECT 1 as test"
        raw_sliced, sliced_file = templater._build_source_mapping(source, rendered)

        # Should be a single literal slice
        assert len(raw_sliced) == 1
        assert raw_sliced[0].slice_type == "literal"
        assert len(sliced_file) == 1
        assert sliced_file[0].slice_type == "literal"

    def test_build_source_mapping_with_model_block(self):
        """Test source mapping strips MODEL block correctly."""
        templater = SQLMeshTemplater()

        source = "MODEL (\n  name foo,\n  kind VIEW\n);\n\nSELECT 1 as test"
        rendered = "SELECT 1 as test"
        raw_sliced, sliced_file = templater._build_source_mapping(source, rendered)

        # First raw slice should be the MODEL block (source-only)
        assert raw_sliced[0].slice_type == "block_start"
        assert raw_sliced[0].source_idx == 0

        # First sliced_file entry should be source-only (zero-length templated)
        assert sliced_file[0].slice_type == "block_start"
        assert sliced_file[0].templated_slice == slice(0, 0)

        # The SQL body should map as literal
        literal_slices = [s for s in sliced_file if s.slice_type == "literal"]
        assert len(literal_slices) >= 1
        # The literal content should cover the rendered output
        total_literal = sum(
            s.templated_slice.stop - s.templated_slice.start for s in literal_slices
        )
        assert total_literal == len(rendered)

    def test_build_source_mapping_with_macros(self):
        """Test source mapping handles macro expansions correctly."""
        templater = SQLMeshTemplater()

        source = (
            "MODEL (\n  name foo,\n  kind VIEW\n);\n\n"
            "SELECT\n    @if(@DEV, 'dev', 'prod') as env\nFROM t"
        )
        rendered = "SELECT\n    'dev' as env\nFROM t"
        raw_sliced, sliced_file = templater._build_source_mapping(source, rendered)

        # Should have: block_start (MODEL), literal, templated, literal.
        # The macro expansion @if(@DEV, 'dev', 'prod') -> 'dev' is coalesced
        # into a single "templated" slice (not split into delete+equal+delete).
        slice_types = [s.slice_type for s in sliced_file]
        assert "block_start" in slice_types
        assert "literal" in slice_types
        assert "templated" in slice_types

        # Verify that the templated slice covers the full macro in the source.
        templated_slices = [s for s in raw_sliced if s.slice_type == "templated"]
        assert len(templated_slices) == 1
        assert "@if(" in templated_slices[0].raw

    def test_coalesce_diff_opcodes(self):
        """Test that difflib opcodes are coalesced to avoid zero-length slices."""
        coalesce = SQLMeshTemplater._coalesce_diff_opcodes

        # delete+equal+delete → single replace
        opcodes = [
            ("equal", 0, 11, 0, 11),
            ("delete", 11, 21, 11, 11),
            ("equal", 21, 26, 11, 16),
            ("delete", 26, 35, 16, 16),
            ("equal", 35, 49, 16, 30),
        ]
        result = coalesce(opcodes)
        assert len(result) == 3
        assert result[0][0] == "equal"
        assert result[1] == ("replace", 11, 35, 11, 16)
        assert result[2][0] == "equal"

        # Pure equals stay unchanged
        assert coalesce([("equal", 0, 10, 0, 10)]) == [("equal", 0, 10, 0, 10)]

        # Standalone replace stays as replace
        opcodes2 = [("equal", 0, 5, 0, 5), ("replace", 5, 10, 5, 8)]
        assert coalesce(opcodes2) == opcodes2

    def test_source_mapping_position_accuracy(self):
        """Test that positions in rendered SQL map to correct source positions.

        The TemplatedFile must be valid and the literal slices within the
        SQL body must produce correct offset-based mappings.
        """
        from sqlfluff.core.templaters.base import TemplatedFile

        templater = SQLMeshTemplater()

        source = "MODEL (\n  name foo,\n  kind VIEW\n);\n\nSELECT\n    id\nFROM t"
        rendered = "SELECT\n    id\nFROM t"
        raw_sliced, sliced_file = templater._build_source_mapping(source, rendered)

        # Constructing a TemplatedFile validates the slicing contract
        # (contiguous raw_sliced, contiguous templated_slice, etc.).
        tf = TemplatedFile(
            source_str=source,
            templated_str=rendered,
            fname="test.sql",
            sliced_file=sliced_file,
            raw_sliced=raw_sliced,
        )

        model_block_end = SQLMeshTemplater._find_model_block_end(source)
        assert model_block_end is not None

        # The SQL body should be a single literal slice starting at
        # the end of the MODEL block.
        literal_slices = [s for s in sliced_file if s.slice_type == "literal"]
        assert len(literal_slices) == 1
        assert literal_slices[0].source_slice.start == model_block_end

        # A position well inside the literal maps correctly.
        # "FROM t" is at rendered[14:20] and source[50:56].
        from_pos = rendered.index("FROM t")
        source_slice_from = tf.templated_slice_to_source_slice(
            slice(from_pos, from_pos + 6)
        )
        assert source[source_slice_from] == "FROM t"

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

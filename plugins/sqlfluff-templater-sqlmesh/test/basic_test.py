"""Basic tests for the SQLMesh templater plugin."""

from sqlfluff_templater_sqlmesh.templater import SQLMeshTemplater


def test_sqlmesh_templater_init():
    """Test that SQLMeshTemplater can be instantiated."""
    templater = SQLMeshTemplater()
    assert templater.name == "sqlmesh"
    assert templater.sequential_fail_limit == 3


def test_sqlmesh_templater_config_pairs():
    """Test that config_pairs returns expected format."""
    templater = SQLMeshTemplater()
    pairs = templater.config_pairs()
    assert len(pairs) == 2
    assert pairs[0] == ("templater", "sqlmesh")
    assert pairs[1][0] == "sqlmesh"
    # Version could be "not installed" if SQLMesh isn't available
    assert isinstance(pairs[1][1], str)


def test_sqlmesh_version_property():
    """Test the SQLMesh version property."""
    templater = SQLMeshTemplater()
    version = templater.sqlmesh_version
    # Should either be a version string or "not installed"
    assert isinstance(version, str)
    assert len(version) > 0

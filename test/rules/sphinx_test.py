"""Test the sphinx module works."""


def test_sphinx_import():
    """Test that expected rules are found in the _all_ attribute.

    By testing this we:
    a) Make sure the plugin architecture and loading is functioning
       properly.
    b) Ensure code coverage. 😁
    """
    import sqlfluff.rules.sphinx as sphinx_module

    # Verify that the rules we're expecting are imported
    assert "Rule_LT02" in sphinx_module.__all__
    assert "Rule_CP01" in sphinx_module.__all__

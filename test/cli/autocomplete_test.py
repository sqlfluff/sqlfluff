"""Tests for shell autocompletion."""
import os

import pytest

from sqlfluff.cli.autocomplete import generate_autocomplete_script
from sqlfluff.cli.commands import dialect_shell_complete


@pytest.mark.parametrize(
    "shell_type",
    [
        "bash",
        "zsh",
        "fish",
    ],
)
def test_generate_autocomplete_script(shell_type, tmp_path):
    """Verify that autocomplete script is created and dictionary result is returned."""
    save_path = str(tmp_path / f"shell_autocomplete.{shell_type}")
    autocomplete_result = generate_autocomplete_script(
        shell_type=shell_type,
        save_path=save_path,
    )
    assert autocomplete_result["shell_type"] == shell_type
    assert autocomplete_result["save_path"] == save_path
    assert os.path.exists(save_path)


@pytest.mark.parametrize(
    "incomplete,expected",
    [
        ["an", ["ansi"]],
        ["s", ["snowflake", "spark3", "sqlite"]],
        ["post", ["postgres"]],
    ],
)
def test_dialect_click_type_shell_complete(incomplete, expected):
    """Check that autocomplete returns dialects as expected."""
    completion_items = dialect_shell_complete(
        ctx="dummy_not_used", param="dummy_not_used", incomplete=incomplete
    )
    actual = [c.value for c in completion_items]
    assert expected == actual

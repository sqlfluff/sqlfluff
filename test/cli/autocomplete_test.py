"""Tests for shell autocompletion."""
import os
import tempfile

import pytest

from sqlfluff.cli.autocomplete import generate_autocomplete_script
from sqlfluff.cli.commands import dialect_shell_complete

autocomplete_tempdir = tempfile.mkdtemp()


@pytest.mark.parametrize(
    "shell_type,save_path,expected_result",
    [
        [
            "bash",
            os.path.join(autocomplete_tempdir, "shell_autocomplete.bash"),
            {
                "shell_type": "bash",
                "save_path": os.path.join(
                    autocomplete_tempdir, "shell_autocomplete.bash"
                ),
                "message": "Please source {} in your shell config file (e.g. ~.bashrc).".format(
                    os.path.join(autocomplete_tempdir, "shell_autocomplete.bash")
                ),
            },
        ],
        [
            "zsh",
            os.path.join(autocomplete_tempdir, "shell_autocomplete.zsh"),
            {
                "shell_type": "zsh",
                "save_path": os.path.join(
                    autocomplete_tempdir, "shell_autocomplete.zsh"
                ),
                "message": "Please source {} in your shell config file (e.g. ~.zshrc).".format(
                    os.path.join(autocomplete_tempdir, "shell_autocomplete.zsh")
                ),
            },
        ],
        [
            "fish",
            os.path.join(autocomplete_tempdir, "shell_autocomplete.fish"),
            {
                "shell_type": "fish",
                "save_path": os.path.join(
                    autocomplete_tempdir, "shell_autocomplete.fish"
                ),
                "message": (
                    "Ensure the autocompletion script is saved (or symlinked) to "
                    "~/.config/fish/completions/.sqlfluff.fish, and then reload your shell."
                ),
            },
        ],
    ],
)
def test_generate_autocomplete_script(shell_type, save_path, expected_result):
    """Verify that autocomplete script is created and dictionary result is returned."""
    autocomplete_result = generate_autocomplete_script(
        shell_type=shell_type,
        save_path=save_path,
    )
    assert autocomplete_result == expected_result
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

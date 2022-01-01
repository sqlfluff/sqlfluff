"""CLI autocompletion methods."""
import os
import subprocess
import sys
from typing import NamedTuple, Optional


class AutoCompleteResult(NamedTuple):
    """Result of `generate_autocomplete_script`."""

    success: bool
    message: str
    shell_type: Optional[str] = None
    save_path: Optional[str] = None


def generate_autocomplete_script(
    shell_type: str = "bash", save_path: Optional[str] = None
) -> AutoCompleteResult:
    """Generate autocompletion script for specified shell type.

    Args:
        shell_type (str, optional): One of bash, zsh, or fish. Defaults to "bash".
        save_path (Optional[str], optional): Location to save the autocompletion script.
                                             Defaults to None.

    Returns:
        AutoCompleteResult: Result object.
    """
    if sys.platform.lower() not in {"linux", "darwin"}:
        return AutoCompleteResult(
            success=False,
            message="Autocompletion is only available for Linux/MacOS.",
        )
    if save_path is None:
        # Use default save_path if none is specified.
        if shell_type.lower() == "fish":
            save_path = "~/.config/fish/completions/.sqlfluff.fish"
        else:
            save_path = f"~/.config/sqlfluff/.sqlfluff-complete.{shell_type.lower()}"

    if shell_type == "fish":
        message = (
            "Ensure the autocompletion script is saved (or symlinked) to "
            "~/.config/fish/completions/.sqlfluff.fish, and then reload your shell."
        )
    else:
        message = f"Please source {save_path} in your shell config file (e.g. ~.{shell_type}rc)."

    # Ensure that parent config directory exists.
    save_path = os.path.expanduser(save_path)
    save_folder = os.path.dirname(save_path)
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # Generate the autocompletion script.
    subprocess.run(
        [f"_SQLFLUFF_COMPLETE={shell_type.lower()}_source sqlfluff > {save_path}"],
        shell=True,
    )

    return AutoCompleteResult(
        success=True,
        message=message,
        shell_type=shell_type,
        save_path=save_path,
    )

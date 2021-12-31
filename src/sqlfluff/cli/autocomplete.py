"""CLI autocompletion methods."""
import os
import subprocess
from typing import Optional


def generate_autocomplete_script(
    shell_type: str = "bash", save_path: Optional[str] = None
) -> None:
    """Generate autocompletion script for specified shell type.

    Args:
        shell_type (str, optional): One of bash, zsh, or fish. Defaults to "bash".
        save_path (Optional[str], optional): Location to save the autocompletion script.
                                             Defaults to None.
    """
    if save_path is None:
        save_path = os.path.join(
            os.path.expanduser("~/.config/sqlfluff"),
            f".sqlfluff-complete.{shell_type.lower()}",
        )

    save_folder = os.path.dirname(save_path)
    if not os.path.exists(save_folder):
        os.mkdir(save_folder)

    subprocess.run(
        [f"_SQLFLUFF_COMPLETE={shell_type.lower()}_source sqlfluff > {save_path}"],
        shell=True,
    )


generate_autocomplete_script(shell_type="zsh")

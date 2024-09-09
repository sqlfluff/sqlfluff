"""Init file for the config module.

This holds all the methods and classes for configuration.
"""

from typing import Optional

from sqlfluff.core.config.fluffconfig import FluffConfig
from sqlfluff.core.config.loader import (
    ConfigLoader,
    load_config_file,
    load_config_resource,
    load_config_string,
)

__all__ = (
    "FluffConfig",
    "ConfigLoader",
    "load_config_file",
    "load_config_resource",
    "load_config_string",
    "progress_bar_configuration",
)


class ProgressBarConfiguration:
    """Singleton-esque progress bar configuration.

    It's expected to be set during starting with parameters coming from commands
    parameters, then to be just utilized as just
    ```
    from sqlfluff.core.config import progress_bar_configuration
    is_progressbar_disabled = progress_bar_configuration.disable_progress_bar
    ```
    """

    _disable_progress_bar: Optional[bool] = True

    @property
    def disable_progress_bar(self) -> Optional[bool]:  # noqa: D102
        return self._disable_progress_bar

    @disable_progress_bar.setter
    def disable_progress_bar(self, value: Optional[bool]) -> None:
        """`disable_progress_bar` setter.

        `True` means that progress bar should be always hidden, `False` fallbacks
        into `None` which is an automatic mode.
        From tqdm documentation: 'If set to None, disable on non-TTY.'
        """
        self._disable_progress_bar = value or None


progress_bar_configuration = ProgressBarConfiguration()

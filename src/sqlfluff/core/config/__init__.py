"""Init file for the config module.

This holds all the methods and classes for configuration.
"""

from typing import Optional

from sqlfluff.core.config.file import (
    load_config_file_as_dict,
    load_config_string_as_dict,
)
from sqlfluff.core.config.fluffconfig import FluffConfig
from sqlfluff.core.config.loader import (
    ConfigLoader,
    load_config_at_path,
    load_config_file,
    load_config_resource,
    load_config_string,
    load_config_up_to_path,
)

__all__ = (
    "FluffConfig",
    "ConfigLoader",
    "load_config_file",
    "load_config_resource",
    "load_config_string",
    "load_config_at_path",
    "load_config_up_to_path",
    "progress_bar_configuration",
    "clear_config_caches",
)


def clear_config_caches() -> None:
    """Clear any of the cached config methods.

    This is primarily used during testing where the cache may be be rendered unreliable
    by using moving around files while setting up tests. Some of the cached methods
    rely on *filename* caching, and so we may break one of the assumptions of the
    caching routines (that files aren't modified while SQLFluff is running) during
    the test suite. That means we need to clear the cache during those times to
    get reliable results.

    NOTE: You may not notice those results when running tests individually locally
    as they may only be visible when running the whole test suite.
    """
    load_config_file_as_dict.cache_clear()
    load_config_at_path.cache_clear()
    load_config_string_as_dict.cache_clear()
    pass


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

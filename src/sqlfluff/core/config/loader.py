"""Config loading methods and helpers.

This is designed to house the main functions which are exposed by the
overall config module. There is some caching in this module, which
is designed around caching the configuration loaded at *specific paths*
rather than the individual file caching in the `file` module.
"""

from __future__ import annotations

try:
    from importlib.resources import files
except ImportError:  # pragma: no cover
    # fallback for python <=3.8
    from importlib_resources import files  # type: ignore

import logging
import os
import os.path
import sys
from pathlib import Path
from typing import (
    Optional,
)

import platformdirs
import platformdirs.unix

from sqlfluff.core.config.file import (
    cache,
    load_config_file_as_dict,
    load_config_string_as_dict,
)
from sqlfluff.core.errors import SQLFluffUserError
from sqlfluff.core.helpers.dict import nested_combine
from sqlfluff.core.helpers.file import iter_intermediate_paths
from sqlfluff.core.types import ConfigMappingType

# Instantiate the config logger
config_logger = logging.getLogger("sqlfluff.config")

global_loader = None
""":obj:`ConfigLoader`: A variable to hold the single module loader when loaded.

We define a global loader, so that between calls to load config, we
can still cache appropriately
"""


ALLOWABLE_LAYOUT_CONFIG_KEYS = (
    "spacing_before",
    "spacing_after",
    "spacing_within",
    "line_position",
    "align_within",
    "align_scope",
)


def _get_user_config_dir_path(sys_platform: str) -> str:
    """Get the user config dir for this system.

    Args:
        sys_platform (str): The result of ``sys.platform()``. Provided
            as an argument here for ease of testing. In normal usage
            it should only be  called with ``sys.platform()``.
    """
    appname = "sqlfluff"
    appauthor = "sqlfluff"

    # On Mac OSX follow Linux XDG base dirs
    # https://github.com/sqlfluff/sqlfluff/issues/889
    user_config_dir_path = os.path.expanduser("~/.config/sqlfluff")
    # If the default config path doesn't exist, use the platform specific
    # config path. Preferentially using the XDG config path if set on MacOS.
    if sys_platform == "darwin" and not os.path.exists(user_config_dir_path):
        user_config_dir_path = platformdirs.unix.Unix(
            appname=appname, appauthor=appauthor
        ).user_config_dir
    # And then fall back to the platform default.
    if not os.path.exists(user_config_dir_path):
        user_config_dir_path = platformdirs.user_config_dir(appname, appauthor)
    return user_config_dir_path


def load_config_file(
    file_dir: str, file_name: str, configs: Optional[ConfigMappingType] = None
) -> ConfigMappingType:
    """Load a config file."""
    file_path = os.path.join(file_dir, file_name)
    raw_config = load_config_file_as_dict(file_path)
    # We always run `nested_combine()` because it has the side effect
    # of making a copy of the objects provided. This prevents us
    # from editing items which also sit within the cache.
    return nested_combine(configs or {}, raw_config)


def load_config_resource(package: str, file_name: str) -> ConfigMappingType:
    """Load a config resource.

    This is however more compatible with mypyc because it avoids
    the use of the __file__ object to find the default config.

    This is only tested extensively with the default config.

    Paths are resolved based on `os.getcwd()`.

    NOTE: This requires that the config file is built into
    a package but should be more performant because it leverages
    importlib.
    https://docs.python.org/3/library/importlib.resources.html
    """
    config_string = files(package).joinpath(file_name).read_text()
    # NOTE: load_config_string_as_dict is cached.
    return load_config_string_as_dict(
        config_string,
        os.getcwd(),
        logging_reference=f"<resource {package}.{file_name}>",
    )


def load_config_string(
    config_string: str,
    configs: Optional[ConfigMappingType] = None,
    working_path: Optional[str] = None,
) -> ConfigMappingType:
    """Load a config from the string in ini format.

    Paths are resolved based on the given working path or `os.getcwd()`.
    """
    filepath = working_path or os.getcwd()
    raw_config = load_config_string_as_dict(
        config_string, filepath, logging_reference="<config string>"
    )
    # We always run `nested_combine()` because it has the side effect
    # of making a copy of the objects provided. This prevents us
    # from editing items which also sit within the cache.
    return nested_combine(configs or {}, raw_config)


@cache
def load_config_at_path(path: str) -> ConfigMappingType:
    """Load config from a given path.

    This method accepts only a path string to enable efficient
    caching of results.
    """
    # The potential filenames we would look for at this path.
    # NB: later in this list overwrites earlier
    filename_options = [
        "setup.cfg",
        "tox.ini",
        "pep8.ini",
        ".sqlfluff",
        "pyproject.toml",
    ]

    configs: ConfigMappingType = {}

    if os.path.isdir(path):
        p = path
    else:
        p = os.path.dirname(path)

    d = os.listdir(os.path.expanduser(p))
    # iterate this way round to make sure things overwrite is the right direction.
    # NOTE: The `configs` variable is passed back in at each stage.
    for fname in filename_options:
        if fname in d:
            configs = load_config_file(p, fname, configs=configs)

    return configs


def _load_user_appdir_config() -> ConfigMappingType:
    """Load the config from the user's OS specific appdir config directory."""
    user_config_dir_path = _get_user_config_dir_path(sys.platform)
    if os.path.exists(user_config_dir_path):
        return load_config_at_path(user_config_dir_path)
    else:
        return {}


def load_config_up_to_path(
    path: str,
    extra_config_path: Optional[str] = None,
    ignore_local_config: bool = False,
) -> ConfigMappingType:
    """Loads a selection of config files from both the path and its parent paths.

    We layer each of the configs on top of each other, starting with any home
    or user configs (e.g. in appdir or home (`~`)), then any local project
    configuration and then any explicitly specified config paths.
    """
    # 1) AppDir & Home config
    if not ignore_local_config:
        user_appdir_config = _load_user_appdir_config()
        user_config = load_config_at_path(os.path.expanduser("~"))
    else:
        user_config, user_appdir_config = {}, {}

    # 3) Local project config
    parent_config_stack = []
    config_stack = []
    if not ignore_local_config:
        # Finding all paths between here and the home
        # directory. We could start at the root of the filesystem,
        # but depending on the user's setup, this might result in
        # permissions errors.
        parent_config_paths = list(
            iter_intermediate_paths(
                Path(path).absolute(), Path(os.path.expanduser("~"))
            )
        )
        # Stripping off the home directory and the current working
        # directory, since they are both covered by other code
        # here
        parent_config_paths = parent_config_paths[1:-1]
        parent_config_stack = [
            load_config_at_path(str(p.resolve())) for p in list(parent_config_paths)
        ]
        # Resolve paths to ensure caching is accurate.
        config_paths = iter_intermediate_paths(Path(path).absolute(), Path.cwd())
        config_stack = [load_config_at_path(str(p.resolve())) for p in config_paths]

    # 4) Extra config paths
    if not extra_config_path:
        extra_config = {}
    else:
        if not os.path.exists(extra_config_path):
            raise SQLFluffUserError(
                f"Extra config '{extra_config_path}' does not exist."
            )
        # Resolve the path so that the caching is accurate.
        extra_config = load_config_file_as_dict(str(Path(extra_config_path).resolve()))

    return nested_combine(
        user_appdir_config,
        user_config,
        *parent_config_stack,
        *config_stack,
        extra_config,
    )


class ConfigLoader:
    """The class for loading config files.

    NOTE: Deprecated class maintained because it was in our example
    plugin for a long while. Remove once this warning has been live for
    an appropriate amount of time.
    """

    def __init__(self) -> None:  # pragma: no cover
        config_logger.warning(
            "ConfigLoader is deprecated, and no longer necessary. "
            "Please update your plugin to use the config loading functions directly "
            "to remove this message."
        )

    @classmethod
    def get_global(cls) -> ConfigLoader:  # pragma: no cover
        """Get the singleton loader."""
        config_logger.warning(
            "ConfigLoader.get_global() is deprecated, and no longer necessary. "
            "Please update your plugin to use the config loading functions directly "
            "to remove this message."
        )
        return cls()

    def load_config_resource(
        self, package: str, file_name: str
    ) -> ConfigMappingType:  # pragma: no cover
        """Load a config resource.

        NOTE: Deprecated classmethod maintained because it was in our example
        plugin for a long while. Remove once this warning has been live for
        an appropriate amount of time.
        """
        config_logger.warning(
            "ConfigLoader.load_config_resource() is deprecated. Please update "
            "your plugin to call sqlfluff.core.config.loader.load_config_resource() "
            "directly to remove this message."
        )
        return load_config_resource(package, file_name)

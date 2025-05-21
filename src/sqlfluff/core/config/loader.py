"""Config loading methods and helpers.

This is designed to house the main functions which are exposed by the
overall config module. There is some caching in this module, which
is designed around caching the configuration loaded at *specific paths*
rather than the individual file caching in the `file` module.
"""

from __future__ import annotations

import logging
import os
import os.path
import sys
from functools import cache
from importlib.resources import files
from pathlib import Path
from typing import (
    Optional,
)

import platformdirs
import platformdirs.macos
import platformdirs.unix

from sqlfluff.core.config.file import (
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


def _get_user_config_dir_path(sys_platform: str) -> str:
    """Get the user config dir for this system.

    Args:
        sys_platform (str): The result of ``sys.platform()``. Provided
            as an argument here for ease of testing. In normal usage
            it should only be  called with ``sys.platform()``. This
            argument only applies to switching between linux and macos.
            Win32 detection still uses the underlying ``sys.platform()``
            methods.
    """
    appname = "sqlfluff"
    appauthor = "sqlfluff"

    # First try the default SQLFluff specific cross-platform config path.
    cross_platform_path = os.path.expanduser("~/.config/sqlfluff")
    if os.path.exists(cross_platform_path):
        return cross_platform_path

    # Then try the platform specific paths, for MacOS, we check
    # the unix variant first to preferentially use the XDG config path if set.
    # https://github.com/sqlfluff/sqlfluff/issues/889
    if sys_platform == "darwin":
        unix_config_path = platformdirs.unix.Unix(
            appname=appname, appauthor=appauthor
        ).user_config_dir
        if os.path.exists(os.path.expanduser(unix_config_path)):
            return unix_config_path
        # Technically we could just delegate to the generic `user_config_dir`
        # method, but for testing it's convenient to explicitly call the macos
        # methods here.
        return platformdirs.macos.MacOS(
            appname=appname, appauthor=appauthor
        ).user_config_dir
    # NOTE: We could delegate to the generic `user_config_dir` method here,
    # but for testing it's convenient to explicitly call the linux methods.
    elif sys_platform == "linux":
        return platformdirs.unix.Unix(
            appname=appname, appauthor=appauthor
        ).user_config_dir
    # Defer to the self-detecting paths.
    # NOTE: On Windows this means that the `sys_platform` argument is not
    # applied.
    return platformdirs.user_config_dir(appname, appauthor)


def load_config_file(
    file_dir: str, file_name: str, configs: Optional[ConfigMappingType] = None
) -> ConfigMappingType:
    """Load a config file from the filesystem.

    Args:
        file_dir (str): The path to the location of file to be loaded.
            This should be a reference to the directory *only* and not
            include the filename itself. Any paths in the loaded file
            are resolved relative to this location.
        file_name (str): The filename of the file to be loaded. If the
            filename is ``pyproject.toml`` then the file is loaded in
            ``toml`` format, but otherwise is assumed to be in ``ini``
            format (as per ``.sqlfluff``).
        configs (ConfigMappingType, optional): A base set of configs to
            merge the loaded configs onto. If not provided, the result
            will contain only the values loaded from the string.

    Returns:
        :obj:`ConfigMappingType`: A nested dictionary of config values.
    """
    file_path = os.path.join(file_dir, file_name)
    raw_config = load_config_file_as_dict(file_path)
    # We always run `nested_combine()` because it has the side effect
    # of making a copy of the objects provided. This prevents us
    # from editing items which also sit within the cache.
    return nested_combine(configs or {}, raw_config)


def load_config_resource(package: str, file_name: str) -> ConfigMappingType:
    """Load a config resource from a python package.

    Args:
        package (str): The name of the python package to load the resource
            from.
        file_name (str): The filename of the file to be loaded. If the
            filename is ``pyproject.toml`` then the file is loaded in
            ``toml`` format, but otherwise is assumed to be in ``ini``
            format (as per ``.sqlfluff``).

    Returns:
        :obj:`ConfigMappingType`: A nested dictionary of config values.

    This is primarily used when loading configuration bundled with a
    SQLFluff plugin, or to load the default config for SQLFluff itself.
    By loading config from the package directly we avoid some of the
    path resolution which otherwise occurs. This is also more compatible
    with ``mypyc`` because it avoids the use of the ``__file__`` attribute
    to find the default config.

    Any paths found in the loaded config are resolved relative
    to ``os.getcwd()``.

    For more information about resource loading, see the docs for importlib:
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
    """Load a config from a string in ini format.

    Args:
        config_string (str): The raw config file as a string. The content
            is assumed to be in the the ``.ini`` format of a ``.sqlfluff``
            file (i.e. not in ``.toml`` format).
        configs (ConfigMappingType, optional): A base set of configs to
            merge the loaded configs onto. If not provided, the result
            will contain only the values loaded from the string.
        working_path (str, optional): The working path to use for the
            resolution of any paths specified in the config. If not provided
            then ``os.getcwd()`` is used as a default.

    Returns:
        :obj:`ConfigMappingType`: A nested dictionary of config values.
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
    """Load config files at a given path.

    Args:
        path (str): The directory to search for config files.

    Returns:
        :obj:`ConfigMappingType`: A nested dictionary of config values.

    This function will search for all valid config files at the given
    path, load any found and combine them into a config mapping. If
    multiple valid files are found, they are resolved in priority order,
    where ``pyproject.toml`` is given the highest precedence, followed
    by ``.sqlfluff``, ``pep8.ini``, ``tox.ini`` and finally ``setup.cfg``.

    By accepting only a path string, we enable efficient caching of
    results, such that configuration can be reused between files without
    reloading the information from disk.
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

    Args:
        path (str): The directory which is the target of the search. Config
            files in subdirectories will not be loaded by this method, but
            valid config files between this path and the current working
            path will.
        extra_config_path (str, optional): An additional path to load config
            from. This path is not used in iterating through intermediate
            paths, and is loaded last (taking the highest precedence in
            combining the loaded configs).
        ignore_local_config (bool, optional, defaults to False): If set to
            True, this skips loading configuration from the user home
            directory (``~``) or ``appdir`` path.

    Returns:
        :obj:`ConfigMappingType`: A nested dictionary of config values.

    We layer each of the configs on top of each other, starting with any home
    or user configs (e.g. in ``appdir`` or home (``~``)), then any local
    project configuration and then any explicitly specified config paths.
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

    # 4) Extra config paths.
    # When calling `load_config_file_as_dict` we resolve the path first so that caching
    # is more efficient.
    extra_config = {}
    if extra_config_path:
        try:
            extra_config = load_config_file_as_dict(
                str(Path(extra_config_path).resolve())
            )
        except FileNotFoundError:
            raise SQLFluffUserError(
                f"Extra config path '{extra_config_path}' does not exist."
            )

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

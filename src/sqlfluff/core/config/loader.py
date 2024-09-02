"""Module for loading config."""

from __future__ import annotations

try:
    from importlib.resources import files
except ImportError:  # pragma: no cover
    # fallback for python <=3.8
    from importlib_resources import files  # type: ignore

import logging
import os
import os.path
from pathlib import Path
from typing import (
    Dict,
    Iterable,
    List,
    Optional,
    Union,
)

import appdirs

from sqlfluff.core.config.cache import (
    load_config_file_as_dict,
    load_config_string_as_dict,
)
from sqlfluff.core.config.removed import REMOVED_CONFIGS
from sqlfluff.core.config.types import ConfigMappingType, ConfigRecordType
from sqlfluff.core.errors import SQLFluffUserError
from sqlfluff.core.helpers.dict import nested_combine
from sqlfluff.core.helpers.file import iter_intermediate_paths

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


class ConfigLoader:
    """The class for loading config files.

    Note:
        Unlike most cfg file readers, sqlfluff is case-sensitive in how
        it reads config files. This is to ensure we support the case
        sensitivity of jinja.

    """

    def __init__(self) -> None:
        # TODO: check that this cache implementation is actually useful
        self._config_cache: Dict[str, ConfigMappingType] = {}

    @classmethod
    def get_global(cls) -> ConfigLoader:
        """Get the singleton loader."""
        global global_loader
        if not global_loader:
            global_loader = cls()
        return global_loader

    @staticmethod
    def _validate_configs(
        configs: Iterable[ConfigRecordType], file_path: str
    ) -> List[ConfigRecordType]:
        """Validate config elements.

        We validate in two ways:
        1. Are these config settings removed or deprecated.
        2. Are these config elements in the layout section _valid_.
        """
        config_map = {cfg.old_path: cfg for cfg in REMOVED_CONFIGS}
        # Materialise the configs into a list to we can iterate twice.
        new_configs = list(configs)
        defined_keys = {k for k, _ in new_configs}
        validated_configs = []
        for k, v in new_configs:
            # First validate against the removed option list.
            if k in config_map.keys():
                removed_option = config_map[k]
                # Is there a mapping option?
                if removed_option.translation_func and removed_option.new_path:
                    # Before mutating, check we haven't _also_ set the new value.
                    if removed_option.new_path in defined_keys:
                        # Raise an warning.
                        config_logger.warning(
                            f"\nWARNING: Config file {file_path} set a deprecated "
                            f"config value {removed_option.formatted_old_key!r} "
                            "(which can be migrated) "
                            f"but ALSO set the value it would be migrated to. The new "
                            f"value ({removed_option.formatted_new_key!r}) takes "
                            "precedence. "
                            "Please update your configuration to remove this warning. "
                            f"\n\n{removed_option.warning}\n\n"
                            "See https://docs.sqlfluff.com/en/stable/perma/"
                            "configuration.html for more details.\n"
                        )
                        # continue to NOT add this value in the set
                        continue

                    # Mutate and warn.
                    v = removed_option.translation_func(v)
                    k = removed_option.new_path
                    # NOTE: At the stage of emitting this warning, we may not yet
                    # have set up red logging because we haven't yet loaded the config
                    # file. For that reason, this error message has a bit more padding.
                    config_logger.warning(
                        f"\nWARNING: Config file {file_path} set a deprecated config "
                        f"value {removed_option.formatted_old_key!r}. This will be "
                        "removed in a later release. This has been mapped to "
                        f"{removed_option.formatted_new_key!r} set to a value of "
                        f"`{v}` for this run. "
                        "Please update your configuration to remove this warning. "
                        f"\n\n{removed_option.warning}\n\n"
                        "See https://docs.sqlfluff.com/en/stable/perma/"
                        "configuration.html for more details.\n"
                    )
                else:
                    # Raise an error.
                    raise SQLFluffUserError(
                        f"Config file {file_path!r} set an outdated config "
                        f"value {removed_option.formatted_old_key!r}."
                        f"\n\n{removed_option.warning}\n\n"
                        "See https://docs.sqlfluff.com/en/stable/perma/"
                        "configuration.html for more details."
                    )

            # Second validate any layout configs for validity.
            # NOTE: For now we don't check that the "type" is a valid one
            # to reference, or that the values are valid. For the values,
            # these are likely to be rejected by the layout routines at
            # runtime. The last risk area is validating that the type is
            # a valid one.
            if k and k[0] == "layout":
                # Check for:
                # - Key length
                # - Key values
                if (
                    # Key length must be 4
                    (len(k) != 4)
                    # Second value must (currently) be "type"
                    or (k[1] != "type")
                    # Last key value must be one of the allowable options.
                    or (k[3] not in ALLOWABLE_LAYOUT_CONFIG_KEYS)
                ):
                    raise SQLFluffUserError(
                        f"Config file {file_path!r} set an invalid `layout` option "
                        f"value {':'.join(k)}.\n"
                        "See https://docs.sqlfluff.com/en/stable/perma/layout.html"
                        "#configuring-layout for more details."
                    )

            validated_configs.append((k, v))
        return validated_configs

    def load_config_resource(self, package: str, file_name: str) -> ConfigMappingType:
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
        raw_config = load_config_string_as_dict(
            config_string,
            os.getcwd(),
            logging_reference=f"<resource {package}.{file_name}>",
        )
        if not configs:
            return raw_config
        return nested_combine(configs, raw_config)

    def load_config_file(
        self, file_dir: str, file_name: str, configs: Optional[ConfigMappingType] = None
    ) -> ConfigMappingType:
        """Load a config file."""
        file_path = os.path.join(file_dir, file_name)
        raw_config = load_config_file_as_dict(file_path)
        if not configs:
            return raw_config
        return nested_combine(configs, raw_config)

    def load_config_string(
        self,
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
        if not configs:
            return raw_config
        return nested_combine(configs, raw_config)

    def load_config_at_path(self, path: Union[str, Path]) -> ConfigMappingType:
        """Load config from a given path."""
        # If we've been passed a Path object, resolve it.
        if isinstance(path, Path):
            path = str(path.resolve())

        # First check the cache
        if str(path) in self._config_cache:
            return self._config_cache[str(path)]

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
        # iterate this way round to make sure things overwrite is the right direction
        for fname in filename_options:
            if fname in d:
                configs = self.load_config_file(p, fname, configs=configs)

        # Store in the cache
        self._config_cache[str(path)] = configs
        return configs

    def load_extra_config(self, extra_config_path: str) -> ConfigMappingType:
        """Load specified extra config."""
        if not os.path.exists(extra_config_path):
            raise SQLFluffUserError(
                f"Extra config '{extra_config_path}' does not exist."
            )

        # First check the cache
        if str(extra_config_path) in self._config_cache:
            return self._config_cache[str(extra_config_path)]

        configs = load_config_file_as_dict(extra_config_path)

        # Store in the cache
        self._config_cache[str(extra_config_path)] = configs
        return configs

    @staticmethod
    def _get_user_config_dir_path() -> str:
        appname = "sqlfluff"
        appauthor = "sqlfluff"

        # On Mac OSX follow Linux XDG base dirs
        # https://github.com/sqlfluff/sqlfluff/issues/889
        user_config_dir_path = os.path.expanduser("~/.config/sqlfluff")
        if appdirs.system == "darwin":
            appdirs.system = "linux2"
            user_config_dir_path = appdirs.user_config_dir(appname, appauthor)
            appdirs.system = "darwin"

        if not os.path.exists(user_config_dir_path):
            user_config_dir_path = appdirs.user_config_dir(appname, appauthor)

        return user_config_dir_path

    def load_user_appdir_config(self) -> ConfigMappingType:
        """Load the config from the user's OS specific appdir config directory."""
        user_config_dir_path = self._get_user_config_dir_path()
        if os.path.exists(user_config_dir_path):
            return self.load_config_at_path(user_config_dir_path)
        else:
            return {}

    def load_user_config(self) -> ConfigMappingType:
        """Load the config from the user's home directory."""
        user_home_path = os.path.expanduser("~")
        return self.load_config_at_path(user_home_path)

    def load_config_up_to_path(
        self,
        path: str,
        extra_config_path: Optional[str] = None,
        ignore_local_config: bool = False,
    ) -> ConfigMappingType:
        """Loads a selection of config files from both the path and its parent paths."""
        user_appdir_config = (
            self.load_user_appdir_config() if not ignore_local_config else {}
        )
        user_config = self.load_user_config() if not ignore_local_config else {}
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
                self.load_config_at_path(p) for p in list(parent_config_paths)
            ]

            config_paths = iter_intermediate_paths(Path(path).absolute(), Path.cwd())
            config_stack = [self.load_config_at_path(p) for p in config_paths]
        extra_config = (
            self.load_extra_config(extra_config_path) if extra_config_path else {}
        )
        return nested_combine(
            user_appdir_config,
            user_config,
            *parent_config_stack,
            *config_stack,
            extra_config,
        )

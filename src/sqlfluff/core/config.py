"""Module for loading config."""

from __future__ import annotations

try:
    from importlib.resources import files
except ImportError:  # pragma: no cover
    # fallback for python <=3.8
    from importlib_resources import files  # type: ignore

import configparser
import logging
import os
import os.path
import sys
from dataclasses import dataclass
from itertools import chain
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
)

import appdirs
import pluggy

from sqlfluff.core.errors import SQLFluffUserError
from sqlfluff.core.helpers.dict import dict_diff, nested_combine
from sqlfluff.core.helpers.file import iter_intermediate_paths
from sqlfluff.core.helpers.string import (
    split_colon_separated_string,
    split_comma_separated_string,
)
from sqlfluff.core.plugin.host import get_plugin_manager

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.templaters.base import RawTemplater

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import toml as tomllib

# Instantiate the config logger
config_logger = logging.getLogger("sqlfluff.config")

global_loader = None
""":obj:`ConfigLoader`: A variable to hold the single module loader when loaded.

We define a global loader, so that between calls to load config, we
can still cache appropriately
"""

ConfigElemType = Tuple[Tuple[str, ...], Any]


ALLOWABLE_LAYOUT_CONFIG_KEYS = (
    "spacing_before",
    "spacing_after",
    "spacing_within",
    "line_position",
    "align_within",
    "align_scope",
)


@dataclass
class _RemovedConfig:
    old_path: Tuple[str, ...]
    warning: str
    new_path: Optional[Tuple[str, ...]] = None
    translation_func: Optional[Callable[[str], str]] = None


REMOVED_CONFIGS = [
    _RemovedConfig(
        ("rules", "L003", "hanging_indents"),
        (
            "Hanging indents are no longer supported in SQLFluff "
            "from version 2.0.0 onwards. See "
            "https://docs.sqlfluff.com/en/stable/layout.html#hanging-indents"
        ),
    ),
    _RemovedConfig(
        ("rules", "max_line_length"),
        (
            "The max_line_length config has moved "
            "from sqlfluff:rules to the root sqlfluff level."
        ),
        ("max_line_length",),
        (lambda x: x),
    ),
    _RemovedConfig(
        ("rules", "tab_space_size"),
        (
            "The tab_space_size config has moved "
            "from sqlfluff:rules to sqlfluff:indentation."
        ),
        ("indentation", "tab_space_size"),
        (lambda x: x),
    ),
    _RemovedConfig(
        ("rules", "L002", "tab_space_size"),
        (
            "The tab_space_size config has moved "
            "from sqlfluff:rules to sqlfluff:indentation."
        ),
        ("indentation", "tab_space_size"),
        (lambda x: x),
    ),
    _RemovedConfig(
        ("rules", "L003", "tab_space_size"),
        (
            "The tab_space_size config has moved "
            "from sqlfluff:rules to sqlfluff:indentation."
        ),
        ("indentation", "tab_space_size"),
        (lambda x: x),
    ),
    _RemovedConfig(
        ("rules", "L004", "tab_space_size"),
        (
            "The tab_space_size config has moved "
            "from sqlfluff:rules to sqlfluff:indentation."
        ),
        ("indentation", "tab_space_size"),
        (lambda x: x),
    ),
    _RemovedConfig(
        ("rules", "L016", "tab_space_size"),
        (
            "The tab_space_size config has moved "
            "from sqlfluff:rules to sqlfluff:indentation."
        ),
        ("indentation", "tab_space_size"),
        (lambda x: x),
    ),
    _RemovedConfig(
        ("rules", "indent_unit"),
        (
            "The indent_unit config has moved "
            "from sqlfluff:rules to sqlfluff:indentation."
        ),
        ("indentation", "indent_unit"),
        (lambda x: x),
    ),
    _RemovedConfig(
        ("rules", "LT03", "operator_new_lines"),
        (
            "Use the line_position config in the appropriate "
            "sqlfluff:layout section (e.g. sqlfluff:layout:type"
            ":binary_operator)."
        ),
        ("layout", "type", "binary_operator", "line_position"),
        (lambda x: "trailing" if x == "before" else "leading"),
    ),
    _RemovedConfig(
        ("rules", "comma_style"),
        (
            "Use the line_position config in the appropriate "
            "sqlfluff:layout section (e.g. sqlfluff:layout:type"
            ":comma)."
        ),
        ("layout", "type", "comma", "line_position"),
        (lambda x: x),
    ),
    # LT04 used to have a more specific version of the same /config itself.
    _RemovedConfig(
        ("rules", "LT04", "comma_style"),
        (
            "Use the line_position config in the appropriate "
            "sqlfluff:layout section (e.g. sqlfluff:layout:type"
            ":comma)."
        ),
        ("layout", "type", "comma", "line_position"),
        (lambda x: x),
    ),
    _RemovedConfig(
        ("rules", "L003", "lint_templated_tokens"),
        "No longer used.",
    ),
    _RemovedConfig(
        ("core", "recurse"),
        "Removed as unused in production and unnecessary for debugging.",
    ),
]


def coerce_value(val: str) -> Any:
    """Try to coerce to a more specific type."""
    # Try to coerce it to a more specific type,
    # otherwise just make it a string.
    try:
        v: Any = int(val)
    except ValueError:
        try:
            v = float(val)
        except ValueError:
            cleaned_val = val.strip().lower()
            if cleaned_val in ["true"]:
                v = True
            elif cleaned_val in ["false"]:
                v = False
            elif cleaned_val in ["none"]:
                v = None
            else:
                v = val
    return v


class ConfigLoader:
    """The class for loading config files.

    Note:
        Unlike most cfg file readers, sqlfluff is case-sensitive in how
        it reads config files. This is to ensure we support the case
        sensitivity of jinja.

    """

    def __init__(self) -> None:
        # TODO: check that this cache implementation is actually useful
        self._config_cache: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def get_global(cls) -> ConfigLoader:
        """Get the singleton loader."""
        global global_loader
        if not global_loader:
            global_loader = cls()
        return global_loader

    @classmethod
    def _walk_toml(
        cls, config: Dict[str, Any], base_key: Tuple[str, ...] = ()
    ) -> List[Tuple[Tuple[str, ...], Any]]:
        """Recursively walk the nested config inside a TOML file.

        For standard usage it mimics the standard loader.

        >>> ConfigLoader._walk_toml({"foo": "bar"})
        [(('foo',), 'bar')]
        >>> ConfigLoader._walk_toml({"foo": {"bar": "baz"}})
        [(('foo', 'bar'), 'baz')]

        For the "rules" section, there's a special handling
        to condense nested sections from the toml for rules
        which contain a dot (or more) (".") in their name.

        >>> ConfigLoader._walk_toml({"rules": {"a": {"b": {"c": "d"}}}})
        [(('rules', 'a.b', 'c'), 'd')]
        >>> ConfigLoader._walk_toml({"rules":
        ...     {"capitalisation": {"keywords":
        ...         {"capitalisation_policy": "upper"}
        ...     }}
        ... })
        [(('rules', 'capitalisation.keywords', 'capitalisation_policy'), 'upper')]

        NOTE: Some rules make have more than one dot in their name.
        >>> ConfigLoader._walk_toml({"rules":
        ...     {"a": {"b": {"c": {"d": {"e": "f"}}}}}
        ... })
        [(('rules', 'a.b.c.d', 'e'), 'f')]
        """
        buff: List[Tuple[Tuple[str, ...], Any]] = []
        # NOTE: For the "rules" section of the sqlfluff config,
        # rule names are often qualified with a dot ".". In the
        # toml scenario this can get interpreted as a nested
        # section, and we resolve that edge case here.
        if len(base_key) == 3 and base_key[0] == "rules":
            base_key = ("rules", ".".join(base_key[1:]))

        for k, v in config.items():
            key = base_key + (k,)
            if isinstance(v, dict):
                buff.extend(cls._walk_toml(v, key))
            else:
                buff.append((key, v))

        return buff

    @classmethod
    def _iter_config_elems_from_dict(
        cls, configs: Dict[str, Any]
    ) -> Iterator[ConfigElemType]:
        """Walk a config dict and get config elements.

        >>> list(
        ...    ConfigLoader._iter_config_elems_from_dict(
        ...        {"foo":{"bar":{"baz": "a", "biz": "b"}}}
        ...    )
        ... )
        [(('foo', 'bar', 'baz'), 'a'), (('foo', 'bar', 'biz'), 'b')]
        """
        for key, val in configs.items():
            if isinstance(val, dict):
                for partial_key, sub_val in cls._iter_config_elems_from_dict(val):
                    yield (key,) + partial_key, sub_val
            else:
                yield (key,), val

    @classmethod
    def _config_elems_to_dict(cls, configs: Iterable[ConfigElemType]) -> Dict[str, Any]:
        """Reconstruct config elements into a dict.

        >>> ConfigLoader._config_elems_to_dict(
        ...     [(("foo", "bar", "baz"), "a"), (("foo", "bar", "biz"), "b")]
        ... )
        {'foo': {'bar': {'baz': 'a', 'biz': 'b'}}}
        """
        result: Dict[str, Any] = {}
        for key, val in configs:
            ref = result
            for step in key[:-1]:
                if step not in ref:
                    ref[step] = {}
                ref = ref[step]
            ref[key[-1]] = val
        return result

    @classmethod
    def _get_config_elems_from_toml(cls, fpath: str) -> List[ConfigElemType]:
        """Load a config from a TOML file and return a list of tuples.

        The return value is a list of tuples, were each tuple has two elements,
        the first is a tuple of paths, the second is the value at that path.
        """
        with open(fpath, mode="r") as file:
            config = tomllib.loads(file.read())
        tool = config.get("tool", {}).get("sqlfluff", {})

        return cls._walk_toml(tool)

    @classmethod
    def _get_config_elems_from_file(
        cls, fpath: Optional[str] = None, config_string: Optional[str] = None
    ) -> List[ConfigElemType]:
        """Load a config from a file and return a list of tuples.

        The return value is a list of tuples, were each tuple has two elements,
        the first is a tuple of paths, the second is the value at that path.

        Note:
            Unlike most cfg file readers, sqlfluff is case-sensitive in how
            it reads config files.

        Note:
            Any variable names ending with `_path` or `_dir`, will be attempted to be
            resolved as relative paths to this config file. If that fails the
            string value will remain.

        """
        assert fpath or config_string, "One of fpath or config_string is required."
        buff: List[ConfigElemType] = []
        # Disable interpolation so we can load macros
        kw: Dict[str, Any] = {}
        kw["interpolation"] = None
        config = configparser.ConfigParser(delimiters="=", **kw)
        # NB: We want to be case sensitive in how we read from files,
        # because jinja is also case sensitive. To do this we override
        # the optionxform attribute.
        config.optionxform = lambda option: option  # type: ignore
        if fpath:
            config.read(fpath)
        else:
            assert config_string
            config.read_string(config_string)
            # Set the fpath to the current working directory
            fpath = os.getcwd()

        for k in config.sections():
            if k == "sqlfluff":
                key: Tuple[str, ...] = ("core",)
            elif k.startswith("sqlfluff:"):
                # Return a tuple of nested values
                key = tuple(k[len("sqlfluff:") :].split(":"))
            else:  # pragma: no cover
                # if it doesn't start with sqlfluff, then don't go
                # further on this iteration
                continue

            for name, val in config.items(section=k):
                # Try to coerce it to a more specific type,
                # otherwise just make it a string.
                v = coerce_value(val)

                # Attempt to resolve paths
                if name.lower() == "load_macros_from_path":
                    # Comma-separated list of paths.
                    paths = split_comma_separated_string(val)
                    v_temp = []
                    for path in paths:
                        v_temp.append(cls._resolve_path(fpath, path))
                    v = ",".join(v_temp)
                elif name.lower().endswith(("_path", "_dir")):
                    # One path
                    v = cls._resolve_path(fpath, val)
                # Add the name to the end of the key
                buff.append((key + (name,), v))
        return buff

    @classmethod
    def _resolve_path(cls, fpath: str, val: str) -> str:
        """Try to resolve a path."""
        # Make the referenced path.
        ref_path = os.path.join(os.path.dirname(fpath), val)
        # Check if it exists, and if it does, replace the value with the path.
        return ref_path if os.path.exists(ref_path) else val

    @staticmethod
    def _incorporate_vals(
        ctx: Dict[str, Any], vals: List[ConfigElemType]
    ) -> Dict[str, Any]:
        """Take a list of tuples and incorporate it into a dictionary.

        >>> ConfigLoader._incorporate_vals({}, [(("a", "b"), "c")])
        {'a': {'b': 'c'}}
        >>> ConfigLoader._incorporate_vals({"a": {"b": "c"}}, [(("a", "d"), "e")])
        {'a': {'b': 'c', 'd': 'e'}}
        """
        for k, v in vals:
            # Keep a ref we can use for recursion
            r = ctx
            # Get the name of the variable
            n = k[-1]
            # Get the path
            pth = k[:-1]
            for dp in pth:
                # Does this path exist?
                if dp in r:
                    if isinstance(r[dp], dict):
                        r = r[dp]
                    else:  # pragma: no cover
                        raise ValueError(f"Overriding config value with section! [{k}]")
                else:
                    r[dp] = {}
                    r = r[dp]
            # Deal with the value itself
            r[n] = v
        return ctx

    @staticmethod
    def _validate_configs(
        configs: Iterable[ConfigElemType], file_path: str
    ) -> List[ConfigElemType]:
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
                formatted_key = ":".join(k)
                removed_option = config_map[k]
                # Is there a mapping option?
                if removed_option.translation_func and removed_option.new_path:
                    formatted_new_key = ":".join(removed_option.new_path)
                    # Before mutating, check we haven't _also_ set the new value.
                    if removed_option.new_path in defined_keys:
                        # Raise an warning.
                        config_logger.warning(
                            f"\nWARNING: Config file {file_path} set a deprecated "
                            f"config value `{formatted_key}` (which can be migrated) "
                            f"but ALSO set the value it would be migrated to. The new "
                            f"value (`{removed_option.new_path}`) takes precedence. "
                            "Please update your configuration to remove this warning. "
                            f"\n\n{removed_option.warning}\n\n"
                            "See https://docs.sqlfluff.com/en/stable/configuration.html"
                            " for more details.\n"
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
                        f"value `{formatted_key}`. This will be removed in a later "
                        "release. This has been mapped to "
                        f"`{formatted_new_key}` set to a value of `{v}` for this run. "
                        "Please update your configuration to remove this warning. "
                        f"\n\n{removed_option.warning}\n\n"
                        "See https://docs.sqlfluff.com/en/stable/configuration.html"
                        " for more details.\n"
                    )
                else:
                    # Raise an error.
                    raise SQLFluffUserError(
                        f"Config file {file_path!r} set an outdated config "
                        f"value {formatted_key}.\n\n{removed_option.warning}\n\n"
                        "See https://docs.sqlfluff.com/en/stable/configuration.html"
                        " for more details."
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
                        "See https://docs.sqlfluff.com/en/stable/layout.html"
                        "#configuring-layout for more details."
                    )

            validated_configs.append((k, v))
        return validated_configs

    def load_config_resource(
        self, package: str, file_name: str, configs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Load a config resource.

        This is however more compatible with mypyc because it avoids
        the use of the __file__ object to find the default config.

        This is only tested extensively with the default config.

        NOTE: This requires that the config file is built into
        a package but should be more performant because it leverages
        importlib.
        https://docs.python.org/3/library/importlib.resources.html
        """
        config_string = files(package).joinpath(file_name).read_text()
        elems = self._get_config_elems_from_file(config_string=config_string)
        elems = self._validate_configs(elems, package + "." + file_name)
        return self._incorporate_vals(configs or {}, elems)

    def load_config_file(
        self, file_dir: str, file_name: str, configs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Load a config file."""
        file_path = os.path.join(file_dir, file_name)
        if file_name == "pyproject.toml":
            elems = self._get_config_elems_from_toml(file_path)
        else:
            elems = self._get_config_elems_from_file(file_path)
        elems = self._validate_configs(elems, file_path)
        return self._incorporate_vals(configs or {}, elems)

    def load_config_string(
        self, config_string: str, configs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Load a config from the string in cfg format."""
        elems = self._get_config_elems_from_file(config_string=config_string)
        elems = self._validate_configs(elems, "<config string>")
        return self._incorporate_vals(configs or {}, elems)

    def load_config_at_path(self, path: Union[str, Path]) -> Dict[str, Any]:
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

        configs: Dict[str, Any] = {}

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

    def load_extra_config(self, extra_config_path: str) -> Dict[str, Any]:
        """Load specified extra config."""
        if not os.path.exists(extra_config_path):
            raise SQLFluffUserError(
                f"Extra config '{extra_config_path}' does not exist."
            )

        # First check the cache
        if str(extra_config_path) in self._config_cache:
            return self._config_cache[str(extra_config_path)]

        configs: Dict[str, Any] = {}
        if extra_config_path.endswith("pyproject.toml"):
            elems = self._get_config_elems_from_toml(extra_config_path)
        else:
            elems = self._get_config_elems_from_file(extra_config_path)
        configs = self._incorporate_vals(configs, elems)

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

    def load_user_appdir_config(self) -> Dict[str, Any]:
        """Load the config from the user's OS specific appdir config directory."""
        user_config_dir_path = self._get_user_config_dir_path()
        if os.path.exists(user_config_dir_path):
            return self.load_config_at_path(user_config_dir_path)
        else:
            return {}

    def load_user_config(self) -> Dict[str, Any]:
        """Load the config from the user's home directory."""
        user_home_path = os.path.expanduser("~")
        return self.load_config_at_path(user_home_path)

    def load_config_up_to_path(
        self,
        path: str,
        extra_config_path: Optional[str] = None,
        ignore_local_config: bool = False,
    ) -> Dict[str, Any]:
        """Loads a selection of config files from both the path and its parent paths."""
        user_appdir_config = (
            self.load_user_appdir_config() if not ignore_local_config else {}
        )
        user_config = self.load_user_config() if not ignore_local_config else {}
        config_paths = (
            iter_intermediate_paths(Path(path).absolute(), Path.cwd())
            if not ignore_local_config
            else {}
        )
        config_stack = (
            [self.load_config_at_path(p) for p in config_paths]
            if not ignore_local_config
            else []
        )
        extra_config = (
            self.load_extra_config(extra_config_path) if extra_config_path else {}
        )
        return nested_combine(
            user_appdir_config, user_config, *config_stack, extra_config
        )

    @classmethod
    def find_ignore_config_files(
        cls,
        path: str,
        working_path: Union[str, Path] = Path.cwd(),
        ignore_file_name: str = ".sqlfluffignore",
    ) -> Set[str]:
        """Finds sqlfluff ignore files from both the path and its parent paths."""
        _working_path: Path = (
            Path(working_path) if isinstance(working_path, str) else working_path
        )
        return set(
            filter(
                os.path.isfile,
                map(
                    lambda x: os.path.join(x, ignore_file_name),
                    iter_intermediate_paths(Path(path).absolute(), _working_path),
                ),
            )
        )


class FluffConfig:
    """The class that actually gets passed around as a config object."""

    private_vals = "rule_denylist", "rule_allowlist", "dialect_obj", "templater_obj"

    def __init__(
        self,
        configs: Optional[Dict[str, Any]] = None,
        extra_config_path: Optional[str] = None,
        ignore_local_config: bool = False,
        overrides: Optional[Dict[str, Any]] = None,
        plugin_manager: Optional[pluggy.PluginManager] = None,
        # Ideally a dialect should be set when config is read but sometimes
        # it might only be set in nested .sqlfluff config files, so allow it
        # to be not required.
        require_dialect: bool = True,
    ):
        self._extra_config_path = (
            extra_config_path  # We only store this for child configs
        )
        self._ignore_local_config = (
            ignore_local_config  # We only store this for child configs
        )
        # If overrides are provided, validate them early.
        if overrides:
            overrides = ConfigLoader._config_elems_to_dict(
                ConfigLoader._validate_configs(
                    [
                        (("core",) + k, v)
                        for k, v in ConfigLoader._iter_config_elems_from_dict(overrides)
                    ],
                    "<provided overrides>",
                )
            )["core"]
        self._overrides = overrides  # We only store this for child configs

        # Fetch a fresh plugin manager if we weren't provided with one
        self._plugin_manager = plugin_manager or get_plugin_manager()

        defaults = nested_combine(*self._plugin_manager.hook.load_default_config())
        # If any existing configs are provided. Validate them:
        if configs:
            configs = ConfigLoader._config_elems_to_dict(
                ConfigLoader._validate_configs(
                    ConfigLoader._iter_config_elems_from_dict(configs),
                    "<provided configs>",
                )
            )
        self._configs = nested_combine(
            defaults, configs or {"core": {}}, {"core": overrides or {}}
        )
        # Some configs require special treatment
        self._configs["core"]["color"] = (
            False if self._configs["core"].get("nocolor", False) else None
        )
        # Handle inputs which are potentially comma separated strings
        for in_key, out_key in [
            # Deal with potential ignore & warning parameters
            ("ignore", "ignore"),
            ("warnings", "warnings"),
            ("rules", "rule_allowlist"),
            # Allowlists and denylistsignore_words
            ("exclude_rules", "rule_denylist"),
        ]:
            if self._configs["core"].get(in_key, None):
                # Checking if key is string as can potentially be a list to
                self._configs["core"][out_key] = split_comma_separated_string(
                    self._configs["core"][in_key]
                )
            else:
                self._configs["core"][out_key] = []

        # Dialect and Template selection.
        dialect: Optional[str] = self._configs["core"]["dialect"]
        self._initialise_dialect(dialect, require_dialect)

        self._configs["core"]["templater_obj"] = self.get_templater(
            self._configs["core"]["templater"]
        )

    def _initialise_dialect(
        self, dialect: Optional[str], require_dialect: bool = True
    ) -> None:
        # NB: We import here to avoid a circular references.
        from sqlfluff.core.dialects import dialect_selector

        if dialect is not None:
            self._configs["core"]["dialect_obj"] = dialect_selector(
                self._configs["core"]["dialect"]
            )
        elif require_dialect:
            self.verify_dialect_specified()

    def verify_dialect_specified(self) -> None:
        """Check if the config specifies a dialect, raising an error if not."""
        dialect: Optional[str] = self._configs["core"]["dialect"]
        if dialect is None:
            # Get list of available dialects for the error message. We must
            # import here rather than at file scope in order to avoid a circular
            # import.
            from sqlfluff.core.dialects import dialect_readout

            raise SQLFluffUserError(
                "No dialect was specified. You must configure a dialect or "
                "specify one on the command line using --dialect after the "
                "command. Available dialects:\n"
                f"{', '.join([d.label for d in dialect_readout()])}"
            )

    def __getstate__(self) -> Dict[str, Any]:
        # Copy the object's state from self.__dict__ which contains
        # all our instance attributes. Always use the dict.copy()
        # method to avoid modifying the original state.
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        del state["_plugin_manager"]
        # The dbt templater doesn't pickle well, but isn't required
        # within threaded operations. If it was, it could easily be
        # rehydrated within the thread.
        state["_configs"]["core"].pop("templater_obj", None)
        return state

    def __setstate__(self, state: Dict[str, Any]) -> None:  # pragma: no cover
        # Restore instance attributes
        self.__dict__.update(state)
        # NB: We don't reinstate the plugin manager, but this should only
        # be happening between processes where the plugin manager should
        # probably be fresh in any case.
        # NOTE: This means that registering user plugins directly will only
        # work if those plugins are used in the main process (i.e. templaters).
        # User registered linting rules either must be "installed" and therefore
        # available to all processes - or their use is limited to only single
        # process invocations of sqlfluff. In the event that user registered
        # rules are used in a multi-process invocation, they will not be applied
        # in the child processes.
        # NOTE: Likewise we don't reinstate the "templater_obj" config value
        # which should also only be used in the main thread rather than child
        # processes.

    @classmethod
    def from_root(
        cls,
        extra_config_path: Optional[str] = None,
        ignore_local_config: bool = False,
        overrides: Optional[Dict[str, Any]] = None,
        **kw: Any,
    ) -> FluffConfig:
        """Loads a config object just based on the root directory."""
        loader = ConfigLoader.get_global()
        c = loader.load_config_up_to_path(
            path=".",
            extra_config_path=extra_config_path,
            ignore_local_config=ignore_local_config,
        )
        return cls(
            configs=c,
            extra_config_path=extra_config_path,
            ignore_local_config=ignore_local_config,
            overrides=overrides,
            **kw,
        )

    @classmethod
    def from_string(
        cls,
        config_string: str,
        extra_config_path: Optional[str] = None,
        ignore_local_config: bool = False,
        overrides: Optional[Dict[str, Any]] = None,
        plugin_manager: Optional[pluggy.PluginManager] = None,
    ) -> FluffConfig:
        """Loads a config object from a single config string."""
        loader = ConfigLoader.get_global()
        c = loader.load_config_string(config_string)
        return cls(
            configs=c,
            extra_config_path=extra_config_path,
            ignore_local_config=ignore_local_config,
            overrides=overrides,
            plugin_manager=plugin_manager,
        )

    @classmethod
    def from_strings(
        cls,
        *config_strings: str,
        extra_config_path: Optional[str] = None,
        ignore_local_config: bool = False,
        overrides: Optional[Dict[str, Any]] = None,
        plugin_manager: Optional[pluggy.PluginManager] = None,
    ) -> FluffConfig:
        """Loads a config object given a series of nested config strings.

        Config strings are incorporated from first to last, treating the
        first element as the "root" config, and then later config strings
        will take precedence over any earlier values.
        """
        loader = ConfigLoader.get_global()
        config_state: Dict[str, Any] = {}
        for config_string in config_strings:
            config_state = loader.load_config_string(
                config_string, configs=config_state
            )
        return cls(
            configs=config_state,
            extra_config_path=extra_config_path,
            ignore_local_config=ignore_local_config,
            overrides=overrides,
            plugin_manager=plugin_manager,
        )

    @classmethod
    def from_path(
        cls,
        path: str,
        extra_config_path: Optional[str] = None,
        ignore_local_config: bool = False,
        overrides: Optional[Dict[str, Any]] = None,
        plugin_manager: Optional[pluggy.PluginManager] = None,
    ) -> FluffConfig:
        """Loads a config object given a particular path."""
        loader = ConfigLoader.get_global()
        c = loader.load_config_up_to_path(
            path=path,
            extra_config_path=extra_config_path,
            ignore_local_config=ignore_local_config,
        )
        return cls(
            configs=c,
            extra_config_path=extra_config_path,
            ignore_local_config=ignore_local_config,
            overrides=overrides,
            plugin_manager=plugin_manager,
        )

    @classmethod
    def from_kwargs(
        cls,
        config: Optional[FluffConfig] = None,
        dialect: Optional[str] = None,
        rules: Optional[List[str]] = None,
        exclude_rules: Optional[List[str]] = None,
        require_dialect: bool = True,
    ) -> FluffConfig:
        """Instantiate a config from either an existing config or kwargs.

        This is a convenience method for the ways that the public classes
        like Linter(), Parser() and Lexer() can be instantiated with a
        FluffConfig or with the convenience kwargs: dialect & rules.
        """
        if (dialect or rules) and config:  # pragma: no cover
            raise ValueError(
                "Cannot specify `config` with `dialect` or `rules`. Any config object "
                "specifies its own dialect and rules."
            )
        elif config:
            return config

        overrides = {}
        if dialect:
            overrides["dialect"] = dialect
        if rules:
            # Make a comma separated string to pass in as override
            overrides["rules"] = ",".join(rules)
        if exclude_rules:
            # Make a comma separated string to pass in as override
            overrides["exclude_rules"] = ",".join(exclude_rules)

        return cls(overrides=overrides, require_dialect=require_dialect)

    def get_templater(
        self, templater_name: str = "jinja", **kwargs: Any
    ) -> "RawTemplater":
        """Fetch a templater by name."""
        templater_lookup: Dict[str, Type["RawTemplater"]] = {
            templater.name: templater
            for templater in chain.from_iterable(
                self._plugin_manager.hook.get_templaters()
            )
        }
        try:
            cls = templater_lookup[templater_name]
            # Instantiate here, optionally with kwargs
            return cls(**kwargs)
        except KeyError:
            if templater_name == "dbt":  # pragma: no cover
                config_logger.warning(
                    "Starting in sqlfluff version 0.7.0 the dbt templater is "
                    "distributed as a separate python package. Please pip install "
                    "sqlfluff-templater-dbt to use it."
                )
            raise SQLFluffUserError(
                "Requested templater {!r} which is not currently available. Try one of "
                "{}".format(templater_name, ", ".join(templater_lookup.keys()))
            )

    def make_child_from_path(self, path: str) -> FluffConfig:
        """Make a child config at a path but pass on overrides and extra_config_path."""
        return self.from_path(
            path,
            extra_config_path=self._extra_config_path,
            ignore_local_config=self._ignore_local_config,
            overrides=self._overrides,
            plugin_manager=self._plugin_manager,
        )

    def diff_to(self, other: FluffConfig) -> Dict[str, Any]:
        """Compare this config to another.

        Args:
            other (:obj:`FluffConfig`): Another config object to compare
                against. We will return keys from *this* object that are
                not in `other` or are different to those in `other`.

        Returns:
            A filtered dict of items in this config that are not in the other
            or are different to the other.

        """
        # We ignore some objects which are not meaningful in the comparison
        # e.g. dialect_obj, which is generated on the fly.
        return dict_diff(self._configs, other._configs, ignore=["dialect_obj"])

    def get(
        self, val: str, section: Union[str, Iterable[str]] = "core", default: Any = None
    ) -> Any:
        """Get a particular value from the config."""
        section_dict = self.get_section(section)
        if section_dict is None:
            return default

        return section_dict.get(val, default)

    def get_section(self, section: Union[str, Iterable[str]]) -> Any:
        """Return a whole section of config as a dict.

        If the element found at the address is a value and not
        a section, it is still returned and so this can be used
        as a more advanced from of the basic `get` method.

        Args:
            section: An iterable or string. If it's a string
                we load that root section. If it's an iterable
                of strings, then we treat it as a path within
                the dictionary structure.

        """
        if isinstance(section, str):
            return self._configs.get(section, None)
        else:
            # Try iterating
            buff = self._configs
            for sec in section:
                buff = buff.get(sec, None)
                if buff is None:
                    return None
            return buff

    def set_value(self, config_path: Iterable[str], val: Any) -> None:
        """Set a value at a given path."""
        # Make the path a list so we can index on it
        config_path = list(config_path)
        # Coerce the value into something more useful.
        config_val = coerce_value(val)
        # Sort out core if not there
        if len(config_path) == 1:  # pragma: no cover TODO?
            config_path = ["core"] + config_path
        # Current section:
        dict_buff = [self._configs]
        for elem in config_path[:-1]:
            dict_buff.append(dict_buff[-1].get(elem, {}))
        # Set the value
        dict_buff[-1][config_path[-1]] = config_val
        # Rebuild the config
        for elem in reversed(config_path[:-1]):
            dict_elem = dict_buff.pop()
            dict_buff[-1][elem] = dict_elem
        self._configs = dict_buff[0]

    def iter_vals(
        self, cfg: Optional[Dict[str, Any]] = None
    ) -> Iterable[Tuple[Any, ...]]:
        """Return an iterable of tuples representing keys.

        We show values before dicts, the tuple contains an indent
        value to know what level of the dict we're in. Dict labels
        will be returned as a blank value before their content.
        """
        cfg = cfg or self._configs

        # Get keys and sort
        keys = sorted(cfg.keys())
        # First iterate values (alphabetically):
        for k in keys:
            if (
                not isinstance(cfg[k], dict)
                and cfg[k] is not None
                and k not in self.private_vals
            ):
                yield (0, k, cfg[k])

        # Then iterate dicts (alphabetically (but `core` comes first if it exists))
        for k in keys:
            if isinstance(cfg[k], dict):
                # First yield the dict label
                yield (0, k, "")
                # Then yield its content
                for idnt, key, val in self.iter_vals(cfg=cfg[k]):
                    yield (idnt + 1, key, val)

    def process_inline_config(self, config_line: str, fname: str) -> None:
        """Process an inline config command and update self."""
        # Strip preceding comment marks
        if config_line.startswith("--"):
            config_line = config_line[2:].strip()
        # Strip preceding sqlfluff line.
        if not config_line.startswith("sqlfluff:"):  # pragma: no cover
            config_logger.warning(
                "Unable to process inline config statement: %r", config_line
            )
            return
        config_line = config_line[9:].strip()
        config_val = split_colon_separated_string(config_line)
        # Validate the value
        ConfigLoader._validate_configs([config_val], fname)
        # Set the value
        self.set_value(*config_val)
        # If the config is for dialect, initialise the dialect.
        # NOTE: Comparison with a 1-tuple is intentional here as
        # the first element of config_val is a tuple.
        if config_val[0] == ("dialect",):
            self._initialise_dialect(config_val[1])

    def process_raw_file_for_config(self, raw_str: str, fname: str) -> None:
        """Process a full raw file for inline config and update self."""
        # Scan the raw file for config commands.
        for raw_line in raw_str.splitlines():
            # With or without a space.
            if raw_line.startswith(("-- sqlfluff", "--sqlfluff")):
                # Found a in-file config command
                self.process_inline_config(raw_line, fname)


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

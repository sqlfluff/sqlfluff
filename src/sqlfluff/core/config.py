"""Module for loading config."""

import logging
import os
import os.path
import configparser

import pluggy
from itertools import chain
from typing import Dict, List, Tuple, Any, Optional, Union, Iterable
from pathlib import Path
from sqlfluff.core.plugin.host import get_plugin_manager
from sqlfluff.core.errors import SQLFluffUserError

import appdirs

import toml

# Instantiate the templater logger
config_logger = logging.getLogger("sqlfluff.config")

global_loader = None
""":obj:`ConfigLoader`: A variable to hold the single module loader when loaded.

We define a global loader, so that between calls to load config, we
can still cache appropriately
"""


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


def nested_combine(*dicts: dict) -> dict:
    """Combine an iterable of dictionaries.

    Each dictionary is combined into a result dictionary. For
    each key in the first dictionary, it will be overwritten
    by any same-named key in any later dictionaries in the
    iterable. If the element at that key is a dictionary, rather
    than just overwriting we use the same function to combine
    those dictionaries.

    Args:
        *dicts: An iterable of dictionaries to be combined.

    Returns:
        `dict`: A combined dictionary from the input dictionaries.

    """
    r: dict = {}
    for d in dicts:
        for k in d:
            if k in r and isinstance(r[k], dict):
                if isinstance(d[k], dict):
                    r[k] = nested_combine(r[k], d[k])
                else:  # pragma: no cover
                    raise ValueError(
                        "Key {!r} is a dict in one config but not another! PANIC: {!r}".format(
                            k, d[k]
                        )
                    )
            else:
                r[k] = d[k]
    return r


def dict_diff(left: dict, right: dict, ignore: Optional[List[str]] = None) -> dict:
    """Work out the difference between to dictionaries.

    Returns a dictionary which represents elements in the `left`
    dictionary which aren't in the `right` or are different to
    those in the `right`. If the element is a dictionary, we
    recursively look for differences in those dictionaries,
    likewise only returning the differing elements.

    NOTE: If an element is in the `right` but not in the `left`
    at all (i.e. an element has been *removed*) then it will
    not show up in the comparison.

    Args:
        left (:obj:`dict`): The object containing the *new* elements
            which will be compared against the other.
        right (:obj:`dict`): The object to compare against.

    Returns:
        `dict`: A dictionary representing the difference.

    """
    buff: dict = {}
    for k in left:
        if ignore and k in ignore:
            continue
        # Is the key there at all?
        if k not in right:
            buff[k] = left[k]
        # Is the content the same?
        elif left[k] == right[k]:
            continue
        # If it's not the same but both are dicts, then compare
        elif isinstance(left[k], dict) and isinstance(right[k], dict):
            diff = dict_diff(left[k], right[k], ignore=ignore)
            # Only if the difference is not ignored it do we include it.
            if diff:
                buff[k] = diff
        # It's just different
        else:
            buff[k] = left[k]
    return buff


class ConfigLoader:
    """The class for loading config files.

    Note:
        Unlike most cfg file readers, sqlfluff is case-sensitive in how
        it reads config files. This is to ensure we support the case
        sensitivity of jinja.

    """

    def __init__(self):
        # TODO: check that this cache implementation is actually useful
        self._config_cache: dict = {}

    @classmethod
    def get_global(cls) -> "ConfigLoader":
        """Get the singleton loader."""
        global global_loader
        if not global_loader:
            global_loader = cls()
        return global_loader

    @classmethod
    def _walk_toml(cls, config: Dict[str, Any], base_key=()):
        """Recursively walk the nested config inside a TOML file."""
        buff: List[tuple] = []
        for k, v in config.items():
            key = base_key + (k,)
            if isinstance(v, dict):
                buff.extend(cls._walk_toml(v, key))
            else:
                buff.append((key, v))

        return buff

    @classmethod
    def _get_config_elems_from_toml(cls, fpath: str) -> List[Tuple[tuple, Any]]:
        """Load a config from a TOML file and return a list of tuples.

        The return value is a list of tuples, were each tuple has two elements,
        the first is a tuple of paths, the second is the value at that path.
        """
        config = toml.load(fpath)
        tool = config.get("tool", {}).get("sqlfluff", {})

        return cls._walk_toml(tool)

    @staticmethod
    def _get_config_elems_from_file(fpath: str) -> List[Tuple[tuple, Any]]:
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
        buff: List[Tuple[tuple, Any]] = []
        # Disable interpolation so we can load macros
        kw: Dict = {}
        kw["interpolation"] = None
        config = configparser.ConfigParser(**kw)
        # NB: We want to be case sensitive in how we read from files,
        # because jinja is also case sensitive. To do this we override
        # the optionxform attribute.
        config.optionxform = lambda option: option  # type: ignore
        config.read(fpath)
        for k in config.sections():
            if k == "sqlfluff":
                key: Tuple = ("core",)
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
                if name.lower().endswith(("_path", "_dir")):
                    # Try to resolve the path.
                    # Make the referenced path.
                    ref_path = os.path.join(os.path.dirname(fpath), val)
                    # Check if it exists, and if it does, replace the value with the path.
                    if os.path.exists(ref_path):
                        v = ref_path
                # Add the name to the end of the key
                buff.append((key + (name,), v))
        return buff

    @staticmethod
    def _incorporate_vals(ctx: dict, vals: List[Tuple[Tuple[str, ...], Any]]) -> dict:
        """Take a list of tuples and incorporate it into a dictionary."""
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

    def load_default_config_file(self, file_dir: str, file_name: str) -> dict:
        """Load the default config file."""
        if file_name == "pyproject.toml":
            elems = self._get_config_elems_from_toml(os.path.join(file_dir, file_name))
        else:
            elems = self._get_config_elems_from_file(os.path.join(file_dir, file_name))
        return self._incorporate_vals({}, elems)

    def load_config_at_path(self, path: str) -> dict:
        """Load config from a given path."""
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

        configs: dict = {}

        if os.path.isdir(path):
            p = path
        else:
            p = os.path.dirname(path)

        d = os.listdir(os.path.expanduser(p))
        # iterate this way round to make sure things overwrite is the right direction
        for fname in filename_options:
            if fname in d:
                if fname == "pyproject.toml":
                    elems = self._get_config_elems_from_toml(os.path.join(p, fname))
                else:
                    elems = self._get_config_elems_from_file(os.path.join(p, fname))
                configs = self._incorporate_vals(configs, elems)

        # Store in the cache
        self._config_cache[str(path)] = configs
        return configs

    def load_extra_config(self, extra_config_path: str) -> dict:
        """Load specified extra config."""
        if not os.path.exists(extra_config_path):
            raise SQLFluffUserError(
                f"Extra config '{extra_config_path}' does not exist."
            )

        # First check the cache
        if str(extra_config_path) in self._config_cache:
            return self._config_cache[str(extra_config_path)]

        configs: dict = {}
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

    def load_user_appdir_config(self) -> dict:
        """Load the config from the user's OS specific appdir config directory."""
        user_config_dir_path = self._get_user_config_dir_path()
        if os.path.exists(user_config_dir_path):
            return self.load_config_at_path(user_config_dir_path)
        else:
            return {}

    def load_user_config(self) -> dict:
        """Load the config from the user's home directory."""
        user_home_path = os.path.expanduser("~")
        return self.load_config_at_path(user_home_path)

    def load_config_up_to_path(
        self,
        path: str,
        extra_config_path: Optional[str] = None,
        ignore_local_config: bool = False,
    ) -> dict:
        """Loads a selection of config files from both the path and its parent paths."""
        user_appdir_config = (
            self.load_user_appdir_config() if not ignore_local_config else {}
        )
        user_config = self.load_user_config() if not ignore_local_config else {}
        config_paths = (
            self.iter_config_locations_up_to_path(path)
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
        cls, path, working_path=os.getcwd(), ignore_file_name=".sqlfluffignore"
    ):
        """Finds sqlfluff ignore files from both the path and its parent paths."""
        return set(
            filter(
                os.path.isfile,
                map(
                    lambda x: os.path.join(x, ignore_file_name),
                    cls.iter_config_locations_up_to_path(
                        path=path, working_path=working_path
                    ),
                ),
            )
        )

    @staticmethod
    def iter_config_locations_up_to_path(path, working_path=Path.cwd()):
        """Finds config locations from both the path and its parent paths.

        The lowest priority is the user appdir, then home dir, then increasingly
        the configs closest to the file being directly linted.
        """
        given_path = Path(path).resolve()
        working_path = Path(working_path).resolve()

        # If we've been passed a file and not a directory,
        # then go straight to the directory.
        if not given_path.is_dir():
            given_path = given_path.parent

        common_path = Path(os.path.commonpath([working_path, given_path]))

        # we have a sub path! We can load nested paths
        path_to_visit = common_path
        while path_to_visit != given_path:
            yield str(path_to_visit.resolve())
            next_path_to_visit = (
                path_to_visit / given_path.relative_to(path_to_visit).parts[0]
            )
            if next_path_to_visit == path_to_visit:  # pragma: no cover
                # we're not making progress...
                # [prevent infinite loop]
                break
            path_to_visit = next_path_to_visit

        yield str(given_path.resolve())


class FluffConfig:
    """The class that actually gets passed around as a config object."""

    private_vals = "rule_denylist", "rule_allowlist", "dialect_obj", "templater_obj"

    def __init__(
        self,
        configs: Optional[dict] = None,
        extra_config_path: Optional[str] = None,
        ignore_local_config: bool = False,
        overrides: Optional[dict] = None,
        plugin_manager: Optional[pluggy.PluginManager] = None,
    ):
        self._extra_config_path = (
            extra_config_path  # We only store this for child configs
        )
        self._ignore_local_config = (
            ignore_local_config  # We only store this for child configs
        )
        self._overrides = overrides  # We only store this for child configs

        # Fetch a fresh plugin manager if we weren't provided with one
        self._plugin_manager = plugin_manager or get_plugin_manager()

        defaults = nested_combine(*self._plugin_manager.hook.load_default_config())
        self._configs = nested_combine(
            defaults, configs or {"core": {}}, {"core": overrides or {}}
        )
        # Some configs require special treatment
        self._configs["core"]["color"] = (
            False if self._configs["core"].get("nocolor", False) else None
        )
        # Deal with potential ignore parameters
        if self._configs["core"].get("ignore", None):
            self._configs["core"]["ignore"] = self._split_comma_separated_string(
                self._configs["core"]["ignore"]
            )
        else:
            self._configs["core"]["ignore"] = []
        # Allowlists and denylists
        if self._configs["core"].get("rules", None):
            self._configs["core"][
                "rule_allowlist"
            ] = self._split_comma_separated_string(self._configs["core"]["rules"])
        else:
            self._configs["core"]["rule_allowlist"] = None
        if self._configs["core"].get("exclude_rules", None):
            self._configs["core"]["rule_denylist"] = self._split_comma_separated_string(
                self._configs["core"]["exclude_rules"]
            )
        else:
            self._configs["core"]["rule_denylist"] = None
        # Configure Recursion
        if self._configs["core"].get("recurse", 0) == 0:
            self._configs["core"]["recurse"] = True

        # Dialect and Template selection.
        # NB: We import here to avoid a circular references.
        from sqlfluff.core.dialects import dialect_selector

        self._configs["core"]["dialect_obj"] = dialect_selector(
            self._configs["core"]["dialect"]
        )
        self._configs["core"]["templater_obj"] = self.get_templater(
            self._configs["core"]["templater"]
        )

    def __getstate__(self):
        # Copy the object's state from self.__dict__ which contains
        # all our instance attributes. Always use the dict.copy()
        # method to avoid modifying the original state.
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        del state["_plugin_manager"]
        return state

    def __setstate__(self, state):
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

    @classmethod
    def from_root(
        cls,
        extra_config_path: Optional[str] = None,
        ignore_local_config: bool = False,
        overrides: Optional[dict] = None,
    ) -> "FluffConfig":
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
        )

    @classmethod
    def from_path(
        cls,
        path: str,
        extra_config_path: Optional[str] = None,
        ignore_local_config: bool = False,
        overrides: Optional[dict] = None,
        plugin_manager: Optional[pluggy.PluginManager] = None,
    ) -> "FluffConfig":
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
        config: Optional["FluffConfig"] = None,
        dialect: Optional[str] = None,
        rules: Optional[List[str]] = None,
        exclude_rules: Optional[List[str]] = None,
    ) -> "FluffConfig":
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
        return cls(overrides=overrides)

    def get_templater(self, templater_name="jinja", **kwargs):
        """Fetch a templater by name."""
        templater_lookup = {
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
                    "Starting in sqlfluff version 0.7.0 the dbt templater is distributed as a "
                    "seperate python package. Please pip install sqlfluff-templater-dbt to use it."
                )
            raise SQLFluffUserError(
                "Requested templater {!r} which is not currently available. Try one of {}".format(
                    templater_name, ", ".join(templater_lookup.keys())
                )
            )

    def make_child_from_path(self, path: str) -> "FluffConfig":
        """Make a new child config at a path but pass on overrides and extra_config_path."""
        return self.from_path(
            path,
            extra_config_path=self._extra_config_path,
            ignore_local_config=self._ignore_local_config,
            overrides=self._overrides,
            plugin_manager=self._plugin_manager,
        )

    def diff_to(self, other: "FluffConfig") -> dict:
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
    ):
        """Get a particular value from the config."""
        section_dict = self.get_section(section)
        if section_dict is None:
            return default

        return section_dict.get(val, default)

    def get_section(self, section: Union[str, Iterable[str]]) -> Union[dict, None]:
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

    def set_value(self, config_path: Iterable[str], val: Any):
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
            dict_buff.append(dict_buff[-1][elem])
        # Set the value
        dict_buff[-1][config_path[-1]] = config_val
        # Rebuild the config
        for elem in reversed(config_path[:-1]):
            dict_elem = dict_buff.pop()
            dict_buff[-1][elem] = dict_elem
        self._configs = dict_buff[0]

    def iter_vals(self, cfg: Optional[dict] = None) -> Iterable[tuple]:
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

    def process_inline_config(self, config_line: str):
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
        # Divide on colons
        config_path = [elem.strip() for elem in config_line.split(":")]
        # Set the value
        self.set_value(config_path[:-1], config_path[-1])

    def process_raw_file_for_config(self, raw_str: str):
        """Process a full raw file for inline config and update self."""
        # Scan the raw file for config commands.
        for raw_line in raw_str.splitlines():
            if raw_line.startswith("-- sqlfluff"):
                # Found a in-file config command
                self.process_inline_config(raw_line)

    @staticmethod
    def _split_comma_separated_string(raw_str: str) -> List[str]:
        return [s.strip() for s in raw_str.split(",") if s.strip()]


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

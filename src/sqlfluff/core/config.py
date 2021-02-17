"""Module for loading config."""

import logging
import os
import os.path
import sys
import configparser
from typing import Dict, List, Tuple, Any, Optional, Union, Iterable
from pathlib import Path
from sqlfluff.core.plugin.host import get_plugin_manager

import appdirs

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
                else:
                    raise ValueError(
                        "Key {0!r} is a dict in one config but not another! PANIC: {1!r}".format(
                            k, d[k]
                        )
                    )
            else:
                r[k] = d[k]
    return r


def dict_diff(left: dict, right: dict) -> dict:
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
        # Is the key there at all?
        if k not in right:
            buff[k] = left[k]
        # Is the content the same?
        elif left[k] == right[k]:
            continue
        # If it's not the same but both are dicts, then compare
        elif isinstance(left[k], dict) and isinstance(right[k], dict):
            diff = dict_diff(left[k], right[k])
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

    @staticmethod
    def _get_config_elems_from_file(fpath: str) -> List[Tuple[tuple, Any]]:
        """Load a config from a file and return a list of tuples.

        The return value is a list of tuples, were each tuple has two elements,
        the first is a tuple of paths, the second is the value at that path.

        Note:
            Unlike most cfg file readers, sqlfluff is case-sensitive in how
            it reads config files.

        Note:
            Any variable names ending with `_path`, will be attempted to be
            resolved as relative paths to this config file. If that fails the
            string value will remain.

        """
        buff: List[Tuple[tuple, Any]] = []
        # Disable interpolation so we can load macros
        kw: Dict = {}
        if sys.version_info >= (3, 0):
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
            else:
                # if it doesn't start with sqlfluff, then don't go
                # further on this iteration
                continue

            for name, val in config.items(section=k):
                # Try to coerce it to a more specific type,
                # otherwise just make it a string.
                v = coerce_value(val)

                # Attempt to resolve paths
                if name.lower().endswith("_path"):
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
                    else:
                        raise ValueError(
                            "Overriding config value with section! [{0}]".format(k)
                        )
                else:
                    r[dp] = {}
                    r = r[dp]
            # Deal with the value itself
            r[n] = v
        return ctx

    def load_default_config_file(self, file_dir: str, file_name: str) -> dict:
        """Load the default config file."""
        elems = self._get_config_elems_from_file(os.path.join(file_dir, file_name))
        return self._incorporate_vals({}, elems)

    def load_config_at_path(self, path: str) -> dict:
        """Load config from a given path."""
        # First check the cache
        if str(path) in self._config_cache:
            return self._config_cache[str(path)]

        # The potential filenames we would look for at this path.
        # NB: later in this list overwrites earlier
        filename_options = ["setup.cfg", "tox.ini", "pep8.ini", ".sqlfluff"]

        configs: dict = {}

        if os.path.isdir(path):
            p = path
        else:
            p = os.path.dirname(path)

        d = os.listdir(p)
        # iterate this way round to make sure things overwrite is the right direction
        for fname in filename_options:
            if fname in d:
                elems = self._get_config_elems_from_file(os.path.join(p, fname))
                configs = self._incorporate_vals(configs, elems)

        # Store in the cache
        self._config_cache[str(path)] = configs
        return configs

    def load_user_appdir_config(self) -> dict:
        """Load the config from the user's OS specific appdir config directory."""
        appname = "sqlfluff"
        appauthor = "sqlfluff"
        user_config_dir_path = appdirs.user_config_dir(appname, appauthor)
        if os.path.exists(user_config_dir_path):
            return self.load_config_at_path(user_config_dir_path)
        return {}

    def load_user_config(self) -> dict:
        """Load the config from the user's home directory."""
        user_home_path = os.path.expanduser("~")
        return self.load_config_at_path(user_home_path)

    def load_config_up_to_path(self, path: str) -> dict:
        """Loads a selection of config files from both the path and its parent paths."""
        user_appdir_config = self.load_user_appdir_config()
        user_config = self.load_user_config()
        config_paths = self.iter_config_locations_up_to_path(path)
        config_stack = [self.load_config_at_path(p) for p in config_paths]
        return nested_combine(user_appdir_config, user_config, *config_stack)

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
            if next_path_to_visit == path_to_visit:
                # we're not making progress...
                # [prevent infinite loop]
                break
            path_to_visit = next_path_to_visit

        yield str(given_path.resolve())


class FluffConfig:
    """.The class that actually gets passed around as a config object."""

    private_vals = "rule_blacklist", "rule_whitelist", "dialect_obj", "templater_obj"

    def __init__(
        self, configs: Optional[dict] = None, overrides: Optional[dict] = None
    ):
        self._overrides = overrides  # We only store this for child configs
        defaults = nested_combine(*get_plugin_manager().hook.load_default_config())
        self._configs = nested_combine(
            defaults, configs or {"core": {}}, {"core": overrides or {}}
        )
        # Some configs require special treatment
        self._configs["core"]["color"] = (
            False if self._configs["core"].get("nocolor", False) else None
        )
        # Deal with potential ignore parameters
        if self._configs["core"].get("ignore", None):
            self._configs["core"]["ignore"] = self._configs["core"]["ignore"].split(",")
        else:
            self._configs["core"]["ignore"] = []
        # Whitelists and blacklists
        if self._configs["core"].get("rules", None):
            self._configs["core"]["rule_whitelist"] = self._configs["core"][
                "rules"
            ].split(",")
        else:
            self._configs["core"]["rule_whitelist"] = None
        if self._configs["core"].get("exclude_rules", None):
            self._configs["core"]["rule_blacklist"] = self._configs["core"][
                "exclude_rules"
            ].split(",")
        else:
            self._configs["core"]["rule_blacklist"] = None
        # Configure Recursion
        if self._configs["core"].get("recurse", 0) == 0:
            self._configs["core"]["recurse"] = True

        # Dialect and Template selection.
        # NB: We import here to avoid a circular references.
        from sqlfluff.core.dialects import dialect_selector
        from sqlfluff.core.templaters import templater_selector

        self._configs["core"]["dialect_obj"] = dialect_selector(
            self._configs["core"]["dialect"]
        )
        self._configs["core"]["templater_obj"] = templater_selector(
            self._configs["core"]["templater"]
        )

    @classmethod
    def from_root(cls, overrides: Optional[dict] = None) -> "FluffConfig":
        """Loads a config object just based on the root directory."""
        loader = ConfigLoader.get_global()
        c = loader.load_config_up_to_path(path=".")
        return cls(configs=c, overrides=overrides)

    @classmethod
    def from_path(cls, path: str, overrides: Optional[dict] = None) -> "FluffConfig":
        """Loads a config object given a particular path."""
        loader = ConfigLoader.get_global()
        c = loader.load_config_up_to_path(path=path)
        return cls(configs=c, overrides=overrides)

    @classmethod
    def from_kwargs(
        cls,
        config: Optional["FluffConfig"] = None,
        dialect: Optional[str] = None,
        rules: Optional[Union[str, List[str]]] = None,
    ) -> "FluffConfig":
        """Instantiate a config from either an existing config or kwargs.

        This is a convenience method for the ways that the public classes
        like Linter(), Parser() and Lexer() can be instantiated with a
        FluffConfig or with the convenience kwargs: dialect & rules.
        """
        if (dialect or rules) and config:
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
            # If it's a string, make it a list
            if isinstance(rules, str):
                rules = [rules]
            # Make a comma separated string to pass in as override
            overrides["rules"] = ",".join(rules)
        return cls(overrides=overrides)

    def make_child_from_path(self, path: str) -> "FluffConfig":
        """Make a new child config at a path but pass on overrides."""
        return self.from_path(path, overrides=self._overrides)

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
        return dict_diff(self._configs, other._configs)

    def get(
        self, val: str, section: Union[str, Iterable[str]] = "core", default: Any = None
    ):
        """Get a particular value from the config."""
        return self._configs[section].get(val, default)

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
        if len(config_path) == 1:
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
        if not config_line.startswith("sqlfluff:"):
            config_logger.warning(
                "Unable to process inline config statement: %r", config_line
            )
            return
        config_line = config_line[9:].strip()
        # Divide on colons
        config_path = [elem.strip() for elem in config_line.split(":")]
        # Set the value
        self.set_value(config_path[:-1], config_path[-1])

"""Module for loading config."""

from __future__ import annotations

import logging
from itertools import chain
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
    Union,
)

import pluggy

from sqlfluff.core.config.loader import ConfigLoader, coerce_value
from sqlfluff.core.errors import SQLFluffUserError
from sqlfluff.core.helpers.dict import dict_diff, nested_combine
from sqlfluff.core.helpers.string import (
    split_colon_separated_string,
    split_comma_separated_string,
)
from sqlfluff.core.plugin.host import get_plugin_manager

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.templaters.base import RawTemplater

# Instantiate the config logger
config_logger = logging.getLogger("sqlfluff.config")


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
        self._handle_comma_separated_values()
        # Dialect and Template selection.
        dialect: Optional[str] = self._configs["core"]["dialect"]
        self._initialise_dialect(dialect, require_dialect)

        self._configs["core"]["templater_obj"] = self.get_templater(
            self._configs["core"]["templater"]
        )

    def _handle_comma_separated_values(self):
        for in_key, out_key in [
            ("ignore", "ignore"),
            ("warnings", "warnings"),
            ("rules", "rule_allowlist"),
            ("exclude_rules", "rule_denylist"),
        ]:
            if self._configs["core"].get(in_key, None):
                self._configs["core"][out_key] = split_comma_separated_string(
                    self._configs["core"][in_key]
                )
            else:
                self._configs["core"][out_key] = []

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
        config_key, config_value = split_colon_separated_string(config_line)
        # Validate the value
        ConfigLoader._validate_configs([config_key, config_value], fname)
        # Set the value
        self.set_value(config_key, config_value)
        # If the config is for dialect, initialise the dialect.
        # NOTE: Comparison with a 1-tuple is intentional here as
        # the first element of config_val is a tuple.
        if config_key == ("core", "dialect"):
            self._initialise_dialect(config_value)

    def process_raw_file_for_config(self, raw_str: str, fname: str) -> None:
        """Process a full raw file for inline config and update self."""
        # Scan the raw file for config commands.
        for raw_line in raw_str.splitlines():
            # With or without a space.
            if raw_line.startswith(("-- sqlfluff", "--sqlfluff")):
                # Found a in-file config command
                self.process_inline_config(raw_line, fname)
        # Deal with potential list-like inputs.
        self._handle_comma_separated_values()

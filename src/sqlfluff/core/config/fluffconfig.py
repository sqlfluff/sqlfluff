"""Module for loading config."""

from __future__ import annotations

import logging
from collections.abc import Iterable
from copy import copy, deepcopy
from itertools import chain
from typing import TYPE_CHECKING, Any, Optional, Union

import pluggy

from sqlfluff.core.config.ini import coerce_value
from sqlfluff.core.config.loader import load_config_string, load_config_up_to_path
from sqlfluff.core.config.validate import validate_config_dict
from sqlfluff.core.errors import SQLFluffUserError
from sqlfluff.core.helpers.dict import (
    dict_diff,
    iter_records_from_nested_dict,
    nested_combine,
    records_to_nested_dict,
)
from sqlfluff.core.helpers.string import (
    split_colon_separated_string,
    split_comma_separated_string,
)
from sqlfluff.core.plugin.host import get_plugin_manager
from sqlfluff.core.types import ConfigMappingType, ConfigValueOrListType

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.templaters.base import RawTemplater

# Instantiate the config logger
config_logger = logging.getLogger("sqlfluff.config")


class FluffConfig:
    """The persistent object for internal methods to access configuration.

    This class is designed to be instantiated once for each file and then be
    reused by each part of the process. For multiple files in the same path, a
    parent object will be created for the each path and then variants of it
    are created *for each file*. The object itself contains the references
    to any long lived objects which might be used by multiple parts of the
    codebase such as the dialect and the templater (both of which can be
    resource intensive to load & instantiate), which allows (for example),
    multiple files to reuse the same instance of the relevant dialect.

    It is also designed to pickle well for use in parallel operations.

    Args:
        configs (ConfigMappingType, optional): A nested dict of config
            values from which to construct the config.
        extra_config_path (str, optional): An optional additional path
            to load config files from. These are loaded last if found
            and take precedence over any pre-existing config values.
            Note that when provided directly to the class, this path
            is not loaded for the class in question (it's assumed that
            has already been done, and the results are incorporated in
            the `configs` argument), but it *is* passed onward to child
            config instances, which will use it.
        ignore_local_config (bool, optional, defaults to False): If set to
            True, this skips loading configuration from the user home
            directory (``~``) or ``appdir`` path.
        overrides (ConfigMappingType, optional): A additional set of
            configs to merge into the ``core`` section of the config
            object at the end. These values take precedence over all
            other provided values and are inherited by child configs.
            For example, override values provided in the CLI use this
            method to apply to all files in a linting operation. Note
            that this mapping dict *only* applies to the ``core``
            section and so cannot be used for all values.
        plugin_manager (PluginManager, optional): Optional pre-loaded
            config manager. Generally users should not need to provide
            this, as the class will fetch it's own if not provided.
            This argument is used when creating new class instances to
            avoid reloading the manager.

    .. note::
       Methods for accessing internal properties on the config are not particularly
       standardised as the project currently assumes that few other tools are using
       this interface directly. If you or your project would like more formally
       supported methods for access to the config object, raise an issue on GitHub
       with the kind of things you'd like to achieve.
    """

    private_vals = "rule_denylist", "rule_allowlist", "dialect_obj", "templater_obj"

    def __init__(
        self,
        configs: Optional[ConfigMappingType] = None,
        extra_config_path: Optional[str] = None,
        ignore_local_config: bool = False,
        overrides: Optional[ConfigMappingType] = None,
        plugin_manager: Optional[pluggy.PluginManager] = None,
        # Ideally a dialect should be set when config is read but sometimes
        # it might only be set in nested .sqlfluff config files, so allow it
        # to be not required.
        require_dialect: bool = True,
    ) -> None:
        self._extra_config_path = (
            extra_config_path  # We only store this for child configs
        )
        self._ignore_local_config = (
            ignore_local_config  # We only store this for child configs
        )
        # If overrides are provided, validate them early.
        if overrides:
            overrides = {"core": overrides}
            validate_config_dict(overrides, "<provided overrides>")
        # Stash overrides so we can pass them to child configs
        core_overrides = overrides["core"] if overrides else None
        assert isinstance(core_overrides, dict) or core_overrides is None
        self._overrides = core_overrides

        # Fetch a fresh plugin manager if we weren't provided with one
        self._plugin_manager = plugin_manager or get_plugin_manager()

        defaults = nested_combine(*self._plugin_manager.hook.load_default_config())
        # If any existing configs are provided. Validate them:
        if configs:
            validate_config_dict(configs, "<provided configs>")
        self._configs = nested_combine(
            defaults, configs or {"core": {}}, overrides or {}
        )
        # Some configs require special treatment
        self._configs["core"]["color"] = (
            False if self._configs["core"].get("nocolor", False) else None
        )
        # Handle inputs which are potentially comma separated strings
        self._handle_comma_separated_values()
        # Dialect and Template selection.
        _dialect = self._configs["core"]["dialect"]
        assert _dialect is None or isinstance(_dialect, str)
        self._initialise_dialect(_dialect, require_dialect)

        self._configs["core"]["templater_obj"] = self.get_templater()

    def _handle_comma_separated_values(self) -> None:
        for in_key, out_key in [
            ("ignore", "ignore"),
            ("warnings", "warnings"),
            ("rules", "rule_allowlist"),
            ("exclude_rules", "rule_denylist"),
        ]:
            in_value = self._configs["core"].get(in_key, None)
            if in_value:
                assert not isinstance(in_value, dict)
                self._configs["core"][out_key] = split_comma_separated_string(in_value)
            else:
                self._configs["core"][out_key] = []

    def _initialise_dialect(
        self, dialect: Optional[str], require_dialect: bool = True
    ) -> None:
        # NB: We import here to avoid a circular references.
        from sqlfluff.core.dialects import dialect_selector

        if dialect is not None:
            self._configs["core"]["dialect_obj"] = dialect_selector(dialect)
        elif require_dialect:
            self.verify_dialect_specified()

    def verify_dialect_specified(self) -> None:
        """Check if the config specifies a dialect, raising an error if not.

        Raises:
            SQLFluffUserError: If dialect config value is unset. The content
                of the error contains user-facing instructions on what dialects
                are available and how to set the dialect.
        """
        if self._configs["core"].get("dialect", None) is None:
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

    def __getstate__(self) -> dict[str, Any]:
        # Copy the object's state from self.__dict__ which contains
        # all our instance attributes. Always use the dict.copy()
        # method to avoid modifying the original state.
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        del state["_plugin_manager"]
        # The dbt templater doesn't pickle well, but isn't required
        # within threaded operations. If it was, it could easily be
        # rehydrated within the thread. For rules which want to determine
        # the type of a templater in their context, use
        # `get_templater_class()` instead, which avoids instantiating
        # a new templater instance.
        # NOTE: It's important that we do this on a copy so that we
        # don't disturb the original object if it's still in use.
        state["_configs"] = state["_configs"].copy()
        state["_configs"]["core"] = state["_configs"]["core"].copy()
        state["_configs"]["core"]["templater_obj"] = None
        return state

    def __setstate__(self, state: dict[str, Any]) -> None:  # pragma: no cover
        # Restore instance attributes
        self.__dict__.update(state)
        # NOTE: Rather than rehydrating the previous plugin manager, we
        # fetch a fresh one.
        self._plugin_manager = get_plugin_manager()
        # NOTE: Likewise we don't reinstate the "templater_obj" config value
        # which should also only be used in the main thread rather than child
        # processes.

    def copy(self) -> FluffConfig:
        """Create a copy of this ``FluffConfig``.

        Copies created using this method can safely be modified without those
        changes propagating back up to the object which was originally copied.

        Returns:
            :obj:`FluffConfig`: A shallow copy of this config object but with
            a deep copy of the internal ``_configs`` dict.
        """
        configs_attribute_copy = deepcopy(self._configs)
        config_copy = copy(self)
        config_copy._configs = configs_attribute_copy
        # During the initial `.copy()`, we use the same `__reduce__()` method
        # which is used during pickling. The `templater_obj` doesn't pickle
        # well so is normally removed, but it's ok for us to just pass across
        # the original object here as we're in the same process.
        configs_attribute_copy["core"]["templater_obj"] = self._configs["core"][
            "templater_obj"
        ]
        return config_copy

    @classmethod
    def from_root(
        cls,
        extra_config_path: Optional[str] = None,
        ignore_local_config: bool = False,
        overrides: Optional[ConfigMappingType] = None,
        require_dialect: bool = True,
    ) -> FluffConfig:
        """Loads a config object based on the root directory.

        Args:
            extra_config_path (str, optional): An optional additional path
                to load config files from. These are loaded last if found
                and take precedence over any pre-existing config values.
            ignore_local_config (bool, optional, defaults to False): If set to
                True, this skips loading configuration from the user home
                directory (``~``) or ``appdir`` path.
            overrides (ConfigMappingType, optional): A additional set of
                configs to merge into the config object at the end. These
                values take precedence over all other provided values and
                are inherited by child configs. For example, override values
                provided in the CLI use this method to apply to all files
                in a linting operation.
            require_dialect (bool, optional, default is True): When True
                an error will be raise if the dialect config value is unset.

        Returns:
            :obj:`FluffConfig`: The loaded config object.
        """
        configs = load_config_up_to_path(
            path=".",
            extra_config_path=extra_config_path,
            ignore_local_config=ignore_local_config,
        )
        return cls(
            configs=configs,
            extra_config_path=extra_config_path,
            ignore_local_config=ignore_local_config,
            overrides=overrides,
            require_dialect=require_dialect,
        )

    @classmethod
    def from_string(
        cls,
        config_string: str,
        overrides: Optional[ConfigMappingType] = None,
    ) -> FluffConfig:
        """Loads a config object from a single config string.

        Args:
            config_string (str): The config string, assumed to be in ``ini``
                format (like a ``.sqlfluff`` file).
            overrides (ConfigMappingType, optional): A additional set of
                configs to merge into the config object at the end. These
                values take precedence over all other provided values and
                are inherited by child configs. For example, override values
                provided in the CLI use this method to apply to all files
                in a linting operation.

        Returns:
            :obj:`FluffConfig`: The loaded config object.
        """
        return cls(
            configs=load_config_string(config_string),
            overrides=overrides,
        )

    @classmethod
    def from_strings(
        cls,
        *config_strings: str,
        overrides: Optional[ConfigMappingType] = None,
    ) -> FluffConfig:
        """Loads a config object given a series of nested config strings.

        Args:
            *config_strings (str): An iterable of config strings, assumed
                to be in ``ini`` format (like a ``.sqlfluff`` file).
            overrides (ConfigMappingType, optional): A additional set of
                configs to merge into the config object at the end. These
                values take precedence over all other provided values and
                are inherited by child configs. For example, override values
                provided in the CLI use this method to apply to all files
                in a linting operation.

        Returns:
            :obj:`FluffConfig`: The loaded config object.

        Config strings are incorporated from first to last, treating the
        first element as the "root" config, and then later config strings
        will take precedence over any earlier values.
        """
        config_state: ConfigMappingType = {}
        for config_string in config_strings:
            config_state = load_config_string(config_string, configs=config_state)
        return cls(
            configs=config_state,
            overrides=overrides,
        )

    @classmethod
    def from_path(
        cls,
        path: str,
        extra_config_path: Optional[str] = None,
        ignore_local_config: bool = False,
        overrides: Optional[ConfigMappingType] = None,
        plugin_manager: Optional[pluggy.PluginManager] = None,
        require_dialect: bool = True,
    ) -> FluffConfig:
        """Loads a config object given a particular path.

        Args:
            path (str): The target path to load config files from. Files
                found between the working path and this path are also loaded
                and nested with files closest to this target path taking
                precedence.
            extra_config_path (str, optional): An optional additional path
                to load config files from. These are loaded last if found
                and take precedence over any pre-existing config values.
            ignore_local_config (bool, optional, defaults to False): If set to
                True, this skips loading configuration from the user home
                directory (``~``) or ``appdir`` path.
            overrides (ConfigMappingType, optional): A additional set of
                configs to merge into the ``core`` section of the config
                object at the end. These values take precedence over all
                other provided values and are inherited by child configs.
                Note that this mapping dict *only* applies to the ``core``
                section and so cannot be used for all values.
            plugin_manager (PluginManager, optional): Optional pre-loaded
                config manager. Generally users should not need to provide
                this, as the class will fetch it's own if not provided.
                This argument is used when creating new class instances to
                avoid reloading the manager.
            require_dialect (bool, optional, default is True): When True
                an error will be raise if the dialect config value is unset.

        Returns:
            :obj:`FluffConfig`: The loaded config object.
        """
        configs = load_config_up_to_path(
            path=path,
            extra_config_path=extra_config_path,
            ignore_local_config=ignore_local_config,
        )
        return cls(
            configs=configs,
            extra_config_path=extra_config_path,
            ignore_local_config=ignore_local_config,
            overrides=overrides,
            plugin_manager=plugin_manager,
            require_dialect=require_dialect,
        )

    @classmethod
    def from_kwargs(
        cls,
        dialect: Optional[str] = None,
        rules: Optional[list[str]] = None,
        exclude_rules: Optional[list[str]] = None,
        require_dialect: bool = True,
    ) -> FluffConfig:
        """Instantiate a config from a subset of common options.

        Args:
            dialect (str, optional): The name of the dialect to use.
            rules (list of str, optional): A list of rules to include.
                Rule specifiers can be codes, names, groups or aliases.
                If not set, defaults to all rules.
            exclude_rules (list of str, optional): A list of rules to
                exclude. Rule specifiers can be codes, names, groups or
                aliases. If not set, does not exclude any rules.
            require_dialect (bool, optional, default is True): When True
                an error will be raise if the dialect config value is unset.

        Returns:
            :obj:`FluffConfig`: The loaded config object.

        This is a convenience method for the ways that the public classes
        like Linter(), Parser() and Lexer() allow a subset of attributes to
        be set directly rather than requiring a pre-made `FluffConfig`.
        """
        overrides: ConfigMappingType = {}
        if dialect:
            overrides["dialect"] = dialect
        if rules:
            # Make a comma separated string to pass in as override
            overrides["rules"] = ",".join(rules)
        if exclude_rules:
            # Make a comma separated string to pass in as override
            overrides["exclude_rules"] = ",".join(exclude_rules)

        return cls(overrides=overrides, require_dialect=require_dialect)

    def get_templater_class(self) -> type[RawTemplater]:
        """Get the configured templater class.

        .. note::
           This is mostly useful to call directly when rules want to determine
           the *type* of a templater without (in particular to work out if it's a
           derivative of the jinja templater), without needing to instantiate a
           full templater. Instantiated templaters don't pickle well, so aren't
           automatically passed around between threads/processes.
        """
        templater_lookup: dict[str, type[RawTemplater]] = {
            templater.name: templater
            for templater in chain.from_iterable(
                self._plugin_manager.hook.get_templaters()
            )
        }
        # Fetch the config value.
        templater_name = self._configs["core"].get("templater", "<no value set>")
        assert isinstance(
            templater_name, str
        ), f"Config value `templater` expected to be a string. Not: {templater_name!r}"
        try:
            cls = templater_lookup[templater_name]
            # Return class. Do not instantiate yet. That happens in `get_templater()`
            # for situations which require it.
            return cls
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

    def get_templater(self, **kwargs: Any) -> RawTemplater:
        """Instantiate the configured templater."""
        return self.get_templater_class()(**kwargs)

    def make_child_from_path(
        self, path: str, require_dialect: bool = True
    ) -> FluffConfig:
        """Make a child config at a path but pass on overrides and extra_config_path.

        Args:
            path (str): The path to load the new config object from, inheriting
                the content of the calling `FluffConfig` as base values.
            require_dialect (bool, optional, default is True): When True
                an error will be raise if the dialect config value is unset.

        Returns:
            :obj:`FluffConfig`: A new config object which copies the current
            config object, but overriding any values set by config values loaded
            from the given path.
        """
        return self.from_path(
            path,
            extra_config_path=self._extra_config_path,
            ignore_local_config=self._ignore_local_config,
            overrides=self._overrides,
            plugin_manager=self._plugin_manager,
            require_dialect=require_dialect,
        )

    def diff_to(self, other: FluffConfig) -> ConfigMappingType:
        """Compare this config to another.

        This is primarily used in the CLI logs to indicate to the user
        what values have been changed for each file compared to the root
        config for the project.

        Args:
            other (:obj:`FluffConfig`): Another config object to compare
                against. We will return keys from *this* object that are
                not in `other` or are different to those in `other`.

        Returns:
            :obj:`dict`: A filtered dict of items in this config that are
            not in the other or are different to the other.
        """
        # We ignore some objects which are not meaningful in the comparison
        # e.g. dialect_obj, which is generated on the fly.
        return dict_diff(self._configs, other._configs, ignore=["dialect_obj"])

    def get(
        self, val: str, section: Union[str, Iterable[str]] = "core", default: Any = None
    ) -> Any:
        """Get a particular value from the config.

        Args:
            val (str): The name of the config value to get.
            section (str or iterable of str, optional): The "path" to the config
                value. For values in the main ``[sqlfluff]`` section of the
                config, which are stored in the ``core`` section of the config
                this can be omitted.
            default: The value to return if the config value was not found. If
                no default is provided, then a ``KeyError`` will be raised if
                no value was found.

        The following examples show how to fetch various default values:

        >>> FluffConfig(overrides={"dialect": "ansi"}).get("dialect")
        'ansi'

        >>> config = FluffConfig(overrides={"dialect": "ansi"})
        >>> config.get("tab_space_size", section="indentation")
        4

        >>> FluffConfig(overrides={"dialect": "ansi"}).get(
        ...     "capitalisation_policy",
        ...     section=["rules", "capitalisation.keywords"]
        ... )
        'consistent'
        """
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
                temp = buff.get(sec, None)
                if temp is None:
                    return None
                buff = temp
            return buff

    def set_value(self, config_path: Iterable[str], val: Any) -> None:
        """Set a value at a given path.

        Args:
            config_path: An iterable of strings. Each should be
                a one of the elements which is colon delimited in
                a standard config file.
            val: The value to set at the given path.

        >>> cfg = FluffConfig(overrides={"dialect": "ansi"})
        >>> cfg.set_value(["dialect"], "postgres")
        >>> cfg.get("dialect")
        'postgres'

        >>> cfg = FluffConfig(overrides={"dialect": "ansi"})
        >>> cfg.set_value(["indentation", "tab_space_size"], 2)
        >>> cfg.get("tab_space_size", section="indentation")
        2
        """
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
        self, cfg: Optional[ConfigMappingType] = None
    ) -> Iterable[tuple[int, str, ConfigValueOrListType]]:
        """Return an iterable of tuples representing keys.

        Args:
            cfg (optional): An optional config mapping to format instead.
                If not provided, we use the internal config object of the
                `FluffConfig`.

        This is primarily to enable formatting of config objects in the CLI.

        We show values before dicts, the tuple contains an indent value to
        know what level of the dict we're in. Dict labels will be returned
        as a blank value before their content.
        """
        cfg = cfg or self._configs

        # Get keys and sort
        keys = sorted(cfg.keys())
        # First iterate values (alphabetically):
        for k in keys:
            value = cfg[k]
            if (
                not isinstance(value, dict)
                and value is not None
                and k not in self.private_vals
            ):
                yield (0, k, value)

        # Then iterate dicts (alphabetically (but `core` comes first if it exists))
        for k in keys:
            value = cfg[k]
            if isinstance(value, dict):
                # First yield the dict label
                yield (0, k, "")
                # Then yield its content
                for idnt, key, val in self.iter_vals(cfg=value):
                    yield (idnt + 1, key, val)

    def process_inline_config(self, config_line: str, fname: str) -> None:
        """Process an inline config command and update self.

        Args:
            config_line (str): The inline config section to be processed.
                This should usually begin with ``-- sqlfluff:``.
            fname (str): The name of the current file being processed. This
                is used purely for logging purposes in the case that an
                invalid config string is provided so that any error messages
                can reference the file with the issue.

        >>> cfg = FluffConfig(overrides={"dialect": "ansi"})
        >>> cfg.process_inline_config(
        ...     "-- sqlfluff:dialect:postgres",
        ...     "test.sql"
        ... )
        >>> cfg.get("dialect")
        'postgres'
        """
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
        # Move to core section if appropriate
        if len(config_key) == 1:
            config_key = ("core",) + config_key
        # Coerce data types
        config_record = (config_key, coerce_value(config_value))
        # Convert to dict & validate
        config_dict: ConfigMappingType = records_to_nested_dict([config_record])
        validate_config_dict(config_dict, f"inline config in {fname}")
        config_val = list(iter_records_from_nested_dict(config_dict))[0]

        # Set the value
        self.set_value(config_key, config_value)
        # If the config is for dialect, initialise the dialect.
        if config_val[0] == ("core", "dialect"):
            dialect_value = config_val[1]
            assert isinstance(dialect_value, str)
            self._initialise_dialect(dialect_value)

    def process_raw_file_for_config(self, raw_str: str, fname: str) -> None:
        """Process a full raw file for inline config and update self.

        Args:
            raw_str (str): The full SQL script to evaluate for inline configs.
            fname (str): The name of the current file being processed. This
                is used purely for logging purposes in the case that an
                invalid config string is provided so that any error messages
                can reference the file with the issue.

        >>> cfg = FluffConfig(overrides={"dialect": "ansi"})
        >>> cfg.process_raw_file_for_config(
        ...     "-- sqlfluff:dialect:postgres",
        ...     "test.sql"
        ... )
        >>> cfg.get("dialect")
        'postgres'
        """
        # Scan the raw file for config commands.
        for raw_line in raw_str.splitlines():
            # With or without a space.
            if raw_line.startswith(("-- sqlfluff", "--sqlfluff")):
                # Found a in-file config command
                self.process_inline_config(raw_line, fname)
        # Deal with potential list-like inputs.
        self._handle_comma_separated_values()

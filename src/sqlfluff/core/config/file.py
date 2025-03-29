"""Lower level routines for config file loading and caching.

Functions in this module load config from *individual* files and
resources. While some are cached, they are cached on the basis of
not processing individual files more than once.

For the cached functions it is VERY recommended to make sure they
are copied before any edits happen to them, as those edits may
propagate back up into the cache. Typically the results are passed
to `nested_combine` either immediately, or eventually after returning
which should negate this effect.
"""

import os.path
from functools import cache
from typing import Optional

from sqlfluff.core.config.ini import load_ini_string
from sqlfluff.core.config.toml import load_toml_file_config
from sqlfluff.core.config.validate import validate_config_dict
from sqlfluff.core.helpers.string import (
    split_comma_separated_string,
)
from sqlfluff.core.types import ConfigMappingType

COMMA_SEPARATED_PATH_KEYS = (
    "load_macros_from_path",
    "loader_search_path",
    "exclude_macros_from_path",
)
RESOLVE_PATH_SUFFIXES = ("_path", "_dir")


def _load_raw_file_as_dict(filepath: str) -> ConfigMappingType:
    """Loads the raw dict object from file without interpolation."""
    filename = os.path.basename(filepath)
    if filename == "pyproject.toml":
        return load_toml_file_config(filepath)
    # If it's not a pyproject file, assume that it's an ini file.
    with open(filepath, mode="r") as file:
        return load_ini_string(file.read())


def _resolve_path(filepath: str, val: str) -> str:
    """Try to resolve a path found in a config value."""
    # Make the referenced path.
    ref_path = os.path.join(os.path.dirname(filepath), val)
    # Check if it exists, and if it does, replace the value with the path.
    return ref_path if os.path.exists(ref_path) else val


def _resolve_paths_in_config(
    config: ConfigMappingType, filepath: str, logging_reference: Optional[str] = None
) -> None:
    """Attempt to resolve any paths found in the config file.

    NOTE: This method is recursive to crawl the whole config object,
    and also mutates the underlying config object rather than returning it.
    """
    log_filename: str = logging_reference or filepath
    for key, val in config.items():
        # If it's a dict, recurse.
        if isinstance(val, dict):
            _resolve_paths_in_config(val, filepath, logging_reference=logging_reference)
        # If it's a potential multi-path, split, resolve and join
        if key.lower() in COMMA_SEPARATED_PATH_KEYS:
            assert isinstance(
                val, str
            ), f"Value for {key} in {log_filename} must be a string not {type(val)}."
            paths = split_comma_separated_string(val)
            config[key] = ",".join(_resolve_path(filepath, path) for path in paths)
        # It it's a single path key, resolve it.
        elif key.lower().endswith(RESOLVE_PATH_SUFFIXES):
            assert isinstance(
                val, str
            ), f"Value for {key} in {log_filename} must be a string not {type(val)}."
            config[key] = _resolve_path(filepath, val)


@cache
def load_config_file_as_dict(filepath: str) -> ConfigMappingType:
    """Load the given config file into a dict and validate.

    This method is cached to mitigate being called multiple times.

    This doesn't manage the combination of config files within a nested
    structure, that happens further up the stack.
    """
    raw_config = _load_raw_file_as_dict(filepath)

    # The raw loaded files have some path interpolation which is necessary.
    _resolve_paths_in_config(raw_config, filepath)
    # Validate
    validate_config_dict(raw_config, filepath)

    # Return dict object (which will be cached)
    return raw_config


@cache
def load_config_string_as_dict(
    config_string: str, working_path: str, logging_reference: str
) -> ConfigMappingType:
    """Load the given config string and validate.

    This method is cached to mitigate being called multiple times.

    This doesn't manage the combination of config files within a nested
    structure, that happens further up the stack. The working path is
    necessary to resolve any paths in the config file.
    """
    raw_config = load_ini_string(config_string)

    # The raw loaded files have some path interpolation which is necessary.
    _resolve_paths_in_config(
        raw_config, working_path, logging_reference=logging_reference
    )
    # Validate
    validate_config_dict(raw_config, logging_reference)

    # Return dict object (which will be cached)
    return raw_config

"""Low level routines for config file loading and caching."""

import configparser
from typing import Any, List, Tuple

from sqlfluff.core.config.types import ConfigMappingType, ConfigValueType
from sqlfluff.core.helpers.dict import records_to_nested_dict

_ConfigElemType = Tuple[Tuple[str, ...], ConfigValueType]


def _coerce_value(val: str) -> ConfigValueType:
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


def load_ini_string(cfg_content: str) -> ConfigMappingType:
    """Read an ini-style config string.

    This would include loading a `.sqlfluff` file.

    Notes:
    - We rename the root `sqlfluff` section, to `core` so that it's in
      line with other config files.
    - The `configparser` reads everything as strings, but this method will
      attempt to find better types for values based on their content.
    - Path resolution isn't done here, that all happens later.
    """
    # If the string is empty, no need to parse it.
    if not cfg_content:
        return {}

    # Disable interpolation so we can load macros
    config = configparser.ConfigParser(delimiters="=", interpolation=None)
    # NB: We want to be case sensitive in how we read from files,
    # because jinja is also case sensitive. To do this we override
    # the optionxform attribute.
    config.optionxform = lambda option: option  # type: ignore

    # Read the content.
    config.read_string(cfg_content)

    # Build up a buffer of config values.
    config_buffer: List[_ConfigElemType] = []
    for k in config.sections():
        if k == "sqlfluff":
            key: Tuple[str, ...] = ("core",)
        elif k.startswith("sqlfluff:"):
            # Return a tuple of nested values
            key = tuple(k[len("sqlfluff:") :].split(":"))
        else:  # pragma: no cover
            # if it doesn't start with sqlfluff, then ignore this
            # section. It's not relevant to sqlfluff.
            continue

        for name, val in config.items(section=k):
            # Try to coerce it to a more specific type,
            # otherwise just make it a string.
            v = _coerce_value(val)

            # Add the name to the end of the key
            config_buffer.append((key + (name,), v))

    # Compress that buffer into a dictionary.
    return records_to_nested_dict(config_buffer)

"""Methods for loading config from pyproject.toml files."""

import sys
from typing import Tuple

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import toml as tomllib

from sqlfluff.core.config.types import ConfigMappingType, ConfigValueType

ConfigElemType = Tuple[Tuple[str, ...], ConfigValueType]


def load_toml_file_config(filepath: str) -> ConfigMappingType:
    """Read the SQLFluff config section of a pyproject.toml file.

    We don't need to change any key names here, because the root
    section of the toml file format is `tool.sqlfluff.core`.
    """
    with open(filepath, mode="r") as file:
        config = tomllib.loads(file.read())
    return config.get("tool", {}).get("sqlfluff", {})

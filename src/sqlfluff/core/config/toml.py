"""Methods for loading config from pyproject.toml files."""

import sys

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import toml as tomllib

from sqlfluff.core.config.types import ConfigMappingType
from sqlfluff.core.helpers.dict import (
    NestedDictRecord,
    iter_records_from_nested_dict,
    records_to_nested_dict,
)


def _condense_rule_record(record: NestedDictRecord) -> NestedDictRecord:
    """Helper function to condense the rule section of a toml config."""
    key, value = record
    if len(key) > 2:
        key = (".".join(key[:-1]), key[-1])
    return key, value


def load_toml_file_config(filepath: str) -> ConfigMappingType:
    """Read the SQLFluff config section of a pyproject.toml file.

    We don't need to change any key names here, because the root
    section of the toml file format is `tool.sqlfluff.core`.
    """
    with open(filepath, mode="r") as file:
        config = tomllib.loads(file.read())
    raw_config = config.get("tool", {}).get("sqlfluff", {})

    # NOTE: For the "rules" section of the sqlfluff config,
    # rule names are often qualified with a dot ".". In the
    # toml scenario this can get interpreted as a nested
    # section, and we resolve that edge case here.
    if "rules" not in raw_config:
        # No rules section, so no need to resolve.
        return raw_config

    rules_section = raw_config["rules"]
    # Condense the rules section.
    raw_config["rules"] = records_to_nested_dict(
        _condense_rule_record(record)
        for record in iter_records_from_nested_dict(rules_section)
    )

    return raw_config

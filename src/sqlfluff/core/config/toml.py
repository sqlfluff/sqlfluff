"""Methods for loading config from pyproject.toml files."""

import sys
from typing import Any, TypeVar

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import toml as tomllib

from sqlfluff.core.helpers.dict import (
    NestedDictRecord,
    iter_records_from_nested_dict,
    records_to_nested_dict,
)
from sqlfluff.core.types import ConfigMappingType

T = TypeVar("T")


def _condense_rule_record(record: NestedDictRecord[T]) -> NestedDictRecord[T]:
    """Helper function to condense the rule section of a toml config."""
    key, value = record
    if len(key) > 2:
        key = (".".join(key[:-1]), key[-1])
    return key, value


def _validate_structure(raw_config: dict[str, Any]) -> ConfigMappingType:
    """Helper function to narrow types for use by SQLFluff.

    This is a recursive function on any dict keys found.
    """
    validated_config: ConfigMappingType = {}
    for key, value in raw_config.items():
        if isinstance(value, dict):
            validated_config[key] = _validate_structure(value)
        elif isinstance(value, list):
            # Coerce all list items to strings, to be in line
            # with the behaviour of ini configs.
            validated_config[key] = [str(item) for item in value]
        elif isinstance(value, (str, int, float, bool)) or value is None:
            validated_config[key] = value
        else:  # pragma: no cover
            # Whatever we found, make it into a string.
            # This is very unlikely to happen and is more for completeness.
            validated_config[key] = str(value)
    return validated_config


def load_toml_file_config(filepath: str) -> ConfigMappingType:
    """Read the SQLFluff config section of a pyproject.toml file.

    We don't need to change any key names here, because the root
    section of the toml file format is `tool.sqlfluff.core`.

    NOTE: Toml files are always encoded in UTF-8. That is a necessary
    part of the toml spec: https://toml.io/en/v1.0.0
    """
    with open(filepath, mode="r", encoding="utf-8") as file:
        toml_dict = tomllib.loads(file.read())
    config_dict = _validate_structure(toml_dict.get("tool", {}).get("sqlfluff", {}))

    # NOTE: For the "rules" section of the sqlfluff config,
    # rule names are often qualified with a dot ".". In the
    # toml scenario this can get interpreted as a nested
    # section, and we resolve that edge case here.
    if "rules" not in config_dict:
        # No rules section, so no need to resolve.
        return config_dict

    rules_section = config_dict["rules"]
    assert isinstance(rules_section, dict), (
        "Expected to find section in `rules` section of config, "
        f"but instead found {rules_section}"
    )
    # Condense the rules section.
    config_dict["rules"] = records_to_nested_dict(
        _condense_rule_record(record)
        for record in iter_records_from_nested_dict(rules_section)
    )

    return config_dict

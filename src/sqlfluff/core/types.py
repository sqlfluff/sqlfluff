"""Enums used by sqlfluff."""

from enum import Enum
from typing import Union

from colorama import Fore

from sqlfluff.core.helpers.dict import NestedDictRecord, NestedStringDict

ConfigValueType = Union[int, float, bool, None, str]
# Ordinary config lists are coerced to strings on load. Templater context
# arrays may additionally contain nested lists and dictionaries.
ConfigValueOrListType = Union[
    ConfigValueType, list[Union["ConfigValueOrListType", "ConfigMappingType"]]
]
ConfigMappingType = NestedStringDict[ConfigValueOrListType]
ConfigRecordType = NestedDictRecord[ConfigValueOrListType]


class FormatType(Enum):
    """Enums for formatting types."""

    human = "human"
    json = "json"
    yaml = "yaml"
    sarif = "sarif"
    github_annotation = "github-annotation"
    github_annotation_native = "github-annotation-native"
    gitlab = "gitlab"
    none = "none"  # An option to return _no output_.


class Color(Enum):
    """Colors used by `colorize` function."""

    red = Fore.RED
    green = Fore.GREEN
    blue = Fore.BLUE
    light = Fore.YELLOW

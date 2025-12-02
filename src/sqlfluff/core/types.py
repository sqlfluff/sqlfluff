"""Enums used by sqlfluff."""

from enum import Enum
from typing import Union

from colorama import Fore

from sqlfluff.core.helpers.dict import NestedDictRecord, NestedStringDict

ConfigValueType = Union[int, float, bool, None, str]
# NOTE: We allow lists in the config types, but only lists
# of strings. Lists of other things are not allowed and should
# be rejected on load (or converted to strings). Given most
# config loading starts as strings, it's more likely that we
# just don't _try_ to convert lists from anything other than
# strings.
ConfigValueOrListType = Union[ConfigValueType, list[str]]
ConfigMappingType = NestedStringDict[ConfigValueOrListType]
ConfigRecordType = NestedDictRecord[ConfigValueOrListType]


class FormatType(Enum):
    """Enums for formatting types."""

    human = "human"
    json = "json"
    yaml = "yaml"
    github_annotation = "github-annotation"
    github_annotation_native = "github-annotation-native"
    none = "none"  # An option to return _no output_.


class Color(Enum):
    """Colors used by `colorize` function."""

    red = Fore.RED
    green = Fore.GREEN
    blue = Fore.BLUE
    light = Fore.YELLOW

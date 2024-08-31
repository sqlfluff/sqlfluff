"""Types common to several config loaders."""

from typing import List, Mapping, Union

ConfigValueType = Union[int, float, bool, None, str]
ConfigMappingType = Mapping[
    str, Union[ConfigValueType, "ConfigMappingType", List[ConfigValueType]]
]

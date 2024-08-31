"""Types common to several config loaders."""

from typing import List, Union

from sqlfluff.core.helpers.dict import NestedStringDict

ConfigValueType = Union[int, float, bool, None, str]
ConfigMappingType = NestedStringDict[Union[ConfigValueType, List[ConfigValueType]]]

"""Types common to several config loaders."""

from typing import List, Union

from sqlfluff.core.helpers.dict import NestedDictRecord, NestedStringDict

ConfigValueType = Union[int, float, bool, None, str]
ConfigValueOrListType = Union[ConfigValueType, List[ConfigValueType]]
ConfigMappingType = NestedStringDict[ConfigValueOrListType]
ConfigRecordType = NestedDictRecord[ConfigValueOrListType]

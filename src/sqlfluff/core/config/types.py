"""Types common to several config loaders."""

from typing import List, Union

from sqlfluff.core.helpers.dict import NestedDictRecord, NestedStringDict

ConfigValueType = Union[int, float, bool, None, str]
# NOTE: We allow lists in the config types, but only lists
# of strings. Lists of other things are not allowed and should
# be rejected on load (or converted to strings). Given most
# config loading starts as strings, it's more likely that we
# just don't _try_ to convert lists from anything other than
# strings.
ConfigValueOrListType = Union[ConfigValueType, List[str]]
ConfigMappingType = NestedStringDict[ConfigValueOrListType]
ConfigRecordType = NestedDictRecord[ConfigValueOrListType]

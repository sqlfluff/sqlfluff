"""Complex Type helpers."""
from typing import Optional, Tuple, FrozenSet, Union, Type

from sqlfluff.core.parser import Matchable, BaseSegment

SimpleHintType = Optional[Tuple[FrozenSet[str], FrozenSet[str]]]
MatchableType = Union[Matchable, Type[BaseSegment]]

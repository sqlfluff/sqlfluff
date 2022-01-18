"""Components for working with object and table references."""
from typing import List, Tuple


# TODO:
# - Extend to handle differing levels of specificity in the references
# - This may require tweaking the parameter types
def matches(possible_references: List[Tuple[str, ...]], targets: List[str]) -> bool:
    """Return True if any of the possible references matches a target."""
    if not possible_references:
        # Corner case: If there are no references, assume okay
        # (i.e. no mismatch = good).
        return True
    return any(pr in targets for pr in possible_references)

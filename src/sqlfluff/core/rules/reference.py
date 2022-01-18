"""Components for working with object and table references."""
from typing import Sequence, Tuple


def object_ref_matches_table(
    possible_references: Sequence[Tuple[str, ...]], targets: Sequence[Tuple[str, ...]]
) -> bool:
    """Return True if any of the possible references matches a target."""
    if not possible_references:
        # Corner case: If there are no references, assume okay
        # (i.e. no mismatch = good).
        return True
    return any(pr in targets for pr in possible_references)

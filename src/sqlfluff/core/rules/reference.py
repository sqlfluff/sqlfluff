"""Components for working with object and table references."""
from typing import Sequence, Tuple


def object_ref_matches_table(
    possible_references: Sequence[Tuple[str, ...]], targets: Sequence[Tuple[str, ...]]
) -> bool:
    """Return True if any of the possible references matches a target."""
    # Simple case: If there are no references, assume okay
    # (i.e. no mismatch = good).
    if not possible_references:
        return True
    # Simple case: Reference exactly matches a target.
    if any(pr in targets for pr in possible_references):
        return True
    # Tricky case: If reference is shorter than target, it's allowed to match a
    # suffix of the target. (Note this is an "optimistic" check, i.e. it assumes
    # the ignored parts of the target don't matter. In a SQL context, this is
    # basically assuming there was an earlier "USE <<database>>" or similar
    # directive.
    for pr in possible_references:
        for t in targets:
            if len(pr) < len(t) and pr == t[-len(pr) :]:
                return True
    return False

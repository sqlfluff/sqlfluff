"""Components for working with object and table references."""

from collections.abc import Collection, Sequence
from typing import Any

from sqlfluff.core.dialects.base import Dialect
from sqlfluff.core.dialects.common import (
    REFERENCE_FEATURE_DOT_ACCESS,
    REFERENCE_FEATURE_STRUCT_QUALIFICATION_AMBIGUITY,
    REFERENCE_FEATURES_SET,
)


def normalize_reference_part(part: str) -> str:
    """Normalize an identifier/reference part for case-insensitive comparisons."""
    return part.upper().strip("\"'`[]")


def dialect_supports_dot_access(dialect: Dialect) -> bool:
    """Return whether a dialect supports dot-access field navigation.

    This covers dialects where multi-part references may represent nested
    structures (e.g. ``table.column.field``) rather than only
    schema/table/column qualification.
    """
    return REFERENCE_FEATURE_DOT_ACCESS in dialect.sets(REFERENCE_FEATURES_SET)


def dialect_has_struct_qualification_ambiguity(dialect: Dialect) -> bool:
    """Return whether a dialect has ambiguous struct-like qualification."""
    return REFERENCE_FEATURE_STRUCT_QUALIFICATION_AMBIGUITY in dialect.sets(
        REFERENCE_FEATURES_SET
    )


def extract_reference_table_candidates(
    ref: Any, dialect: Dialect, available_tables: Collection[str] | None = None
) -> list[tuple[Any, str]]:
    """Extract candidate table references from an object reference.

    Returns a list of tuples: ``(reference_part, normalized_name)``.
    Candidates are de-duplicated by normalized name while preserving order.

    If ``available_tables`` is supplied and the dialect supports dot access,
    the leading part of a deep path (e.g. ``table.column.field``) is also
    considered a candidate.
    """
    candidates: list[tuple[Any, str]] = []

    for table_part in ref.extract_possible_references(level=ref.ObjectReferenceLevel.TABLE):
        candidates.append((table_part, normalize_reference_part(table_part.part)))

    if available_tables and dialect_supports_dot_access(dialect):
        raw_parts = list(ref.iter_raw_references())
        if len(raw_parts) > 2:
            leading_part = raw_parts[0]
            candidates.insert(
                0, (leading_part, normalize_reference_part(leading_part.part))
            )

    if available_tables is not None:
        normalized_available_tables = {
            normalize_reference_part(table) for table in available_tables
        }
        candidates = [
            (part, normalized)
            for part, normalized in candidates
            if normalized in normalized_available_tables
        ]

    deduped: list[tuple[Any, str]] = []
    seen: set[str] = set()
    for part, normalized in candidates:
        if normalized in seen:
            continue
        seen.add(normalized)
        deduped.append((part, normalized))
    return deduped


def object_ref_matches_table(
    possible_references: Sequence[tuple[str, ...]], targets: Sequence[tuple[str, ...]]
) -> bool:
    """Return True if any of the possible references matches a target."""
    # Simple case: If there are no references, assume okay
    # (i.e. no mismatch = good).
    if not possible_references:
        return True
    # Simple case: Reference exactly matches a target.
    if any(pr in targets for pr in possible_references):
        return True
    # Tricky case: If one is shorter than the other, check for a suffix match.
    # (Note this is an "optimistic" check, i.e. it assumes the ignored parts of
    # the target don't matter. In a SQL context, this is basically assuming
    # there was an earlier "USE <<database>>" or similar directive.
    for pr in possible_references:
        for t in targets:
            if (len(pr) < len(t) and pr == t[-len(pr) :]) or (
                len(t) < len(pr) and t == pr[-len(t) :]
            ):
                return True
    return False

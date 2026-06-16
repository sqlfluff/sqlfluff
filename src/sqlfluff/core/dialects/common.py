"""Common classes for dialects to use."""

import warnings
from collections.abc import Generator
from enum import Enum
from typing import NamedTuple, Optional, Protocol, Union, cast, runtime_checkable

from sqlfluff.core.parser import BaseSegment, RawSegment


class AliasInfo(NamedTuple):
    """Details about a table alias."""

    ref_str: str  # Name given to the alias
    segment: Optional[BaseSegment]  # Identifier segment containing the name
    aliased: bool
    from_expression_element: BaseSegment
    alias_expression: Optional[BaseSegment]
    object_reference: Optional[BaseSegment]


class ColumnAliasInfo(NamedTuple):
    """Details about a column alias."""

    alias_identifier_name: str
    aliased_segment: BaseSegment
    column_reference_segments: list[BaseSegment]


class ObjectReferencePart(NamedTuple):
    """Details about a part of an object reference."""

    part: str  # Name of the part
    # Segment(s) comprising the part. Usually just one segment, but could
    # be multiple in dialects (e.g. BigQuery) that support unusual
    # characters in names (e.g. "-")
    segments: list[RawSegment]


@runtime_checkable
class _SupportsIterRawReferences(Protocol):
    """An object reference segment exposing the legacy ``iter_raw_references``.

    Used to type (and guard) the back-compat ``dialect_name=None`` dispatch path
    without importing the concrete dialect segment classes -- doing so would be a
    circular import and a forbidden ``core -> dialects`` dependency.
    """

    def iter_raw_references(self) -> Generator["ObjectReferencePart", None, None]:
        """Yield the reference parts of this object reference."""
        ...


class ObjectReferenceLevel(Enum):
    """Labels for the "levels" of a reference.

    Note: Since SQLFluff does not have access to database catalog
    information, interpreting references will often be ambiguous.
    Typical example: The first part *may* refer to a schema, but that is
    almost always optional if referring to an object in some default or
    currently "active" schema. For this reason, use of this enum is optional
    and intended mainly to clarify the intent of the code -- no guarantees!
    Additionally, the terminology may vary by dialect, e.g. in BigQuery,
    "project" would be a more accurate term than "schema".
    """

    OBJECT = 1
    TABLE = 2
    SCHEMA = 3


def _level_to_int(level: Union[ObjectReferenceLevel, int]) -> int:
    # If it's an ObjectReferenceLevel, get the value. Otherwise, assume it's
    # an int.
    level = getattr(level, "value", level)
    assert isinstance(level, int)
    return level


# =============================================================================
# Functional helpers for object references.
#
# These mirror methods that historically lived on ObjectReferenceSegment (and
# its dialect-specific subclasses). They are defined here as free functions
# that dispatch on the dialect name + segment type so that the logic is
# portable (e.g. to the Rust parser, where segments are generic and carry only
# their type information plus a dialect name). The corresponding segment
# methods are retained as deprecated thin wrappers that delegate here.
# =============================================================================


def deprecated_segment_method(old: str, new: str) -> None:
    """Warn that a reference/alias segment method is deprecated.

    These methods have been replaced by the free functions in this module so
    that the logic can be dispatched on the dialect name + segment type (rather
    than the Python segment class), which is a prerequisite for porting the
    rules that use them to Rust. Call this from the deprecated wrapper methods.
    """
    warnings.warn(
        f"{old} is deprecated and will be removed in a future release. "
        f"Use sqlfluff.core.dialects.common.{new} instead.",
        DeprecationWarning,
        stacklevel=3,
    )


def _iter_raw_references_default(
    segment: BaseSegment, *, split_on_dots: bool
) -> Generator[ObjectReferencePart, None, None]:
    """Yield the reference parts of a generic object reference.

    When ``split_on_dots`` is True (e.g. BigQuery's splittable references), each
    identifier is further split on embedded dots.
    """
    for elem in segment.recursive_crawl("identifier"):
        raw_trimmed = cast(RawSegment, elem).raw_trimmed()
        if split_on_dots:
            for part in raw_trimmed.split("."):
                yield ObjectReferencePart(part, [cast(RawSegment, elem)])
        else:
            yield ObjectReferencePart(raw_trimmed, [cast(RawSegment, elem)])


def _iter_raw_references_wildcard(
    segment: BaseSegment,
) -> Generator[ObjectReferencePart, None, None]:
    """Yield the reference parts of a wildcard identifier (includes ``star``)."""
    for elem in segment.recursive_crawl("identifier", "star"):
        yield ObjectReferencePart(
            cast(RawSegment, elem).raw_trimmed(), [cast(RawSegment, elem)]
        )


def _iter_raw_references_bigquery_table(
    segment: BaseSegment,
) -> Generator[ObjectReferencePart, None, None]:
    """Yield reference parts for a BigQuery table reference.

    Overrides the default because hyphens (DashSegment) cause one logical part
    of the name to be split across multiple elements, e.g. "table-a" is parsed
    as three segments.
    """
    # For each descendant element, group them, using "dot" elements as a
    # delimiter.
    parts: list[str] = []
    elems_for_parts: list[RawSegment] = []

    def flush() -> ObjectReferencePart:
        nonlocal parts, elems_for_parts
        result = ObjectReferencePart("".join(parts), elems_for_parts)
        parts = []
        elems_for_parts = []
        return result

    for elem in segment.recursive_crawl("identifier", "literal", "dash", "dot", "star"):
        if not elem.is_type("dot"):
            if elem.is_type("identifier"):
                # Found an identifier (potentially with embedded dots).
                elem_subparts = cast(RawSegment, elem).raw_trimmed().split(".")
                for idx, part in enumerate(elem_subparts):
                    # Save each part of the segment.
                    parts.append(part)
                    elems_for_parts.append(cast(RawSegment, elem))

                    if idx != len(elem_subparts) - 1:
                        # For each part except the last, flush.
                        yield flush()
            else:
                # For non-identifier segments, save the whole segment.
                parts.append(cast(RawSegment, elem).raw_trimmed())
                elems_for_parts.append(cast(RawSegment, elem))
        else:
            yield flush()

    # Flush any leftovers.
    if parts:
        yield flush()


def iter_raw_references(
    segment: BaseSegment, dialect_name: Optional[str]
) -> Generator[ObjectReferencePart, None, None]:
    """Generate the reference parts of an object reference.

    Dispatches on the dialect name and segment type to reproduce the behavior
    previously provided by dialect-specific segment subclasses.

    ``dialect_name`` of None is a back-compat path for the deprecated segment
    method wrappers (which have no dialect to hand): it dispatches via the
    segment's own (deprecated) ``iter_raw_references`` method so that Python
    class dispatch -- and therefore the exact legacy behavior -- still applies.
    Always pass the real dialect name from non-deprecated call sites.
    """
    if dialect_name is None:
        assert isinstance(segment, _SupportsIterRawReferences), (
            "iter_raw_references(segment, None) requires an object reference "
            f"segment (with a legacy iter_raw_references method); got {segment.type!r}"
        )
        yield from segment.iter_raw_references()
        return
    if segment.is_type("wildcard_identifier"):
        yield from _iter_raw_references_wildcard(segment)
        return
    if dialect_name == "bigquery":
        if segment.is_type("table_reference"):
            yield from _iter_raw_references_bigquery_table(segment)
            return
        if segment.is_type("column_reference"):
            yield from _iter_raw_references_default(segment, split_on_dots=True)
            return
    yield from _iter_raw_references_default(segment, split_on_dots=False)


def _raw_refs(
    segment: BaseSegment, dialect_name: Optional[str]
) -> list[ObjectReferencePart]:
    """Collect the raw reference parts of a segment."""
    return list(iter_raw_references(segment, dialect_name))


def is_qualified(segment: BaseSegment, dialect_name: Optional[str]) -> bool:
    """Return whether there is more than one element to the reference."""
    return len(_raw_refs(segment, dialect_name)) > 1


def qualification(segment: BaseSegment, dialect_name: Optional[str]) -> str:
    """Return the qualification type of this reference."""
    return "qualified" if is_qualified(segment, dialect_name) else "unqualified"


def _extract_possible_references_default(
    segment: BaseSegment,
    level: Union[ObjectReferenceLevel, int],
    dialect_name: Optional[str],
) -> list[ObjectReferencePart]:
    """Extract possible references of a given level."""
    level_int = _level_to_int(level)
    refs = _raw_refs(segment, dialect_name)
    if len(refs) >= level_int:
        return [refs[-level_int]]
    return []


def _extract_possible_references_bigquery_column(
    segment: BaseSegment,
    level: Union[ObjectReferenceLevel, int],
    dialect_name: Optional[str],
) -> list[ObjectReferencePart]:
    """Extract possible references of a given level for a BigQuery column.

    BigQuery's support for things like the following:
    - Functions that take a table as a parameter (e.g. TO_JSON_STRING)
      https://cloud.google.com/bigquery/docs/reference/standard-sql/
      json_functions#to_json_string
    - STRUCT

    means that, without schema information (which SQLFluff does not have),
    references to data are often ambiguous.
    """
    level_int = _level_to_int(level)
    refs = _raw_refs(segment, dialect_name)
    if level_int == ObjectReferenceLevel.SCHEMA.value and len(refs) >= 3:
        return [refs[0]]  # pragma: no cover
    if level_int == ObjectReferenceLevel.TABLE.value:
        # One part: Could be a table, e.g. TO_JSON_STRING(t)
        # Two parts: Could be dataset.table or table.column.
        # Three parts: Could be table.column.struct or dataset.table.column.
        # Four parts: dataset.table.column.struct
        # Five parts: project.dataset.table.column.struct
        # So... return the first 3 parts.
        return refs[:3]
    if (
        level_int == ObjectReferenceLevel.OBJECT.value and len(refs) >= 3
    ):  # pragma: no cover
        # Ambiguous case: The object (i.e. column) could be the first or
        # second part, so return both.
        return [refs[1], refs[2]]
    return _extract_possible_references_default(
        segment, level, dialect_name
    )  # pragma: no cover


def extract_possible_references(
    segment: BaseSegment,
    level: Union[ObjectReferenceLevel, int],
    dialect_name: Optional[str],
) -> list[ObjectReferencePart]:
    """Extract possible references of a given level.

    "level" may be (but is not required to be) a value from the
    ObjectReferenceLevel enum defined above.

    NOTE: The base implementation here returns at most one part, but
    dialects such as BigQuery that support nesting (e.g. STRUCT) may return
    multiple reference parts.
    """
    if dialect_name == "bigquery" and segment.is_type("column_reference"):
        return _extract_possible_references_bigquery_column(
            segment, level, dialect_name
        )
    return _extract_possible_references_default(segment, level, dialect_name)


def _extract_possible_multipart_references_default(
    segment: BaseSegment,
    levels: list[Union[ObjectReferenceLevel, int]],
    dialect_name: Optional[str],
) -> list[tuple[ObjectReferencePart, ...]]:
    """Extract possible multipart references, e.g. schema.table."""
    levels_tmp = [_level_to_int(level) for level in levels]
    min_level = min(levels_tmp)
    max_level = max(levels_tmp)
    refs = _raw_refs(segment, dialect_name)
    if len(refs) >= max_level:
        return [tuple(refs[-max_level : 1 - min_level])]
    return []


def _extract_possible_multipart_references_bigquery_column(
    segment: BaseSegment,
    levels: list[Union[ObjectReferenceLevel, int]],
    dialect_name: Optional[str],
) -> list[tuple[ObjectReferencePart, ...]]:
    """Extract possible multipart references for a BigQuery column."""
    levels_tmp = [_level_to_int(level) for level in levels]
    min_level = min(levels_tmp)
    max_level = max(levels_tmp)
    refs = _raw_refs(segment, dialect_name)
    if max_level == ObjectReferenceLevel.SCHEMA.value and len(refs) >= 3:
        return [tuple(refs[0 : max_level - min_level + 1])]
    # Note we aren't handling other possible cases. We'll add these as
    # needed.
    return _extract_possible_multipart_references_default(segment, levels, dialect_name)


def extract_possible_multipart_references(
    segment: BaseSegment,
    levels: list[Union[ObjectReferenceLevel, int]],
    dialect_name: Optional[str],
) -> list[tuple[ObjectReferencePart, ...]]:
    """Extract possible multipart references, e.g. schema.table."""
    if dialect_name == "bigquery" and segment.is_type("column_reference"):
        return _extract_possible_multipart_references_bigquery_column(
            segment, levels, dialect_name
        )
    return _extract_possible_multipart_references_default(segment, levels, dialect_name)


# =============================================================================
# Functional helpers for "eventual" aliases of FROM / JOIN segments.
# =============================================================================


def get_from_expression_element_alias(
    segment: BaseSegment, dialect_name: Optional[str]
) -> Generator[AliasInfo, None, None]:
    """Return the eventual table name referred to by a table expression.

    ``segment`` should be a ``from_expression_element``.
    """
    # Get any table expressions
    tbl_expression = segment.get_child("table_expression")
    if not tbl_expression:  # pragma: no cover
        _bracketed = segment.get_child("bracketed")
        if _bracketed:
            tbl_expression = _bracketed.get_child("table_expression")
    # For TSQL nested, bracketed tables get the first table as reference
    if tbl_expression and not tbl_expression.get_child("object_reference"):
        _bracketed = tbl_expression.get_child("bracketed")
        if _bracketed:
            tbl_expression = _bracketed.get_child("table_expression")

    # Work out the references
    ref: Optional[BaseSegment] = None
    if tbl_expression:
        ref = tbl_expression.get_child("object_reference")

    # Handle any aliases
    has_alias = False
    alias_expressions = segment.get_children("alias_expression", "bracketed")
    for alias_expression in alias_expressions:
        if alias_expression.is_type("bracketed"):  # pragma: no cover
            _alias_expression = alias_expression.get_child("alias_expression")
            if _alias_expression is None:
                continue
            alias_expression = _alias_expression
        # If it has an alias, return that
        has_alias = True
        alias_segment = alias_expression.get_child("identifier")
        if alias_segment:
            yield AliasInfo(
                alias_segment.raw_normalized(casefold=False),
                alias_segment,
                True,
                segment,
                alias_expression,
                ref,
            )
    if has_alias:
        return

    # If not return the object name (or None if there isn't one)
    if ref:
        references = list(iter_raw_references(ref, dialect_name))
        # Return the last element of the reference.
        if references:
            penultimate_ref = references[-1]
            yield AliasInfo(
                penultimate_ref.part,
                penultimate_ref.segments[0],
                False,
                segment,
                None,
                ref,
            )
            return
    # No references or alias
    yield AliasInfo(
        "",
        None,
        False,
        segment,
        None,
        ref,
    )


def get_join_clause_aliases(
    segment: BaseSegment, dialect_name: Optional[str]
) -> list[tuple[BaseSegment, AliasInfo]]:
    """Return the eventual table name referred to by a join clause."""
    buff = []

    from_expression = segment.get_child("from_expression_element")
    # As per grammar, there will always be a FromExpressionElementSegment
    assert from_expression
    from_aliases = get_from_expression_element_alias(from_expression, dialect_name)
    # Only append if non-null. A None reference, may
    # indicate a generator expression or similar.
    for alias in from_aliases:
        buff.append((from_expression, alias))

    # In some dialects, like TSQL, join clauses can have nested join clauses
    # recurse into them - but not if part of a sub-select statement (see #3144)
    for join_clause in segment.recursive_crawl(
        "join_clause", no_recursive_seg_type="select_statement"
    ):
        if join_clause is segment:
            # If the starting segment itself matches the list of types we're
            # searching for, recursive_crawl() will return it. Skip that.
            continue
        aliases = get_join_clause_aliases(join_clause, dialect_name)
        # Only append if non-null. A None reference, may
        # indicate a generator expression or similar.
        if aliases:
            buff = buff + aliases
    return buff


def get_from_clause_aliases(
    segment: BaseSegment, dialect_name: Optional[str]
) -> list[tuple[BaseSegment, AliasInfo]]:
    """List the eventual aliases of a from clause.

    Comes as a list of tuples (table expr, tuple (string, segment, bool)).
    """
    buff: list[tuple[BaseSegment, AliasInfo]] = []
    direct_table_children = []
    join_clauses = []

    for from_expression in segment.get_children("from_expression"):
        direct_table_children += from_expression.get_children("from_expression_element")
        join_clauses += from_expression.get_children("join_clause")

    # Iterate through the potential sources of aliases
    for clause in direct_table_children:
        direct_table_aliases = get_from_expression_element_alias(clause, dialect_name)
        # Only append if non-null. A None reference, may
        # indicate a generator expression or similar.
        table_expr = (
            clause
            if clause in direct_table_children
            else clause.get_child("from_expression_element")
        )
        for alias in direct_table_aliases:
            assert table_expr
            buff.append((table_expr, alias))
    for clause in join_clauses:
        aliases = get_join_clause_aliases(clause, dialect_name)
        # Only append if non-null. A None reference, may
        # indicate a generator expression or similar.
        if aliases:
            buff = buff + aliases
    return buff

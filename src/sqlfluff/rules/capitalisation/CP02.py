"""Implementation of Rule CP02."""

from typing import Optional

from sqlfluff.core.parser import BaseSegment, SourceFix
from sqlfluff.core.rules import LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.rules.capitalisation.CP01 import Rule_CP01
from sqlfluff.utils.identifers import identifiers_policy_applicable


class Rule_CP02(Rule_CP01):
    """Inconsistent capitalisation of unquoted identifiers.

    This rule applies to all unquoted identifiers, whether references
    or aliases, and whether they refer to columns or other objects (such
    as tables or schemas).

    .. note::

       In **most** dialects, unquoted identifiers are treated as case-insensitive
       and so the fixes proposed by this rule do not change the interpretation
       of the query. **HOWEVER**, some databases (notably :ref:`bigquery_dialect_ref`,
       :ref:`trino_dialect_ref` and :ref:`clickhouse_dialect_ref`) do take the casing
       of *unquoted* identifiers into account when determining the casing of the column
       heading in the *result*.

       As this feature is only present in a few dialects, and not widely understood
       by users, we regard it as *an antipattern*. It is more widely understood that
       if the case of an identifier *matters*, then it should be quoted. If you, or
       your organisation, do wish to rely on this feature, we recommend that you
       disabled this rule (see :ref:`ruleselection`).

    **Anti-pattern**

    In this example, unquoted identifier ``a`` is in lower-case but
    ``B`` is in upper-case.

    .. code-block:: sql

        select
            a,
            B
        from foo

    In this more complicated example, there are a mix of capitalisations
    in both reference and aliases of columns and tables. That inconsistency
    is acceptable when those identifiers are quoted, but not when unquoted.

    .. code-block:: sql

        select
            col_1 + Col_2 as COL_3,
            "COL_4" as Col_5
        from Foo as BAR

    **Best practice**

    Ensure all unquoted identifiers are either in upper-case or in lower-case.

    .. code-block:: sql

        select
            a,
            b
        from foo;

        -- ...also good...

        select
            A,
            B
        from foo;

        --- ...or for comparison with our more complex example, this too:

        select
            col_1 + col_2 as col_3,
            "COL_4" as col_5
        from foo as bar

    """

    name = "capitalisation.identifiers"
    aliases = ("L014",)
    is_fix_compatible = True
    # Check identifiers which mix templated and literal source text.
    targets_templated = True

    crawl_behaviour = SegmentSeekerCrawler(
        {"naked_identifier", "properties_naked_identifier"}
    )
    config_keywords = [
        "extended_capitalisation_policy",
        "unquoted_identifiers_policy",
        "ignore_words",
        "ignore_words_regex",
    ]
    _description_elem = "Unquoted identifiers"

    def _eval(self, context: RuleContext) -> Optional[list[LintResult]]:
        # Return None if identifier is case-sensitive property to enable Change
        # Data Feed
        # https://docs.delta.io/2.0.0/delta-change-data-feed.html#enable-change-data-feed
        if (
            context.dialect.name in ["databricks", "sparksql"]
            and context.parent_stack
            and context.parent_stack[-1].type == "property_name_identifier"
            and context.segment.raw == "enableChangeDataFeed"
        ):
            return None

        # Skip segments whose source is entirely templated (e.g., placeholder
        # parameters like :accountId) to avoid incorrect qualification
        # suggestions. Identifiers which mix templated and literal source text
        # (e.g. {{ env_type }}_MY_DB) are still checked, against their literal
        # portion only (see _raw_for_capitalisation below).
        if context.segment.is_templated and not self._literal_source(context.segment):
            return [LintResult(memory=context.memory)]

        if identifiers_policy_applicable(
            self.unquoted_identifiers_policy,  # type: ignore
            context.parent_stack,
        ):
            return super()._eval(context=context)
        else:
            return [LintResult(memory=context.memory)]

    def _literal_source_spans(self, segment: BaseSegment) -> list[tuple[int, int]]:
        """Return the source offsets of the segment's literal portions.

        Only literal raw slices are considered, so templated blocks are
        never included. An empty list indicates that the segment's source
        is entirely templated (i.e. the user didn't write any of it).
        """
        source_slice = segment.pos_marker.source_slice
        spans = []
        for raw_slice in segment.pos_marker.templated_file.raw_sliced:
            if raw_slice.slice_type != "literal":
                continue
            start = max(raw_slice.source_idx, source_slice.start)
            stop = min(raw_slice.end_source_idx(), source_slice.stop)
            if stop > start:
                spans.append((start, stop))
        return spans

    def _literal_source(self, segment: BaseSegment) -> str:
        """Return the non-templated source text of the segment.

        An empty string indicates that the segment's source is entirely
        templated (i.e. the user didn't write any of it directly).
        """
        templated_file = segment.pos_marker.templated_file
        return "".join(
            templated_file.source_str[start:stop]
            for start, stop in self._literal_source_spans(segment)
        )

    def _is_mixed_templated_segment(self, segment: BaseSegment) -> bool:
        # Mixed segments are checked against their literal portion (see
        # _raw_for_capitalisation), so they must not be skipped outright.
        return segment.is_templated and bool(self._literal_source(segment))

    def _raw_for_capitalisation(self, segment: BaseSegment) -> str:
        # For identifiers mixing templated and literal source text, check
        # only the literal portion. The templated portion is generated code
        # whose casing is outside the user's control here.
        literal = self._literal_source(segment)
        if segment.is_templated and literal:
            return literal
        return segment.raw

    def _get_fix(self, segment: BaseSegment, fixed_raw: str) -> LintFix:
        pos_marker = segment.pos_marker
        # A plain edit can be discarded as unsafe for identifiers which
        # follow templated code in the source (their source and templated
        # offsets differ), so recase via a source-level fix in that case.
        spans = (
            self._literal_source_spans(segment)
            if self._literal_source(segment)
            and pos_marker.source_slice != pos_marker.templated_slice
            else []
        )
        if spans:
            # Recase only the literal portions of the source, leaving any
            # templated blocks untouched, via a source-level fix. Each
            # literal span is recased independently, so literals which are
            # split by templated blocks are handled correctly, and templated
            # code is never edited.
            source_str = pos_marker.source_str()
            literal = self._literal_source(segment)
            # Work out which case transformation maps the literal source onto
            # the fixed value, and apply it to each literal span.
            if fixed_raw == literal.lower():
                recase = str.lower
            elif fixed_raw == literal.upper():
                recase = str.upper
            elif fixed_raw == literal.capitalize():
                recase = str.capitalize
            else:
                # Unrecognised transformation: fall back to a default fix.
                return super()._get_fix(segment, fixed_raw)
            # Replace spans from the end so earlier offsets stay valid.
            # Spans are absolute source offsets; convert them to offsets
            # within the segment's own source text.
            source_start = segment.pos_marker.source_slice.start
            new_source_str = source_str
            for start, stop in reversed(spans):
                start -= source_start
                stop -= source_start
                new_source_str = (
                    new_source_str[:start]
                    + recase(source_str[start:stop])
                    + new_source_str[stop:]
                )
            edit_segment = segment.edit(
                segment.raw,
                source_fixes=[
                    SourceFix(
                        new_source_str,
                        pos_marker.source_slice,
                        pos_marker.templated_slice,
                    )
                ],
            )
            return LintFix.replace(segment, [edit_segment])
        return super()._get_fix(segment, fixed_raw)

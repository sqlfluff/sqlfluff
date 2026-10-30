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
    # Identifiers that mix templated and literal source text are checked
    # against their literal text, so keep those violations.
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
        # suggestions. Partly templated ones are handled in _handle_segment.
        if context.segment.is_templated and not self._literal_spans(context.segment):
            return [LintResult(memory=context.memory)]

        if identifiers_policy_applicable(
            self.unquoted_identifiers_policy,  # type: ignore
            context.parent_stack,
        ):
            return super()._eval(context=context)
        else:
            return [LintResult(memory=context.memory)]

    # Stands in for each templated part of an identifier when its literal text
    # is checked, so the literal parts read as one word with the template
    # output inside it. A digit has no case and doesn't start a word.
    _TEMPLATE_STAND_IN = "0"

    def _handle_segment(
        self,
        segment: BaseSegment,
        context: RuleContext,
        raw: Optional[str] = None,
    ) -> LintResult:
        """Check an identifier, using only its literal text if partly templated.

        For ``{{ env }}_MY_DB`` only ``_MY_DB`` was written by the user, so
        only that is checked and fixed. Any fix is applied to the source text
        of the literal parts, leaving the template untouched. If the fixed
        text can't be mapped back onto those parts character for character,
        the violation is reported without a fix.
        """
        spans = self._literal_spans(segment) if segment.is_templated else []
        # A segment that already has source fixes was fixed on an earlier loop.
        if not spans or segment.source_fixes:
            return super()._handle_segment(segment, context, raw)
        pos_marker = segment.pos_marker
        assert pos_marker

        # Snake case splits words at digits, so it gets no stand-in.
        stand_in = (
            ""
            if self.extended_capitalisation_policy == "snake"  # type: ignore
            else self._TEMPLATE_STAND_IN
        )
        check_raw = ""
        offsets = []
        cursor = pos_marker.source_slice.start
        for source_idx, text in spans:
            if source_idx > cursor:
                check_raw += stand_in
            offsets.append(len(check_raw))
            check_raw += text
            cursor = source_idx + len(text)
        if cursor < pos_marker.source_slice.stop:
            check_raw += stand_in

        result = super()._handle_segment(segment, context, check_raw)
        if not result.fixes:
            return result

        fixed_raw = result.fixes[0].edit[0].raw  # type: ignore
        if len(fixed_raw) != len(check_raw):
            # e.g. snake case added an underscore. Report it, but don't fix it.
            result.fixes = []
            return result

        # Rebuild the identifier's source with the fixed literal parts and the
        # template text copied through unchanged. A fix can only carry one
        # source edit, so this replaces the whole identifier's source.
        source_slice = pos_marker.source_slice
        source = pos_marker.templated_file.source_str[source_slice]
        for (source_idx, text), offset in zip(spans, offsets):
            start = source_idx - source_slice.start
            source = (
                source[:start]
                + fixed_raw[offset : offset + len(text)]
                + source[start + len(text) :]
            )
        source_fix = SourceFix(source, source_slice, pos_marker.templated_slice)
        result.fixes = [
            LintFix.replace(segment, [segment.edit(source_fixes=[source_fix])])
        ]
        return result

    @staticmethod
    def _literal_spans(segment: BaseSegment) -> list[tuple[int, str]]:
        """Return the literal parts of a segment's source.

        Each part is a ``(source index, text)`` pair. An empty list means the
        source is entirely templated.
        """
        pos_marker = segment.pos_marker
        assert pos_marker
        source_slice = pos_marker.source_slice
        spans = []
        templated_file = pos_marker.templated_file
        for raw_slice in templated_file.raw_slices_spanning_source_slice(source_slice):
            if raw_slice.slice_type != "literal":
                continue
            start = max(raw_slice.source_idx, source_slice.start)
            stop = min(raw_slice.end_source_idx(), source_slice.stop)
            if stop > start:
                text = raw_slice.raw[
                    start - raw_slice.source_idx : stop - raw_slice.source_idx
                ]
                spans.append((start, text))
        return spans

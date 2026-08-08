"""Implementation of Rule JJ01."""

from sqlfluff.core.parser.segments import BaseSegment, SourceFix
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import RootOnlyCrawler
from sqlfluff.core.templaters import JinjaTemplater


class Rule_JJ01(BaseRule):
    """Jinja tags should have a single whitespace on either side.

    This rule is only active if the ``jinja`` templater (or one of it's
    subclasses, like the ``dbt`` templater) are used for the current file.

    **Anti-pattern**

    Jinja tags with either no whitespace or very long whitespace
    are hard to read.

    .. code-block:: jinja
       :force:

        SELECT {{    a     }} from {{ref('foo')}}

    **Best practice**

    A single whitespace surrounding Jinja tags, alternatively
    longer gaps containing newlines are acceptable.

    .. code-block:: jinja
       :force:

        SELECT {{ a }} from {{ ref('foo') }};
        SELECT {{ a }} from {{
            ref('foo')
        }};
    """

    name = "jinja.padding"
    aliases = ("L046",)
    groups = ("all", "core", "jinja")
    crawl_behaviour = RootOnlyCrawler()
    targets_templated = True
    is_fix_compatible = True

    @staticmethod
    def _get_whitespace_ends(
        s: str, open_delim: str, close_delim: str
    ) -> tuple[str, str, str, str, str]:
        """Remove tag ends and partition off any whitespace ends.

        This function assumes that we've already trimmed the string
        to just the tag, and will raise an AssertionError if not.
        >>> Rule_JJ01._get_whitespace_ends('  {{not_trimmed}}   ', '{{', '}}')
        Traceback (most recent call last):
            ...
        AssertionError

        In essence it divides up a tag into the end tokens, any
        leading or trailing whitespace and the inner content
        >>> Rule_JJ01._get_whitespace_ends('{{ my_content }}', '{{', '}}')
        ('{{', ' ', 'my_content', ' ', '}}')

        It also works with block tags and more complicated content
        and end markers.
        >>> Rule_JJ01._get_whitespace_ends('{%+if a + b is True     -%}', '{%', '%}')
        ('{%+', '', 'if a + b is True', '     ', '-%}')
        """
        assert s.startswith(open_delim) and s.endswith(close_delim)
        pre_len = len(open_delim)
        post_len = len(close_delim)
        main = s[pre_len:-post_len]
        pre = s[:pre_len]
        post = s[-post_len:]
        modifier_chars = ["+", "-"]
        if main and main[0] in modifier_chars:
            main = main[1:]
            pre = s[: pre_len + 1]
        if main and main[-1] in modifier_chars:
            main = main[:-1]
            post = s[-(post_len + 1) :]
        inner = main.strip()
        pos = main.find(inner)
        return pre, main[:pos], inner, main[pos + len(inner) :], post

    @classmethod
    def _find_raw_at_src_idx(cls, segment: BaseSegment, src_idx: int):
        """Recursively search to find a raw segment for a position in the source.

        NOTE: This assumes it's not being called on a `raw`.

        In the case that there are multiple potential targets, we will find the
        first.
        """
        assert segment.segments
        for seg in segment.segments:
            if not seg.pos_marker:  # pragma: no cover
                continue
            src_slice = seg.pos_marker.source_slice
            # If it's before, skip onward.
            if src_slice.stop <= src_idx:
                continue
            # Is the current segment raw?
            if seg.is_raw():
                return seg
            # Otherwise recurse
            return cls._find_raw_at_src_idx(seg, src_idx)

    def _eval(self, context: RuleContext) -> list[LintResult]:
        """Look for non-literal segments.

        NOTE: The existing crawlers don't filter very well for only templated
        code, and so we process the whole file from the root here.
        """
        # If the position maker for the root segment is literal then there's
        # no templated code. So we can return early.
        assert context.segment.pos_marker
        if context.segment.pos_marker.is_literal():
            return []

        # We'll need the templated file. If for whatever reason it's
        # not present, abort.
        if not context.templated_file:  # pragma: no cover
            return []

        # We also only work with setups which use the jinja templater
        # or a derivative of that. Otherwise return empty.
        # NOTE: The `templater_obj` is not available in parallel operations
        # and we don't really want to rehydrate a templater just to check
        # what type it is, so use `get_templater_class()`.
        _templater_class = context.config.get_templater_class()
        if not issubclass(_templater_class, JinjaTemplater):
            self.logger.debug(f"Detected non-jinja templater: {_templater_class.name}")
            return []

        # Read the configured Jinja delimiters so we can match tags
        # that use custom delimiters (e.g. Snowflake CLI's <% var %>).
        delimiters = set()
        for key in (
            "variable_start_string",
            "block_start_string",
            "comment_start_string",
        ):
            val = context.config.get_section(("templater", "jinja", key))
            if val:
                delimiters.add(val)
        # Default Jinja delimiters
        open_delims = delimiters or {"{{", "{%", "{#"}
        close_delims = set()
        for key in (
            "variable_end_string",
            "block_end_string",
            "comment_end_string",
        ):
            val = context.config.get_section(("templater", "jinja", key))
            if val:
                close_delims.add(val)
        if not close_delims:
            close_delims = {"}}", "%}", "#}"}

        results = []
        # Work through the templated slices
        for raw_slice in context.templated_file.raw_sliced:
            # We only want templated slices.
            if raw_slice.slice_type not in ("templated", "block_start", "block_end"):
                continue

            stripped = raw_slice.raw.strip()
            if not stripped:
                continue  # pragma: no cover

            # Match against any of the configured opening/closing delimiters
            open_delim = None
            close_delim = None
            for d in open_delims:
                if stripped.startswith(d):
                    open_delim = d
                    break
            if open_delim:
                for d in close_delims:
                    if stripped.endswith(d):
                        close_delim = d
                        break

            if not open_delim or not close_delim:
                continue  # pragma: no cover

            self.logger.debug(
                "Tag found @ source index %s: %r ", raw_slice.source_idx, stripped
            )

            # Partition and Position
            src_idx = raw_slice.source_idx
            tag_pre, ws_pre, inner, ws_post, tag_post = self._get_whitespace_ends(
                stripped, open_delim, close_delim
            )
            position = raw_slice.raw.find(stripped[0])

            self.logger.debug(
                "Tag string segments: %r | %r | %r | %r | %r @ %s + %s",
                tag_pre,
                ws_pre,
                inner,
                ws_post,
                tag_post,
                src_idx,
                position,
            )

            # For the following section, whitespace should be a single
            # whitespace OR it should contain a newline.

            pre_fix = None
            post_fix = None
            # Check the initial whitespace.
            if not ws_pre or (ws_pre != " " and "\n" not in ws_pre):
                pre_fix = " "
            # Check latter whitespace.
            if not ws_post or (ws_post != " " and "\n" not in ws_post):
                post_fix = " "

            # If no fixes, continue
            if pre_fix is None and post_fix is None:
                continue

            fixed = (
                tag_pre + (pre_fix or ws_pre) + inner + (post_fix or ws_post) + tag_post
            )

            # We need to identify a raw segment to attach to fix to.
            raw_seg = self._find_raw_at_src_idx(context.segment, src_idx)

            # If that raw segment already has fixes, don't apply it again.
            # We're likely on a second pass.
            if raw_seg.source_fixes:
                continue

            source_fixes = [
                SourceFix(
                    fixed,
                    slice(
                        src_idx + position,
                        src_idx + position + len(stripped),
                    ),
                    # This position in the templated file is rough, but
                    # close enough for sequencing.
                    raw_seg.pos_marker.templated_slice,
                )
            ]

            results.append(
                LintResult(
                    anchor=raw_seg,
                    description=f"Jinja tags should have a single "
                    f"whitespace on either side: {stripped}",
                    fixes=[
                        LintFix.replace(
                            raw_seg,
                            [raw_seg.edit(source_fixes=source_fixes)],
                        )
                    ],
                )
            )

        return results

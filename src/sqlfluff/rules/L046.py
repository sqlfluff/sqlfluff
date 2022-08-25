"""Implementation of Rule L046."""
from typing import Tuple
from sqlfluff.core.parser.segments import SourceFix

from sqlfluff.core.rules import (
    BaseRule,
    EvalResultType,
    LintResult,
    LintFix,
    RuleContext,
)
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.functional import rsp, FunctionalContext
from sqlfluff.core.rules.doc_decorators import document_groups


@document_groups
class Rule_L046(BaseRule):
    """Jinja tags should have a single whitespace on either side.

    **Anti-pattern**

    Jinja tags with either no whitespace or very long whitespace
    are hard to read.

    .. code-block:: sql
       :force:

        SELECT {{    a     }} from {{ref('foo')}}

    **Best practice**

    A single whitespace surrounding Jinja tags, alternatively
    longer gaps containing newlines are acceptable.

    .. code-block:: sql
       :force:

        SELECT {{ a }} from {{ ref('foo') }};
        SELECT {{ a }} from {{
            ref('foo')
        }};
    """

    groups = ("all", "core")
    # Crawling for "raw" isn't a great way of filtering but it will
    # do for now. TODO: Make a more efficient crawler for templated
    # sections.
    crawl_behaviour = SegmentSeekerCrawler({"raw"})
    targets_templated = True

    @staticmethod
    def _get_whitespace_ends(s: str) -> Tuple[str, str, str, str, str]:
        """Remove tag ends and partition off any whitespace ends.

        This function assumes that we've already trimmed the string
        to just the tag, and will raise an AssertionError if not.
        >>> Rule_L046._get_whitespace_ends('  {{not_trimmed}}   ')
        Traceback (most recent call last):
            ...
        AssertionError

        In essence it divides up a tag into the end tokens, any
        leading or trailing whitespace and the inner content
        >>> Rule_L046._get_whitespace_ends('{{ my_content }}')
        ('{{', ' ', 'my_content', ' ', '}}')

        It also works with block tags and more complicated content
        and end markers.
        >>> Rule_L046._get_whitespace_ends('{%+if a + b is True     -%}')
        ('{%+', '', 'if a + b is True', '     ', '-%}')
        """
        assert s[0] == "{" and s[-1] == "}"
        # Jinja tags all have a length of two. We can use slicing
        # to remove them easily.
        main = s[2:-2]
        pre = s[:2]
        post = s[-2:]
        # Optionally Jinja tags may also have plus of minus notation
        # https://jinja2docs.readthedocs.io/en/stable/templates.html#whitespace-control
        modifier_chars = ["+", "-"]
        if main and main[0] in modifier_chars:
            main = main[1:]
            pre = s[:3]
        if main and main[-1] in modifier_chars:
            main = main[:-1]
            post = s[-3:]
        inner = main.strip()
        pos = main.find(inner)
        return pre, main[:pos], inner, main[pos + len(inner) :], post

    def _eval(self, context: RuleContext) -> EvalResultType:
        """Look for non-literal segments."""
        assert context.segment.pos_marker
        if context.segment.is_raw() and not context.segment.pos_marker.is_literal():
            if not context.memory:
                memory = set()
            else:
                memory = context.memory

            # Get any templated raw slices.
            # NOTE: We use this function because a single segment
            # may include multiple raw templated sections:
            # e.g. a single identifier with many templated tags.
            templated_raw_slices = FunctionalContext(context).segment.raw_slices.select(
                rsp.is_slice_type("templated", "block_start", "block_end")
            )
            result = []

            # Iterate through any tags found.
            for raw_slice in templated_raw_slices:
                stripped = raw_slice.raw.strip()
                if not stripped or stripped[0] != "{" or stripped[-1] != "}":
                    continue  # pragma: no cover

                self.logger.debug(
                    "Tag found @ %s: %r ", context.segment.pos_marker, stripped
                )

                # Dedupe using a memory of source indexes.
                # This is important because several positions in the
                # templated file may refer to the same position in the
                # source file and we only want to get one violation.
                src_idx = raw_slice.source_idx
                if context.memory and src_idx in context.memory:
                    continue
                memory.add(src_idx)

                # Partition and Position
                tag_pre, ws_pre, inner, ws_post, tag_post = self._get_whitespace_ends(
                    stripped
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

                if pre_fix is not None or post_fix is not None:
                    fixed = (
                        tag_pre
                        + (pre_fix or ws_pre)
                        + inner
                        + (post_fix or ws_post)
                        + tag_post
                    )
                    src_fix = [
                        SourceFix(
                            fixed,
                            slice(
                                src_idx + position,
                                src_idx + position + len(stripped),
                            ),
                            # NOTE: The templated slice here is
                            # going to be a little imprecise, but
                            # the one that really matters is the
                            # source slice.
                            context.segment.pos_marker.templated_slice,
                        )
                    ]
                    result.append(
                        LintResult(
                            memory=memory,
                            anchor=context.segment,
                            description=f"Jinja tags should have a single "
                            f"whitespace on either side: {stripped}",
                            fixes=[
                                LintFix.replace(
                                    context.segment,
                                    [context.segment.edit(source_fixes=src_fix)],
                                )
                            ],
                        )
                    )
            if result:
                return result
            else:
                return LintResult(memory=memory)
        return LintResult(memory=context.memory)

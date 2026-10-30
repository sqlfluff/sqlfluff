"""Tests for crawlers."""

from functools import partial

import pytest

from sqlfluff.core.config import FluffConfig
from sqlfluff.core.linter.linter import Linter
from sqlfluff.core.rules.context import RuleContext
from sqlfluff.core.rules.crawlers import (
    ParentOfSegmentCrawler,
    RootOnlyCrawler,
    SegmentSeekerCrawler,
)
from sqlfluff.core.templaters.base import TemplatedFile


@pytest.mark.parametrize(
    "CrawlerType,crawler_kwargs,raw_sql_in,target_raws_out",
    [
        (RootOnlyCrawler, {}, "SELECT 1 + 2", ["SELECT 1 + 2"]),
        (
            SegmentSeekerCrawler,
            {"types": {"numeric_literal"}},
            "SELECT 1 + 2",
            ["1", "2"],
        ),
        (
            ParentOfSegmentCrawler,
            {"types": {"numeric_literal"}},
            "SELECT 1 + 2",
            ["1 + 2"],
        ),
    ],
)
def test_rules_crawlers(CrawlerType, crawler_kwargs, raw_sql_in, target_raws_out):
    """Test Crawlers."""
    cfg = FluffConfig(overrides={"dialect": "ansi"})
    linter = Linter(config=cfg)
    root = linter.parse_string(raw_sql_in).tree

    root_context = RuleContext(
        dialect=cfg.get("dialect_obj"),
        fix=True,
        templated_file=TemplatedFile(raw_sql_in, "<test-case>"),
        path=None,
        segment=root,
        config=cfg,
    )

    crawler = CrawlerType(**crawler_kwargs)

    result_raws = [context.segment.raw for context in crawler.crawl(root_context)]

    assert result_raws == target_raws_out


def reference_crawl(crawler, context):
    """The straightforward recursive crawl the crawler must stay equivalent to.

    SegmentSeekerCrawler.crawl() may skip work, but not change what it yields or
    the raw stack it leaves. This one recurses into every child.
    """
    self_match = False
    if not crawler.passes_filter(context.segment):
        if crawler.provide_raw_stack:
            context.raw_stack += tuple(context.segment.raw_segments)
        return

    if crawler.is_self_match(context.segment):
        self_match = True
        yield context

    if not context.segment.segments or (self_match and not crawler.allow_recurse):
        if crawler.provide_raw_stack:
            context.raw_stack += (context.segment,)
        return

    if not crawler.types & context.segment.descendant_type_set:
        if crawler.provide_raw_stack:
            context.raw_stack += tuple(context.segment.raw_segments)
        return

    new_parent_stack = context.parent_stack + (context.segment,)
    for idx, child in enumerate(context.segment.segments):
        context.segment = child
        context.parent_stack = new_parent_stack
        context.segment_idx = idx
        yield from reference_crawl(crawler, context)


def crawl_trace(crawl, context):
    """Run a crawl, noting each yield and the raw stack at that point.

    The crawl reuses one context in place, so everything is noted as each segment
    is yielded. Segments are noted by id, as segments with the same content are
    equal. The raw stack the crawl ends with is returned too.
    """
    yielded, raw_stacks = [], []
    for ctx in crawl(context):
        yielded.append(
            (id(ctx.segment), tuple(map(id, ctx.parent_stack)), ctx.segment_idx)
        )
        raw_stacks.append(tuple(map(id, ctx.raw_stack)))
    return yielded, raw_stacks, tuple(map(id, context.raw_stack))


@pytest.mark.parametrize("provide_raw_stack", [True, False])
@pytest.mark.parametrize(
    "raw_sql_in,types,allow_recurse",
    [
        # Targets that are only ever leaves.
        ("SELECT 1 + 2 FROM t WHERE a = 3", {"numeric_literal"}, True),
        # A target with children, which can have another target inside it.
        ("SELECT (a + b) * c FROM t", {"expression"}, True),
        ("SELECT (a + b) * c FROM t", {"expression"}, False),
        # A target that isn't in the tree at all.
        ("SELECT 1 + 2 FROM t", {"case_expression"}, True),
        # Targets inside a section that doesn't parse. The crawler skips these.
        ("SELECT 1 + 2 FROM t; asd 3 qwe 4", {"numeric_literal"}, True),
    ],
)
def test_rules_crawlers_seeker_matches_reference(
    raw_sql_in, types, allow_recurse, provide_raw_stack
):
    """Test the seeker crawler against a plain recursive crawl.

    The raw stack is checked too, when the crawler is asked to build one.
    """
    cfg = FluffConfig(overrides={"dialect": "ansi"})
    linter = Linter(config=cfg)
    root = linter.parse_string(raw_sql_in).tree
    crawler = SegmentSeekerCrawler(
        types, provide_raw_stack=provide_raw_stack, allow_recurse=allow_recurse
    )

    def new_root_context():
        return RuleContext(
            dialect=cfg.get("dialect_obj"),
            fix=True,
            templated_file=TemplatedFile(raw_sql_in, "<test-case>"),
            path=None,
            segment=root,
            config=cfg,
        )

    yielded, raw_stacks, end_stack = crawl_trace(crawler.crawl, new_root_context())
    ref_yielded, ref_raw_stacks, ref_end_stack = crawl_trace(
        partial(reference_crawl, crawler), new_root_context()
    )

    assert yielded == ref_yielded
    assert raw_stacks == ref_raw_stacks
    assert end_stack == ref_end_stack

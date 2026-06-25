"""Experimental Rust-assisted target selection for CP01.

This is a proof-of-concept for "Rust-assisted" rules: instead of crawling the
Python ``BaseSegment`` tree to find the segments a rule cares about, we walk the
Rust-built node tree (``root._rs_node``) once and select the targets there, then
reuse the rule's existing per-segment logic unchanged.

For CP01 (keyword capitalisation) the only thing the crawl does is pick the
keyword / binary_operator / date_part segments (minus a few exclusions); the
casing/policy logic in ``Rule_CP01._handle_segment`` is identical regardless of
how the targets were found. So this module reproduces *just* the selection on
the Rust tree and hands the resulting Python segments back to ``_handle_segment``.

The Rust raw-leaf order corresponds 1:1 (including meta segments) to
``root.raw_segments``, so a target found at leaf index ``i`` anchors to
``root.raw_segments[i]``.

Gated/experimental: nothing imports this on the hot path yet; it exists to be
validated against stock CP01 before any wiring into rule dispatch.
"""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.parser import BaseSegment
    from sqlfluff.core.rules import LintResult, RuleContext
    from sqlfluff.core.rules.capitalisation.CP01 import Rule_CP01

# Segment types CP01 targets (mirrors its SegmentSeekerCrawler set).
_TARGET_TYPES = frozenset({"keyword", "binary_operator", "date_part"})
# Mirror Rule_CP01._exclude_types / _exclude_parent_types.
_EXCLUDE_TYPES = frozenset({"literal"})
_EXCLUDE_PARENT_TYPES = frozenset(
    {"data_type", "datetime_type_identifier", "primitive_type"}
)


def cp01_targets_via_rs_node(
    root: "BaseSegment",
) -> Optional[list["BaseSegment"]]:
    """Select CP01's target segments by walking ``root._rs_node``.

    Returns the Python ``raw_segments`` CP01 would visit, in document order, or
    ``None`` if no Rust node tree is available (caller should fall back to the
    normal crawl).
    """
    rs_node = getattr(root, "_rs_node", None)
    if rs_node is None:
        return None

    raw_segments = root.raw_segments
    targets: list[BaseSegment] = []
    # Leaf index into raw_segments, advanced for every rs leaf (raw + meta).
    idx = 0

    def _is_target(node: object, parent: Optional[object]) -> bool:
        class_types = frozenset(node.class_types() or ())
        if not (_TARGET_TYPES & class_types):
            return False
        if _EXCLUDE_TYPES & class_types:
            return False
        if parent is not None:
            parent_class_types = frozenset(parent.class_types() or ())
            if _EXCLUDE_PARENT_TYPES & parent_class_types:
                return False
            # Qualified function names (e.g. UDFs) are case-sensitive: skip a
            # keyword whose parent is a multi-part function_name.
            parent_children = parent.children() or []
            if parent.segment_type == "function_name" and len(parent_children) != 1:
                # Defensive: a keyword/operator that is a part of a qualified
                # function name does not occur in normal SQL, but mirror CP01.
                return False  # pragma: no cover
        return True

    def _walk(node: object, parent: Optional[object]) -> None:
        nonlocal idx
        children = node.children()
        if children is None:
            # A leaf node consumes exactly one raw_segments slot.
            segment = raw_segments[idx]
            idx += 1
            if _is_target(node, parent):
                targets.append(segment)
            return
        for child in children:
            _walk(child, node)

    _walk(rs_node, None)
    return targets


def cp01_results_via_rs_node(
    rule: "Rule_CP01",
    root: "BaseSegment",
    context: "RuleContext",
) -> Optional[list["LintResult"]]:
    """Produce CP01's LintResults using Rust-assisted target selection.

    Targets are picked from the Rust node tree; the actual casing decision and
    fix are produced by the rule's existing ``_handle_segment`` (so the policy
    logic is shared verbatim). Memory is threaded between targets exactly as the
    crawler would. Returns ``None`` if no Rust node tree is available.
    """
    import copy

    targets = cp01_targets_via_rs_node(root)
    if targets is None:
        return None

    results: list[LintResult] = []
    memory: dict = {}
    for segment in targets:
        seg_context = copy.copy(context)
        seg_context.segment = segment
        seg_context.memory = memory
        result = rule._handle_segment(segment, seg_context)
        memory = result.memory
        results.append(result)
    return results


def cp01_results_via_rust(
    rule: "Rule_CP01",
    root: "BaseSegment",
    context: "RuleContext",
) -> Optional[list["LintResult"]]:
    """Produce CP01's LintResults by running detection natively in Rust.

    The whole detection loop (target selection, exclusions, consistent-policy
    inference, casing) runs in Rust via ``RsNode.cp01_violations`` and returns
    ``(leaf_index, fixed_raw)`` pairs in a single FFI crossing. Python only maps
    each leaf index to its ``raw_segment`` and emits a standard ``LintFix``.

    Returns ``None`` (caller falls back) when there's no Rust node tree or the
    config uses features the native path doesn't implement yet
    (``ignore_words_regex`` or non-keyword policies).
    """
    from sqlfluff.core.rules import LintResult

    rs_node = getattr(root, "_rs_node", None)
    if rs_node is None:
        return None

    policy = str(getattr(rule, "capitalisation_policy", "consistent"))
    if policy not in ("consistent", "upper", "lower", "capitalise"):
        return None
    # The native path doesn't implement regex word-ignore yet.
    if getattr(rule, "ignore_words_regex", None):
        return None

    ignore_words_config = str(getattr(rule, "ignore_words", None))
    if ignore_words_config and ignore_words_config != "None":
        ignore_words = rule.split_comma_separated_string(ignore_words_config.lower())
    else:
        ignore_words = []
    ignore_templated = bool(context.config.get("ignore_templated_areas"))

    violations = rs_node.cp01_violations(policy, ignore_words, ignore_templated)
    if not violations:
        return []

    raw_segments = root.raw_segments
    results: list[LintResult] = []
    for leaf_idx, fixed_raw in violations:
        segment = raw_segments[leaf_idx]
        results.append(
            LintResult(
                anchor=segment,
                fixes=[rule._get_fix(segment, fixed_raw)],
                description=f"{rule._description_elem} must be consistent.",
            )
        )
    return results

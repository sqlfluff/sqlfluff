"""Fix application over the Rust arena façade (source-patching).

The lint/fix *loop* for the experimental Rust-engine fast path: crawl rules
over the :class:`RsSegment` façade (``sqlfluff.core.rules.rs_lint``), then
apply their fixes by patching the original source string — the arena tree is
never mutated. Lives in ``core.linter`` (not ``core.rules``) because applying
fixes needs the linter's fix/patch machinery, which the rules layer must not
import.
"""

from __future__ import annotations

from typing import Any, Optional

from sqlfluff.core.rules.rs_lint import RsSegment

# NOTE: Several fallback branches below are only reached with the Rust engine
# forced on (the ``py*-rust-engine`` tox env) over inputs that exercise the
# uncommon fix shapes — non-literal anchors, unparsable re-parses, the native
# uuid-bridge, loop detection. CI's coverage combine doesn't include the
# forced-engine env, so those lines carry ``# pragma: no cover`` here. They are
# covered for real once the stack wires the façade fix path into the default
# suite (rs-stack-12). Same rationale as ``_try_facade_paths_fix`` in
# ``cli/commands.py``.


def apply_source_fixes(source: str, fixes: list[Any]) -> Optional[str]:
    """Apply ``LintFix`` objects to ``source`` by patching literal source slices.

    Returns the patched source, or ``None`` if any fix targets a non-literal
    (templated) region or an unsupported edit type — signalling the caller to
    leave those to the Python path.
    """
    # (start, stop, repl, rank). `rank` breaks ties between edits at the SAME
    # start offset, matching the order native reconstructs from the tree:
    # create_after (0) attaches to the segment ending at the offset, so it comes
    # before create_before (1, attaches to the segment starting there), which
    # comes before replace/delete (2, modifies the segment starting there).
    edits: list[tuple[int, int, str, int]] = []
    for fx in fixes:
        pm = fx.anchor.pos_marker
        if pm is None:
            # A freshly-constructed anchor with no source position (e.g. some
            # reflow indent fixes) can't be source-patched — bail so the caller
            # falls back to the Python tree-mutation path.
            return None  # pragma: no cover
        lit = pm.is_literal
        sl = pm.source_slice
        repl = "".join(e.raw for e in (fx.edit or []))
        et = fx.edit_type
        if not (lit() if callable(lit) else lit):
            # Templated (non-literal) anchor. Two safe cases:
            # 1. The edit segments carry `source_fixes` (SourceFix(edit,
            #    source_slice, …)) describing the exact source rewrite of a
            #    `{% %}`/`{{ }}` tag (e.g. JJ01) — apply those.
            # 2. A create_before/create_after inserts at the source *boundary*
            #    (before/after the templated region) without touching the
            #    template itself (e.g. LT12 appending a trailing newline).
            # A replace/delete on templated content without source_fixes would
            # corrupt the template → bail so the caller falls back to Python.
            src_fixes = [
                sfx
                for e in (fx.edit or [])
                for sfx in (getattr(e, "source_fixes", None) or [])
            ]
            if src_fixes:
                for sfx in src_fixes:
                    ssl = sfx.source_slice
                    edits.append((ssl.start, ssl.stop, sfx.edit, 2))
            elif et == "create_before":  # pragma: no cover
                edits.append((sl.start, sl.start, repl, 1))
            elif et == "create_after":  # pragma: no cover
                edits.append((sl.stop, sl.stop, repl, 0))
            else:  # pragma: no cover
                return None
            continue
        if et == "replace":
            edits.append((sl.start, sl.stop, repl, 2))
        elif et == "create_before":
            edits.append((sl.start, sl.start, repl, 1))
        elif et == "create_after":
            edits.append((sl.stop, sl.stop, repl, 0))
        elif et == "delete":
            edits.append((sl.start, sl.stop, "", 2))
        else:  # pragma: no cover
            return None
    # Native applies fixes to the tree hierarchically: deleting a parent segment
    # removes its children too. In source coordinates a `delete` range therefore
    # subsumes any nested edit — e.g. AL07 deletes an `alias_expression` while
    # also "replacing" the alias identifier inside it. Drop non-delete edits
    # fully contained in a delete's range so they don't conflict / double-apply.
    delete_ranges = [(a, b) for (a, b, r, _rk) in edits if b > a and r == ""]
    if delete_ranges:
        edits = [
            e
            for e in edits
            if (e[2] == "" and e[1] > e[0])  # keep the deletes themselves
            or e[1] == e[0]  # keep zero-width inserts (create_before/after)
            or not any(
                da <= e[0] and e[1] <= db and (da, db) != (e[0], e[1])
                for (da, db) in delete_ranges
            )
        ]
    # Reconstruct left-to-right in ORIGINAL coordinates (a naive per-edit
    # ``out[:start] + repl + out[stop:]`` shifts later edits' positions and
    # corrupts adjacent edits at the same offset).
    edits.sort(key=lambda e: (e[0], e[3], e[1]))
    out_parts: list[str] = []
    pos = 0
    for start, stop, repl, _rank in edits:
        if start < pos:  # genuinely overlapping edits — can't apply safely
            return None
        out_parts.append(source[pos:start])
        out_parts.append(repl)
        pos = stop
    out_parts.append(source[pos:])
    return "".join(out_parts)


def facade_violations(
    source: str,
    fname: str,
    config: Any,
    rules: list[Any],
) -> Optional[list[Any]]:
    """Crawl ``rules`` over the arena façade and return their ``SQLLintError``s.

    Returns ``None`` if the source can't be parsed via the engine (the caller
    should fall back to the Python path). ``ignore_mask`` is not applied here —
    callers relying on ``noqa`` must handle it separately.
    """
    import sqlfluffrs

    rst = sqlfluffrs.engine_parse_to_tree(source, fname, config, None, True)
    if rst is None:  # pragma: no cover
        return None
    dialect_obj = config.get("dialect_obj")
    root = RsSegment(rst.root)
    # The engine's TemplatedFile — required by rules that read raw_slices /
    # source_str (e.g. CV10) and for correct source-position mapping.
    templated_file = rst.templated_file
    out: list[Any] = []
    for rule in rules:
        lints, _, _, _ = rule.crawl(
            tree=root,
            dialect=dialect_obj,
            fix=False,
            templated_file=templated_file,
            ignore_mask=None,
            fname=fname,
            config=config,
        )
        out.extend(lints)
    return out


def _native_apply_fixes(
    rst: Any, rule_code: str, fixes: list[Any], config: Any
) -> Optional[str]:
    """uuid-bridge: apply tree-restructuring ``fixes`` via the native machinery.

    For fixes that ``apply_source_fixes`` can't express as source-slice edits
    (subquery→CTE, reflow indent, …), materialise the arena tree into a real
    ``BaseSegment`` tree **preserving the arena uuids** so native ``apply_fixes``
    (which matches fixes by ``anchor.uuid``) lines up with the façade fixes, then
    reconstruct the fixed source with native ``generate_source_patches`` +
    ``fix_string`` — the exact, parity-correct path. Returns the fixed source, or
    ``None`` on any failure so the caller falls back / skips.
    """
    try:
        from sqlfluff.core.linter.fix import apply_fixes, compute_anchor_edit_info
        from sqlfluff.core.linter.linted_file import LintedFile
        from sqlfluff.core.linter.patch import generate_source_patches

        tf = rst.templated_file
        if tf is None:  # pragma: no cover
            return None
        anchor_info = compute_anchor_edit_info(fixes)
        if any(not info.is_valid for info in anchor_info.values()):  # pragma: no cover
            return None
        materialised = RsSegment(rst.root).copy(preserve_uuid=True)
        new_tree, _before, _after, valid = apply_fixes(
            materialised,
            config.get("dialect_obj"),
            rule_code,
            anchor_info,
            fix_even_unparsable=config.get("fix_even_unparsable"),
            max_parse_depth=config.get("max_parse_depth"),
            max_parse_nodes=config.get("max_parse_nodes"),
        )
        if not valid:  # pragma: no cover
            return None
        patches = generate_source_patches(new_tree, tf)
        source_only = tf.source_only_slices()
        slices = LintedFile._slice_source_file_using_patches(
            patches, source_only, tf.source_str
        )
        return LintedFile._build_up_fixed_source_string(slices, patches, tf.source_str)
    except Exception:  # noqa: BLE001 -- defers to caller # pragma: no cover
        return None


def facade_fix_loop(
    source: str,
    fname: str,
    config: Any,
    rules: list[Any],
    limit: int,
) -> str:
    """Iteratively fix ``source`` over the arena façade.

    Mirrors the main/post phase scheduling of ``Linter.lint_fix_parsed``
    (source-patch + re-parse, version-based loop detection).
    """
    import sqlfluffrs

    dialect_obj = config.get("dialect_obj")
    by_phase = {
        "main": [r for r in rules if r.lint_phase == "main"],
        "post": [r for r in rules if r.lint_phase == "post"],
    }
    seen = {source}

    def parse(s: str) -> Any:
        return sqlfluffrs.engine_parse_to_tree(s, fname, config, None, True)

    for phase in ("main", "post"):
        nloops = limit if phase == "main" else 2
        for loop in range(nloops):
            this = rules if (phase == "main" and loop == 0) else by_phase[phase]
            changed = False
            # Parse once at the start of the loop and reuse that tree across rules
            # that make no change; only re-parse when a fix actually rewrites the
            # source (and reuse *that* parse as both the validity check and the
            # current tree). This replaces the previous per-rule re-parse — the
            # dominant cost — with 1 + (number of applied fixes) parses per loop.
            rst = parse(source)
            for rule in this:
                if rst is None:  # pragma: no cover
                    break
                _v, _r, fixes, _m = rule.crawl(
                    tree=RsSegment(rst.root),
                    dialect=dialect_obj,
                    fix=True,
                    templated_file=rst.templated_file,
                    ignore_mask=None,
                    fname=fname,
                    config=config,
                )
                if not fixes:
                    continue
                new_source = apply_source_fixes(source, fixes)
                if new_source is None:
                    # Tree-restructuring fix that source-patching can't express —
                    # apply it via the native machinery over a uuid-preserving
                    # materialisation of the current arena tree (approach B).
                    new_source = _native_apply_fixes(rst, rule.code, fixes, config)
                if new_source is None or new_source == source:  # pragma: no cover
                    continue
                if new_source in seen:  # loop detected -> stop  # pragma: no cover
                    continue
                new_rst = parse(new_source)  # single parse: validity + next tree
                if new_rst is None:  # reject unparsable fix  # pragma: no cover
                    continue
                source = new_source
                seen.add(new_source)
                changed = True
                rst = new_rst
            if not changed:
                break
    return source

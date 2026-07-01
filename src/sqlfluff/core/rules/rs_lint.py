"""Experimental: lint & fix over the Rust parse arena via an ``RsSegment`` façade.

The Rust-driven engine parses to an arena and hands Python an ``RsTree``
(``sqlfluffrs.engine_parse_to_tree``). :class:`RsSegment` is a ``BaseSegment``
duck-type backed by the arena's ``RsHandle`` cursor, so the existing Python
rules can crawl the Rust tree directly — no Python ``BaseSegment`` tree is built.

Fixes are applied by **source-slice patching + re-parse** rather than mutating a
tree, so this works today without arena mutation. :func:`facade_fix_loop` mirrors
``Linter.lint_fix_parsed``'s main/post phase scheduling.

This covers the rules whose ``BaseSegment`` API surface the façade implements
(see :data:`FACADE_SAFE_RULES`); other rules should stay on the Python path.
Detection and fixing match native SQLFluff for the covered rules.
"""
# The RsSegment accessors are trivial one-line delegations to the arena handle
# that mirror the documented BaseSegment interface; per-method docstrings would
# be pure noise, so D102 is disabled for this façade module.
# ruff: noqa: D102

from __future__ import annotations

from typing import Any, Iterator, Optional

# Rules verified to lint AND fix correctly over the façade — i.e. the façade's
# multi-pass source-patch fix output is byte-identical to native SQLFluff across
# every case in that rule's ``std_rule_cases`` fixture. Rules whose fixes are
# structural (alias add/remove, etc., where source-patching diverges from
# native's tree rebuild) or need façade accessors not yet implemented are
# excluded and should stay on the Python ``BaseSegment`` path.
FACADE_SAFE_RULES: frozenset[str] = frozenset(
    {
        "AL03",
        "AL04",
        "AL06",
        "AL08",
        "AL09",
        "AL10",
        "AM01",
        "AM02",
        "AM03",
        "AM05",
        "AM06",
        "AM08",
        "AM09",
        "CP01",
        "CP02",
        "CP03",
        "CP04",
        "CP05",
        "CV01",
        "CV02",
        "CV04",
        "CV05",
        "CV08",
        "CV09",
        "LT06",
        "LT11",
        "LT15",
        "OR01",
        "PG01",
        "RF02",
        "RF04",
        "RF06",
        "ST01",
        "ST03",
        "TQ01",
        "TQ02",
        "TQ03",
    }
)


def _typename(t: Any) -> str:
    """Coerce a ``get_child`` arg (type-name string or segment class) to a name."""
    if isinstance(t, str):
        return t
    return getattr(t, "type", None) or getattr(t, "_surrogate_type", None) or str(t)


class RsSegment:
    """A ``BaseSegment`` duck-type backed by an arena ``RsHandle``.

    Every accessor delegates to the (Rust) handle; navigation returns fresh
    ``RsSegment`` wrappers. Read-only: ``edit`` returns a real Python
    ``RawSegment`` for fix construction, but the arena itself is never mutated.
    """

    __slots__ = ("_h", "_segments")

    def __init__(self, handle: Any) -> None:
        self._h = handle
        self._segments: Optional[tuple[RsSegment, ...]] = None

    # -- identity ------------------------------------------------------------
    def __eq__(self, other: object) -> bool:
        return isinstance(other, RsSegment) and self._h == other._h

    def __hash__(self) -> int:
        return hash(self._h)

    @property
    def uuid(self) -> int:
        return self._h.uuid

    # -- payload -------------------------------------------------------------
    @property
    def raw(self) -> str:
        return self._h.raw

    @property
    def raw_upper(self) -> str:
        return self._h.raw_upper

    @property
    def type(self) -> str:
        return self._h.type

    def get_type(self) -> str:
        return self._h.type

    def is_type(self, *seg_type: str) -> bool:
        return self._h.is_type(list(seg_type))

    @property
    def class_types(self) -> frozenset[str]:
        return frozenset(self._h.class_types())

    @property
    def instance_types(self) -> tuple[str, ...]:
        return tuple(self._h.instance_types())

    @property
    def descendant_type_set(self) -> frozenset[str]:
        return frozenset(self._h.descendant_type_set())

    @property
    def is_code(self) -> bool:
        return self._h.is_code

    @property
    def is_meta(self) -> bool:
        return self._h.is_meta

    @property
    def is_whitespace(self) -> bool:
        return self._h.is_whitespace

    @property
    def is_comment(self) -> bool:
        return self._h.is_comment

    def is_raw(self) -> bool:
        return self._h.is_raw()

    @property
    def is_templated(self) -> bool:
        return self._h.is_templated

    @property
    def indent_val(self) -> int:
        t = self._h.type
        return 1 if t == "indent" else (-1 if t == "dedent" else 0)

    @property
    def is_implicit(self) -> bool:
        return bool(self._h.is_implicit())

    @property
    def pos_marker(self) -> Any:
        return self._h.pos_marker

    def get_start_loc(self) -> tuple[int, int]:
        return self._h.pos_marker.working_loc

    def get_end_loc(self) -> tuple[int, int]:
        pm = self._h.pos_marker
        return pm.working_loc_after(self._h.raw)

    # -- navigation ----------------------------------------------------------
    @property
    def segments(self) -> tuple[RsSegment, ...]:
        if self._segments is None:
            self._segments = tuple(RsSegment(c) for c in self._h.children)
        return self._segments

    @property
    def raw_segments(self) -> list[RsSegment]:
        return [RsSegment(x) for x in self._h.raw_segments()]

    def get_raw_segments(self) -> list[RsSegment]:
        return self.raw_segments

    @property
    def raw_segments_with_ancestors(
        self,
    ) -> list[tuple[RsSegment, list[Any]]]:
        out: list[tuple[RsSegment, list[Any]]] = []
        for leaf_h in self._h.raw_segments():
            leaf = RsSegment(leaf_h)
            out.append((leaf, self.path_to(leaf)))
        return out

    def get_parent(self) -> Optional[tuple[RsSegment, int]]:
        gp = self._h.get_parent()
        return (RsSegment(gp[0]), gp[1]) if gp else None

    def get_child(self, *seg_type: Any) -> Optional[RsSegment]:
        r = self._h.get_child([_typename(t) for t in seg_type])
        return RsSegment(r) if r is not None else None

    def get_children(self, *seg_type: Any) -> list[RsSegment]:
        return [
            RsSegment(x) for x in self._h.get_children([_typename(t) for t in seg_type])
        ]

    def path_to(self, other: "RsSegment") -> list[Any]:
        from sqlfluff.core.parser.segments.base import PathStep

        return [
            PathStep(RsSegment(h), idx, ln, tuple(cidx))  # type: ignore[arg-type]
            for (h, idx, ln, cidx) in self._h.path_to(other._h)
        ]

    def recursive_crawl(
        self,
        *seg_type: str,
        recurse_into: bool = True,
        no_recursive_seg_type: Any = None,
        allow_self: bool = True,
    ) -> list[RsSegment]:
        if isinstance(no_recursive_seg_type, str):
            nr = [no_recursive_seg_type]
        else:
            nr = list(no_recursive_seg_type) if no_recursive_seg_type else []
        return [
            RsSegment(x)
            for x in self._h.recursive_crawl(
                list(seg_type), recurse_into, nr, allow_self
            )
        ]

    def recursive_crawl_all(self, reverse: bool = False) -> list[RsSegment]:
        segs = [RsSegment(x) for x in self._h.recursive_crawl_all()]
        return list(reversed(segs)) if reverse else segs

    def iter_segments(
        self, expanding: Any = None, pass_through: bool = False
    ) -> Iterator["RsSegment"]:
        # Minimal: yield direct children (no meta-expansion), sufficient for the
        # rules currently covered.
        return iter(self.segments)

    # -- fix support ---------------------------------------------------------
    def edit(self, raw: Optional[str] = None, source_fixes: Any = None) -> Any:
        """Return a real ``RawSegment`` for a fix's replacement text.

        The arena is not mutated; the returned segment only carries the new raw
        + this node's position, which is all the source-patch fixer needs.
        """
        from sqlfluff.core.parser import RawSegment

        return RawSegment(raw=raw, pos_marker=self.pos_marker)

    def __getattr__(self, name: str) -> Any:
        # Only fires for BaseSegment API the façade doesn't implement yet. Raising
        # keeps behaviour honest — such rules aren't in FACADE_SAFE_RULES.
        raise AttributeError(
            f"RsSegment (arena façade) does not implement {name!r}; "
            "this rule is not façade-safe yet."
        )

    def __repr__(self) -> str:
        return f"RsSegment({self._h!r})"


def apply_source_fixes(source: str, fixes: list[Any]) -> Optional[str]:
    """Apply ``LintFix`` objects to ``source`` by patching literal source slices.

    Returns the patched source, or ``None`` if any fix targets a non-literal
    (templated) region or an unsupported edit type — signalling the caller to
    leave those to the Python path.
    """
    edits: list[tuple[int, int, str]] = []
    for fx in fixes:
        pm = fx.anchor.pos_marker
        lit = pm.is_literal
        if not (lit() if callable(lit) else lit):
            return None
        sl = pm.source_slice
        repl = "".join(e.raw for e in (fx.edit or []))
        et = fx.edit_type
        if et == "replace":
            edits.append((sl.start, sl.stop, repl))
        elif et == "create_before":
            edits.append((sl.start, sl.start, repl))
        elif et == "create_after":
            edits.append((sl.stop, sl.stop, repl))
        elif et == "delete":
            edits.append((sl.start, sl.stop, ""))
        else:
            return None
    out = source
    for start, stop, repl in sorted(edits, key=lambda t: t[0], reverse=True):
        out = out[:start] + repl + out[stop:]
    return out


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
            for rule in this:
                rst = parse(source)
                if rst is None:
                    continue
                _v, _r, fixes, _m = rule.crawl(
                    tree=RsSegment(rst.root),
                    dialect=dialect_obj,
                    fix=True,
                    templated_file=None,
                    ignore_mask=None,
                    fname=fname,
                    config=config,
                )
                if not fixes:
                    continue
                new_source = apply_source_fixes(source, fixes)
                if new_source is None or new_source == source:
                    continue
                if parse(new_source) is None:  # reject unparsable fix (~ _valid)
                    continue
                if new_source in seen:  # loop detected -> stop applying
                    continue
                source = new_source
                seen.add(new_source)
                changed = True
            if not changed:
                break
    return source

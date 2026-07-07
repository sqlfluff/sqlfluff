"""Experimental: lint & fix over the Rust parse arena via an ``RsSegment`` façade.

The Rust-driven engine parses to an arena and hands Python an ``RsTree``
(``sqlfluffrs.engine_parse_to_tree``). :class:`RsSegment` is a ``BaseSegment``
duck-type backed by the arena's ``RsHandle`` cursor, so the existing Python
rules can crawl the Rust tree directly — no Python ``BaseSegment`` tree is built.

Fixes are applied by **source-slice patching + re-parse** rather than mutating a
tree, so this works today without arena mutation — see
``sqlfluff.core.linter.rs_fix`` (the loop lives in the linter layer because
applying fixes needs the linter's fix/patch machinery).

This covers the rules whose ``BaseSegment`` API surface the façade implements
(see :data:`FACADE_SAFE_RULES`); other rules should stay on the Python path.
Detection and fixing match native SQLFluff for the covered rules.
"""
# The RsSegment accessors are trivial one-line delegations to the arena handle
# that mirror the documented BaseSegment interface; per-method docstrings would
# be pure noise, so D102 is disabled for this façade module.
# ruff: noqa: D102

from __future__ import annotations

import re
import weakref
from typing import TYPE_CHECKING, Any, Iterator, Optional, Union, cast

if TYPE_CHECKING:
    from sqlfluffrs import RsHandle

# Interning cache so the same arena node always yields the same RsSegment object.
# Keyed by node uuid (a globally-unique monotonic counter), held weakly so
# wrappers are freed once no longer referenced. This makes identity (`x is y`)
# comparisons — used across the rule engine — behave like they do on native
# BaseSegment instances, without which navigation returns a fresh wrapper each
# time and `is` never matches (causing e.g. infinite recursion in alias analysis).
_INTERN: "weakref.WeakValueDictionary[int, RsSegment]" = weakref.WeakValueDictionary()

# Rules whose façade FIX output is byte-identical to native SQLFluff. Vetted
# both per-rule across ``std_rule_cases`` AND — crucially — by the COMBINED
# multi-rule fix over the whole ``test/fixtures/dialects/*`` corpus under each
# fixture's CORRECT dialect (running everything as ``ansi`` produces unparsable
# regions and spurious divergences that are pure harness artifacts). A rule is
# only listed if adding it introduces zero new whole-corpus divergences over the
# rest of the set. This is a *fix-output* guarantee, used by the self-guarding
# stdin/path-fix fast path (which re-checks that no violations remain).
#
# NOTE: it is NOT a detection/lint guarantee — some rules over-report violations
# over the façade (safe for the fix guard, wrong for lint), e.g. CP01
# double-reports the sparksql ``div`` operator. Wiring `lint` needs the
# detection-verified subset (this set minus the DETECTION_UNSAFE members below,
# plus rules using ``isinstance`` on concrete classes a duck-type can't satisfy).
#
# RF06 was DROPPED from this set: it strips backtick quotes from
# mysql/mariadb/tsql stored-procedure/function *names* that native LEAVES quoted.
# Native reports the violation but its ``apply_fixes`` rejects the fix — unquoting
# ``\`name\``` reparses as ``function_name_identifier`` not the ``naked_identifier``
# the fix specifies, so ``validate_segment_with_reparse`` fails. The façade's
# source-patch path skips that grammar validation (arena/materialised segments have
# no ``match_grammar``), so it applies a fix native won't. Faithfully replicating
# the validation needs full real-dialect-class materialisation (real leaves too),
# which defeats the façade; deferring RF06 to the Python path is the safe fix.
#
# TQ02 was also DROPPED, for a *different* reason — a reparse-vs-mutate fixed-point
# divergence, not a validation gap. On a tsql procedure body its fix reorders
# BEGIN / SET NOCOUNT; native's apply_fixes re-fires it on the MUTATED tree every
# pass (never stabilises) → hits runaway_limit → reverts to the ORIGINAL. The
# façade re-crawls the REPARSED source, where the fix does NOT re-fire → it
# stabilises after one pass and keeps the reorder. The façade reaches a stable
# fixed point native's mutate-loop can't; matching native's give-up would require
# running native's mutate-loop (defeating the façade). Loop-hardening can't help
# (the façade stabilises); deferring TQ02 to Python is the safe fix.
FACADE_SAFE_RULES_DETECTION_UNSAFE: frozenset[str] = frozenset(
    {"AL04", "AL10", "CP01", "CV09", "RF02", "ST03"}
)
FACADE_SAFE_RULES: frozenset[str] = frozenset(
    {
        "AL01",
        "AL02",
        "AL03",
        "AL04",
        "AL06",
        "AL07",
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
        "CV03",
        "CV04",
        "CV05",
        "CV07",
        "CV08",
        "CV09",
        "CV10",
        "CV11",
        "CV12",
        "JJ01",
        "LT06",
        "LT11",
        "LT15",
        "OR01",
        "PG01",
        "RF02",
        "RF04",
        "ST01",
        "ST03",
        "ST04",
        "ST06",
        "ST07",
        "ST08",
        "ST09",
        "TQ01",
        "TQ03",
    }
)


def _typename(t: Any) -> str:
    """Coerce a ``get_child`` arg (type-name string or segment class) to a name."""
    if isinstance(t, str):
        return t
    return getattr(t, "type", None) or getattr(t, "_surrogate_type", None) or str(t)


# Cache of synthetic segment classes used by ``RsSegment.copy`` to materialise a
# real Python ``BaseSegment`` tree from an arena subtree. Keyed by
# (class-name, type, class_types, is_raw) so identical arena nodes reuse the same
# class. We build synthetic classes (rather than resolving the concrete dialect
# class) because ``RsSegment`` holds no dialect reference; setting ``_class_types``
# directly guarantees ``is_type``/``class_types`` parity with the façade node
# without needing the dialect registry.
_SYNTH_CLASSES: dict[tuple[str, str, frozenset[str], bool], type] = {}


def _synth_segment_class(
    name: str, seg_type: str, class_types: frozenset[str], is_raw: bool
) -> type:
    """Return (cached) a real segment class reporting the given type/class_types."""
    from sqlfluff.core.parser import RawSegment
    from sqlfluff.core.parser.segments.base import BaseSegment

    if not name:
        # Meta/whitespace/newline tokens carry no class name in the arena;
        # derive a stable one from the type so `type()` gets a valid str.
        name = "".join(p.capitalize() for p in seg_type.split("_")) + "Segment"
    key = (name, seg_type, class_types, is_raw)
    cls = _SYNTH_CLASSES.get(key)
    if cls is None:
        base = RawSegment if is_raw else BaseSegment
        # The SegmentMetaclass recomputes ``_class_types`` from the base hierarchy
        # on class creation, so we override it *after* creation to force an exact
        # match with the arena node's class_types.
        # Include the handful of *dialect* segment methods that rules call on
        # copied segments (which are these synthetic classes, not the concrete
        # dialect class): CTEDefinitionSegment.get_identifier (used by ST05 on a
        # cloned CTE). These are navigation-only so they work on any real segment.
        cls = type(
            name,
            (base,),
            {"type": seg_type, "get_identifier": _synth_get_identifier},
        )
        cls._class_types = class_types  # type: ignore[attr-defined]
        _SYNTH_CLASSES[key] = cls
    return cls


def _synth_get_identifier(self: Any) -> Any:
    """Port of CTEDefinitionSegment.get_identifier for materialised copies."""
    return self.get_child("identifier")


class RsSegment:
    """A ``BaseSegment`` duck-type backed by an arena ``RsHandle``.

    Every accessor delegates to the (Rust) handle; navigation returns fresh
    ``RsSegment`` wrappers. Read-only: ``edit`` returns a real Python
    ``RawSegment`` for fix construction, but the arena itself is never mutated.
    """

    # `_uid` caches the node uuid (fetched once for interning) so __hash__/uuid
    # avoid an FFI call; `_ct` caches class_types (an interned wrapper is stable,
    # so the arena node's type set never changes under it) so is_type/class_types
    # become Python set operations instead of per-call FFI — the hot path in
    # rule crawling.
    __slots__ = ("_h", "_uid", "_segments", "_ct", "_rwa", "__weakref__")
    _h: "RsHandle"
    _uid: int
    _segments: Optional[tuple["RsSegment", ...]]
    _ct: Optional[frozenset[str]]
    _rwa: Optional[list[tuple["RsSegment", list[Any]]]]

    def __new__(cls, handle: Any) -> "RsSegment":
        # Intern by node uuid so the same node returns the same object (identity
        # stability). Field init happens here, not __init__, because __init__
        # still runs when __new__ returns a cached instance.
        uid = handle.uuid
        obj = _INTERN.get(uid)
        if obj is None:
            obj = object.__new__(cls)
            obj._h = handle
            obj._uid = uid
            obj._segments = None
            obj._ct = None
            obj._rwa = None
            _INTERN[uid] = obj
        return obj

    # No __init__: all state is set in __new__. Defining a no-op __init__ would
    # add a Python-frame dispatch to every wrapper creation (the hot path); with
    # __new__ overridden and no __init__, object.__init__ ignores the argument.

    # -- identity ------------------------------------------------------------
    def __eq__(self, other: object) -> bool:
        # Interning makes same-node wrappers identical; uuid compare covers the
        # rare case where a wrapper was GC'd and re-created for the same node.
        return self is other or (
            isinstance(other, RsSegment) and self._uid == other._uid
        )

    def __hash__(self) -> int:
        return self._uid

    @property
    def uuid(self) -> int:
        return self._uid

    # -- payload -------------------------------------------------------------
    @property
    def raw(self) -> str:
        return self._h.raw

    @property
    def raw_upper(self) -> str:
        return self._h.raw_upper

    @property
    def block_type(self) -> Optional[str]:
        # A ``TemplateSegment`` (placeholder) attribute; ``None`` otherwise.
        return self._h.block_type()

    @property
    def block_uuid(self) -> Optional[int]:
        # A ``TemplateSegment`` (placeholder) attribute used by reflow reindent
        # to group template-block indents.  Native stores a ``uuid.UUID``; the
        # arena exposes it as an int (hashable + truthy), ``None`` otherwise.
        return self._h.block_uuid()

    def normalize(self, value: Optional[str] = None) -> str:
        # Mirrors ``RawSegment.normalize`` (parser/segments/raw.py): quote-strip
        # via ``quoted_value`` then apply ``escape_replacements``.
        raw_buff = value or self._h.raw
        qv = self._h.quoted_value()
        if qv:
            _match = re.match(qv[0], raw_buff)
            if _match:
                group: Union[str, int] = qv[1]
                # The arena stores the capture group as a string; a numeric
                # index arrives as e.g. ``"1"`` and must be int for ``group``.
                try:
                    group = int(group)
                except (TypeError, ValueError):
                    pass
                _group_match = _match.group(group)
                if isinstance(_group_match, str):
                    raw_buff = _group_match
        for old, new in self._h.escape_replacements() or []:
            raw_buff = re.sub(old, new, raw_buff)
        return raw_buff

    def raw_normalized(self, casefold: bool = True) -> str:
        # Raw node: normalize then apply the dialect fold (``RawSegment``).
        # Container: join children (mirrors ``BaseSegment.raw_normalized``).
        if self._h.is_raw():
            raw_buff = self.normalize()
            fold = self._h.casefold()
            if fold and casefold:
                if fold == "upper":
                    raw_buff = raw_buff.upper()
                elif fold == "lower":
                    raw_buff = raw_buff.lower()
            return raw_buff
        return "".join(s.raw_normalized(casefold) for s in self.get_raw_segments())

    def raw_trimmed(self) -> str:
        # Mirrors ``RawSegment.raw_trimmed``: strip ``trim_start`` prefixes,
        # then ``trim_chars`` from both ends.
        raw_buff = self._h.raw
        trim_start = self._h.trim_start()
        if trim_start:
            for seq in trim_start:
                if raw_buff.startswith(seq):
                    raw_buff = raw_buff[len(seq) :]
        trim_chars = self._h.trim_chars()
        if trim_chars:
            raw_buff = self._h.raw
            for seq in trim_chars:
                while raw_buff.startswith(seq):
                    raw_buff = raw_buff[len(seq) :]
                while raw_buff.endswith(seq):
                    raw_buff = raw_buff[: -len(seq)]
            return raw_buff
        return raw_buff

    @property
    def type(self) -> str:
        # Native `BaseSegment.type` is the concrete class's `type` attribute
        # (the class-level type), NOT the instance override.  `get_type()` below
        # returns the instance type (`self._h.type`).
        return self._h.class_type()

    def get_type(self) -> str:
        return self._h.type

    def is_type(self, *seg_type: str) -> bool:
        # Membership in cached class_types — verified equivalent to the arena's
        # is_type (class_types already includes the structural hierarchy).
        ct = self._ct
        if ct is None:
            ct = self._ct = frozenset(self._h.class_types())
        if len(seg_type) == 1:  # hot path — most callers pass one type
            return seg_type[0] in ct
        return not ct.isdisjoint(seg_type)

    @property
    def class_types(self) -> frozenset[str]:
        ct = self._ct
        if ct is None:
            ct = self._ct = frozenset(self._h.class_types())
        return ct

    @property
    def instance_types(self) -> tuple[str, ...]:
        return tuple(self._h.instance_types())

    @property
    def descendant_type_set(self) -> frozenset[str]:
        return frozenset(self._h.descendant_type_set())

    @property
    def direct_descendant_type_set(self) -> set[str]:
        # Union of the class_types of the *direct* children (BaseSegment parity).
        result: set[str] = set()
        for seg in self.segments:
            result.update(seg.class_types)
        return result

    @property
    def can_start_end_non_code(self) -> bool:
        # Class attribute in BaseSegment; only FileSegment + UnparsableSegment
        # set it True.
        return self.is_type("file", "unparsable")

    @property
    def source_fixes(self) -> list[Any]:
        # Arena nodes come straight from a parse and carry no prior source fixes
        # (matches a freshly-parsed native segment's empty list).
        return []

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
        pm = self._h.pos_marker
        assert pm, f"{self} has no PositionMarker"
        return pm.working_loc

    def get_end_loc(self) -> tuple[int, int]:
        pm = self._h.pos_marker
        assert pm, f"{self} has no PositionMarker"
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

    def select_children(
        self,
        start_seg: Optional["RsSegment"] = None,
        stop_seg: Optional["RsSegment"] = None,
        select_if: Any = None,
        loop_while: Any = None,
    ) -> list[RsSegment]:
        # Port of BaseSegment.select_children; index() relies on __eq__ (uuid)
        # + interning, so start/stop segments match by node identity.
        segs = self.segments
        start_index = segs.index(start_seg) if start_seg else -1
        stop_index = segs.index(stop_seg) if stop_seg else len(segs)
        buff = []
        for seg in segs[start_index + 1 : stop_index]:
            if loop_while and not loop_while(seg):
                break
            if not select_if or select_if(seg):
                buff.append(seg)
        return buff

    # No coverage: reflow (DepthMap) entry points. Not exercised even under
    # the forced-engine env at this point in the stack — reflow only runs over
    # the façade once the LT fix rules join FACADE_SAFE_RULES (stack-04).
    @property
    def raw_segments_with_ancestors(  # pragma: no cover
        self,
    ) -> list[tuple[RsSegment, list[Any]]]:
        # Reflow hot path (DepthMap). Use the bulk arena traversal — one FFI call
        # returning every leaf with its full path — instead of a path_to() FFI per
        # leaf, and cache it (the arena is immutable, so successive reflow rules on
        # the same root reuse it).
        cached = self._rwa
        if cached is not None:
            return cached
        from sqlfluff.core.parser.segments.base import PathStep

        out: list[tuple[RsSegment, list[Any]]] = [
            (
                RsSegment(leaf_h),
                [
                    PathStep(RsSegment(h), idx, ln, tuple(cidx))  # type: ignore[arg-type]
                    for (h, idx, ln, cidx) in steps
                ],
            )
            for (leaf_h, steps) in self._h.raw_segments_with_ancestors()
        ]
        self._rwa = out
        return out

    def reflow_depth_data(  # pragma: no cover
        self,
    ) -> tuple[
        list[tuple[int, list[tuple[int, int, int, str]]]],
        list[tuple[int, list[str]]],
    ]:
        # Reflow DepthMap fast path: raw arena-side scalars — per leaf, its
        # top-down stack of (anc_uuid, idx, len, stack_pos), plus the deduped
        # (anc_uuid, class_types). ``DepthMap.from_parent`` assembles DepthInfo
        # from these (core must not import sqlfluff.utils, so not built here).
        return self._h.reflow_depth_info()

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

    def get_identifier(self) -> Any:
        # Port of CTEDefinitionSegment.get_identifier: blindly the first
        # identifier child (the CTE grammar guarantees one).
        return self.get_child("identifier")

    @property
    def source_str(self) -> str:
        # TemplateSegment.source_str is the source text at the placeholder; for
        # the façade that's the source slice at this node's position.
        pm = self.pos_marker
        return pm.source_str() if pm is not None else ""

    def path_to(self, other: "RsSegment") -> list[Any]:
        from sqlfluff.core.parser.segments.base import PathStep

        # `other` may be a freshly-constructed segment (e.g. a reflow-created
        # WhitespaceSegment) that isn't in the arena — it has no `_h`. Native
        # path_to returns [] when `other` isn't found under self; match that
        # rather than crashing.
        if not isinstance(other, RsSegment):
            return []
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
    ) -> Iterator[RsSegment]:
        # Return an iterator (not a list) to match BaseSegment.recursive_crawl,
        # so callers can `next(...)` on it (e.g. get_alias).
        if isinstance(no_recursive_seg_type, str):
            nr = [no_recursive_seg_type]
        else:
            nr = list(no_recursive_seg_type) if no_recursive_seg_type else []
        return iter(
            [
                RsSegment(x)
                for x in self._h.recursive_crawl(
                    list(seg_type), recurse_into, nr, allow_self
                )
            ]
        )

    def recursive_crawl_all(self, reverse: bool = False) -> Iterator[RsSegment]:
        segs = [RsSegment(x) for x in self._h.recursive_crawl_all()]
        return iter(reversed(segs)) if reverse else iter(segs)

    def get_alias(self) -> Any:
        # Port of SelectClauseElementSegment.get_alias (dialect_ansi.py):
        # navigation-only, so it works over the façade. Returns ColumnAliasInfo.
        from sqlfluff.core.dialects.common import ColumnAliasInfo

        alias_expression_segment = next(
            self.recursive_crawl(
                "alias_expression", no_recursive_seg_type="select_statement"
            ),
            None,
        )
        if alias_expression_segment is None:
            return None
        alias_identifier_segment = next(
            (s for s in alias_expression_segment.segments if s.is_type("identifier")),
            None,
        )
        if alias_identifier_segment is None:
            return None
        aliased_segment = next(
            s
            for s in self.segments
            if not s.is_whitespace and not s.is_meta and s != alias_expression_segment
        )
        column_reference_segments = []
        if aliased_segment.is_type("column_reference"):
            column_reference_segments.append(aliased_segment)
        else:
            column_reference_segments.extend(
                aliased_segment.recursive_crawl("column_reference")
            )
        # RsSegment duck-types BaseSegment; cast for the typed NamedTuple.
        return ColumnAliasInfo(
            alias_identifier_name=alias_identifier_segment.raw,
            aliased_segment=cast(Any, aliased_segment),
            column_reference_segments=cast(Any, column_reference_segments),
        )

    def iter_segments(
        self, expanding: Any = None, pass_through: bool = False
    ) -> Iterator["RsSegment"]:
        # Faithful port of BaseSegment.iter_segments: expand children whose type
        # is in `expanding` (e.g. recurse into bracketed to reach a nested
        # SELECT), carrying `expanding` deeper only when pass_through is set.
        for s in self.segments:
            if expanding and s.is_type(*expanding):
                yield from s.iter_segments(
                    expanding=expanding if pass_through else None
                )
            else:
                yield s

    # -- fix support ---------------------------------------------------------
    def set_parent(self, parent: Any, idx: int) -> None:
        # No-op: the arena already encodes parentage (get_parent reads it) and a
        # façade node's parent is fixed. Native uses this to wire up freshly
        # constructed fix segments — irrelevant to detection over the arena.
        pass

    def copy(
        self,
        segments: Optional[tuple[Any, ...]] = None,
        parent: Optional[Any] = None,
        parent_idx: Optional[int] = None,
        preserve_uuid: bool = False,
    ) -> Any:
        """Materialise a real Python ``BaseSegment`` tree from this arena subtree.

        Mirrors :meth:`BaseSegment.copy`: recurses to build child copies (unless
        ``segments`` is supplied), keeps this node's ``pos_marker``, and honours
        ``parent``/``parent_idx``. The arena itself is never mutated; this returns
        a freestanding real segment tree that rules can safely hand to fixes.

        Class identity is reconstructed via a synthetic segment class whose
        ``type``/``class_types`` exactly match the arena node (see
        :func:`_synth_segment_class`), so ``is_type`` and ``recursive_crawl_all``
        line up 1:1 with the façade original (as ``ST05.SegmentCloneMap`` relies
        on) while every leaf carries the right ``raw``/``pos_marker`` and each
        node's ``pos_marker`` remains assignable.
        """
        from sqlfluff.core.helpers.identity import get_next_id

        h = self._h
        cls = _synth_segment_class(
            h.segment_class or "", h.type, self.class_types, h.is_raw()
        )

        if h.is_raw():
            fold = h.casefold()
            casefold = (
                str.upper if fold == "upper" else str.lower if fold == "lower" else None
            )
            # The arena stores the quoted_value capture group as a string; a
            # numeric index arrives as e.g. "1" and must be an int for
            # ``re.Match.group`` (a numeric string is treated as a group *name*).
            # This mirrors the conversion in ``RsSegment.normalize``.
            quoted_value: Optional[tuple[str, Union[str, int]]] = h.quoted_value()
            if quoted_value:
                pattern, group = quoted_value
                try:
                    group = int(group)
                except (TypeError, ValueError):
                    pass
                quoted_value = (pattern, group)
            new_segment = cls(
                raw=h.raw,
                pos_marker=h.pos_marker,
                instance_types=tuple(h.instance_types()),
                trim_start=h.trim_start(),
                trim_chars=h.trim_chars(),
                quoted_value=quoted_value,
                escape_replacements=h.escape_replacements(),
                casefold=casefold,
            )
            if preserve_uuid:
                # Keep the arena node's uuid so native ``apply_fixes`` (which
                # matches fixes to segments by ``anchor.uuid``) lines up with the
                # façade fixes — the uuid-bridge for tree-restructuring fixes.
                new_segment.uuid = self._uid
            if parent is not None:
                assert parent_idx is not None
                new_segment.set_parent(parent, parent_idx)
            return new_segment

        # Container node: build via __new__ (like BaseSegment.copy) so we bypass
        # the parse-time validation in __init__ and just transplant state.
        new_segment = cls.__new__(cls)  # type: ignore[call-overload]
        new_segment.pos_marker = h.pos_marker
        new_segment.uuid = self._uid if preserve_uuid else get_next_id()
        if parent is not None:
            assert parent_idx is not None
            new_segment.set_parent(parent, parent_idx)
        if segments is not None:
            new_segment.segments = tuple(segments)
        else:
            new_segment.segments = tuple(
                child.copy(
                    parent=new_segment, parent_idx=idx, preserve_uuid=preserve_uuid
                )
                for idx, child in enumerate(self.segments)
            )
        return new_segment

    def edit(
        self,
        raw: Optional[str] = None,
        source_fixes: Any = None,
        source_str: Optional[str] = None,
    ) -> Any:
        """Return a real segment for a fix's replacement text.

        The arena is not mutated; the returned segment only carries the new raw
        (or, for a placeholder edit, the new source_str) + this node's position,
        which is all the source-patch fixer needs. Mirrors ``RawSegment.edit`` and
        ``TemplateSegment.edit``: when ``source_str`` is given we're editing a
        template placeholder, so return a ``TemplateSegment``.
        """
        from sqlfluff.core.parser import RawSegment

        if source_str is not None:
            from sqlfluff.core.parser.segments.meta import TemplateSegment

            return TemplateSegment(
                pos_marker=self.pos_marker,
                source_str=source_str,
                block_type=self.block_type or "",
                source_fixes=source_fixes,
            )
        # Mirror RawSegment.edit: `raw` defaults to the current raw (fixes that
        # only set source_fixes, e.g. JJ01, pass raw=None but must keep the raw).
        return RawSegment(
            raw=raw if raw is not None else self.raw,
            pos_marker=self.pos_marker,
            source_fixes=source_fixes,
        )

    def __getattr__(self, name: str) -> Any:
        # Only fires for BaseSegment API the façade doesn't implement yet. Raising
        # keeps behaviour honest — such rules aren't in FACADE_SAFE_RULES.
        raise AttributeError(
            f"RsSegment (arena façade) does not implement {name!r}; "
            "this rule is not façade-safe yet."
        )

    def __repr__(self) -> str:
        return f"RsSegment({self._h!r})"

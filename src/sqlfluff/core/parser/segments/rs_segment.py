"""Experimental: a read-only ``BaseSegment`` facade over the Rust parse arena.

When the Rust parser runs, the root segment carries an ``RsTree`` arena
(``_rs_tree``). :class:`RsSegment` wraps one of its ``RsHandle`` cursors and
answers the ``BaseSegment`` API rules crawl with, so Python rules can run over
the arena without a ``BaseSegment`` tree. Anything not implemented raises
``AttributeError`` rather than silently differing from native.
"""

# Accessors are one-line delegations mirroring documented BaseSegment members.
# ruff: noqa: D102

from __future__ import annotations

import weakref
from typing import TYPE_CHECKING, Any, Iterator, Optional, Union, cast

import regex

from sqlfluff.core.parser.segments.base import BaseSegment, PathStep
from sqlfluff.core.parser.segments.raw import RawSegment

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.parser.segments.base import SourceFix
    from sqlfluffrs import RsHandle, RsPositionMarker

# One wrapper per arena node, so `is` comparisons (used across the rule engine)
# behave as on native segments. Keyed by the node's (random v4) uuid and held
# weakly, so wrappers are freed once unreferenced.
_INTERN: weakref.WeakValueDictionary[int, RsSegment] = weakref.WeakValueDictionary()


class RsSegment:
    """A read-only ``BaseSegment`` duck-type backed by an arena ``RsHandle``."""

    # Caches: the arena is read-only here, so per-node values never go stale.
    __slots__ = (
        "_h",
        "_uid",
        "_segments",
        "_raws",
        "_ct",
        "_dts",
        "_ddts",
        "_ci",
        "_hash",
        "__weakref__",
    )
    _h: RsHandle
    _uid: int
    _segments: Optional[tuple[RsSegment, ...]]
    _raws: Optional[list[RsSegment]]
    _ct: Optional[frozenset[str]]
    _dts: Optional[frozenset[str]]
    _ddts: Optional[set[str]]
    _ci: Optional[tuple[int, ...]]
    _hash: Optional[int]

    def __new__(cls, handle: RsHandle) -> RsSegment:
        # State is set here, not in __init__, which would rerun on cache hits.
        uid = handle.uuid
        obj = _INTERN.get(uid)
        if obj is None:
            obj = object.__new__(cls)
            obj._h = handle
            obj._uid = uid
            obj._segments = None
            obj._raws = None
            obj._ct = None
            obj._dts = None
            obj._ddts = None
            obj._ci = None
            obj._hash = None
            _INTERN[uid] = obj
        return obj

    def _class_name(self) -> str:
        # Stands in for native's class name in __eq__/__hash__. The arena has
        # none for metas, which type plus is_implicit tell apart instead.
        return self._h.segment_class or f"{self._h.type}:{self.is_implicit}"

    def __eq__(self, other: object) -> bool:
        # As BaseSegment.__eq__: same node, or same class, raw and start.
        if not isinstance(other, RsSegment):
            return False
        if self._uid == other._uid:
            return True
        pm, other_pm = self._h.pos_marker, other._h.pos_marker
        return (
            self._class_name() == other._class_name()
            and self.raw == other.raw
            and pm is not None
            and other_pm is not None
            and pm.working_loc == other_pm.working_loc
        )

    def __hash__(self) -> int:
        # As BaseSegment._hash, cached.
        if self._hash is None:
            pm = self._h.pos_marker
            start = pm.source_slice.start if pm else None
            self._hash = hash((self._class_name(), self.raw, start))
        return self._hash

    def __repr__(self) -> str:
        return f"RsSegment({self._h!r})"

    def __getattr__(self, name: str) -> Any:
        # Only reached for BaseSegment API the facade doesn't implement.
        raise AttributeError(f"RsSegment (arena facade) does not implement {name!r}")

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

    def normalize(self, value: Optional[str] = None) -> str:
        # Mirrors RawSegment.normalize. The arena's patterns use the Rust regex
        # crate's `(?<name>...)` syntax, which `re` rejects but `regex` accepts.
        raw_buff = value or self._h.raw
        qv = self._h.quoted_value()
        if qv:
            _match = regex.match(qv[0], raw_buff)
            if _match:
                # The arena stores the group as a string; "1" means index 1.
                group: Union[str, int] = int(qv[1]) if qv[1].isdigit() else qv[1]
                _group_match = _match.group(group)
                if isinstance(_group_match, str):
                    raw_buff = _group_match
        for old, new in self._h.escape_replacements() or []:
            raw_buff = regex.sub(old, new, raw_buff)
        return raw_buff

    def raw_normalized(self, casefold: bool = True) -> str:
        if not self._h.is_raw():
            return "".join(s.raw_normalized(casefold) for s in self.raw_segments)
        raw_buff = self.normalize()
        fold = self._h.casefold()
        if fold and casefold:
            raw_buff = raw_buff.upper() if fold == "upper" else raw_buff.lower()
        return raw_buff

    @property
    def trim_start(self) -> Optional[tuple[str, ...]]:
        return self._h.trim_start()

    @property
    def trim_chars(self) -> Optional[tuple[str, ...]]:
        return self._h.trim_chars()

    raw_trimmed = RawSegment.raw_trimmed

    @property
    def source_fixes(self) -> list[SourceFix]:
        # Always empty straight after a parse; the arena holds none until fix
        # edits are ingested.
        return []

    @property
    def source_str(self) -> str:
        # Native only defines this on TemplateSegment; rules probe it via getattr.
        pm = self._h.pos_marker
        return pm.source_str() if pm is not None else ""

    @property
    def block_type(self) -> Optional[str]:
        return self._h.block_type()

    @property
    def block_uuid(self) -> Optional[int]:
        # Native stores a uuid.UUID; the arena gives its int (hashable, truthy).
        return self._h.block_uuid()

    # -- types ---------------------------------------------------------------
    @property
    def type(self) -> str:
        # The class-level type; get_type() gives the instance type.
        return self._h.class_type()

    def get_type(self) -> str:
        return self._h.type

    @property
    def class_types(self) -> frozenset[str]:
        ct = self._ct
        if ct is None:
            ct = self._ct = frozenset(self._h.class_types())
        return ct

    def is_type(self, *seg_type: str) -> bool:
        # The arena's class_types already include instance types.
        return not self.class_types.isdisjoint(seg_type)

    @property
    def instance_types(self) -> tuple[str, ...]:
        return tuple(self._h.instance_types())

    @property
    def descendant_type_set(self) -> frozenset[str]:
        dts = self._dts
        if dts is None:
            dts = self._dts = frozenset(self._h.descendant_type_set())
        return dts

    @property
    def direct_descendant_type_set(self) -> set[str]:
        # Cached like native, which crawlers read for every node they visit.
        if self._ddts is None:
            self._ddts = {t for seg in self.segments for t in seg.class_types}
        return self._ddts

    # -- flags ---------------------------------------------------------------
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

    @property
    def is_templated(self) -> bool:
        return self._h.is_templated

    def is_raw(self) -> bool:
        return self._h.is_raw()

    @property
    def is_implicit(self) -> bool:
        return bool(self._h.is_implicit())

    @property
    def indent_val(self) -> int:
        t = self._h.type
        return 1 if t == "indent" else (-1 if t == "dedent" else 0)

    @property
    def can_start_end_non_code(self) -> bool:
        # Only FileSegment and UnparsableSegment set this natively.
        return self.is_type("file", "unparsable")

    # -- position ------------------------------------------------------------
    @property
    def pos_marker(self) -> Optional[RsPositionMarker]:
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
        # Cached like native: reflow's from_root cache keys on this list's identity.
        if self._raws is None:
            self._raws = [RsSegment(h) for h in self._h.raw_segments()]
        return self._raws

    @property
    def _code_indices(self) -> tuple[int, ...]:
        # Native caches this too; path_to hands it out on every step.
        ci = self._ci
        if ci is None:
            ci = self._ci = tuple(i for i, s in enumerate(self.segments) if s.is_code)
        return ci

    def get_raw_segments(self) -> list[RsSegment]:
        return self.raw_segments

    def get_parent(self) -> Optional[tuple[RsSegment, int]]:
        parent = self._h.get_parent()
        return (RsSegment(parent[0]), parent[1]) if parent else None

    def get_child(self, *seg_type: str) -> Optional[RsSegment]:
        child = self._h.get_child(list(seg_type))
        return RsSegment(child) if child is not None else None

    def get_children(self, *seg_type: str) -> list[RsSegment]:
        return [RsSegment(h) for h in self._h.get_children(list(seg_type))]

    def path_to(self, other: Any) -> list[PathStep]:
        # Native returns [] for self or a segment outside this tree; so does the
        # arena, and a non-arena segment (e.g. built for a fix) can't be inside.
        if not isinstance(other, RsSegment):
            return []
        steps = []
        for h, idx, length in self._h.path_to(other._h):
            seg = RsSegment(h)
            steps.append(PathStep(cast(Any, seg), idx, length, seg._code_indices))
        return steps

    # Native's own implementations: they only use `segments` and `is_type`,
    # so reusing them keeps behaviour (and stack depth) identical.
    count_segments = BaseSegment.count_segments
    select_children = BaseSegment.select_children
    iter_segments = BaseSegment.iter_segments
    recursive_crawl_all = BaseSegment.recursive_crawl_all

    def recursive_crawl(
        self,
        *seg_type: str,
        recurse_into: bool = True,
        no_recursive_seg_type: Union[str, list[str], None] = None,
        allow_self: bool = True,
    ) -> Iterator[RsSegment]:
        if isinstance(no_recursive_seg_type, str):
            no_recursive_seg_type = [no_recursive_seg_type]
        # Wrap lazily: callers often take only the first match (next/any).
        return map(
            RsSegment,
            self._h.recursive_crawl(
                list(seg_type),
                recurse_into,
                list(no_recursive_seg_type or []),
                allow_self,
            ),
        )

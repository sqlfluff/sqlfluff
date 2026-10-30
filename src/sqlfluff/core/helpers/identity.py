"""Process-global unique identifiers for segments.

Replaces per-instance ``uuid4()`` generation. A monotonic counter is
sufficient because segment ``uuid`` values are only ever used as opaque,
in-memory identity keys (dict keys and ``==`` in the fix engine). They never
need cryptographic unpredictability or cross-process uniqueness, and are never
parsed back as RFC-4122 UUIDs.

The high bits carry a source tag so these ids stay disjoint from token ids
minted on the Rust side (see the ``identity`` module in ``sqlfluffrs_types``,
which uses ``RUST_TAG = 2 << 120``). Both runtimes count from 1, so without the
tag a Python-created segment and a Rust-origin token would share low integer
ids -- and the fix engine would then treat two unrelated segments as the same
anchor. This is not hypothetical: ``PyToken.uuid`` surfaces the Rust ``u128``
to Python verbatim, so the two id spaces genuinely meet inside one tree.

Parser and grammar cache keys come from ``get_cache_key``, which shares this
counter but adds a random prefix per process, because keys made in different
processes can meet in one parse.
"""

from __future__ import annotations

import itertools
import os

# Source tag OR'd into the high bits of every Python-minted id. Must stay
# distinct from the Rust tag (``2 << 120``). Fits within 128 bits alongside any
# realistic process-lifetime counter value (which is always < ``2 ** 120``).
_PYTHON_TAG = 1 << 120

_counter = itertools.count(1)


def get_next_id() -> int:
    """Return a process-unique, source-tagged identifier.

    ``next()`` on an ``itertools.count`` is atomic under the CPython GIL -- its
    C-level ``__next__`` never releases the GIL mid-increment -- so this is
    thread-safe without an explicit lock. Avoiding the lock is the point: it
    keeps the per-segment cost to a single counter increment rather than
    re-introducing the lock acquire/release that motivated dropping ``uuid4``.
    """
    return _PYTHON_TAG | next(_counter)


# Random prefix for this process's cache keys. Its fixed width (64 bits, as 16
# hex digits) means no two (prefix, counter) pairs can make the same key.
_cache_key_prefix: str


def _draw_cache_key_prefix() -> None:
    """Draw a new random prefix for this process's cache keys."""
    global _cache_key_prefix
    _cache_key_prefix = os.urandom(8).hex()


_draw_cache_key_prefix()
# A forked child carries on from its parent's counter, so it draws its own prefix.
# Windows has no fork, and so no ``register_at_fork``.
if hasattr(os, "register_at_fork"):
    os.register_at_fork(after_in_child=_draw_cache_key_prefix)


def get_cache_key() -> str:
    """Return a cache key for a parser or grammar, unique across processes.

    Unlike segment ids, keys made in different processes can meet in one parse.
    Parsers and grammars pickle by value, so a dialect sent to a worker process
    keeps its keys, while the worker's own counter starts again from low values
    and would reuse them. The random prefix keeps the two sets apart. Segment
    classes pickle by reference, so every process mints their keys itself and
    they need no prefix.
    """
    return f"{_cache_key_prefix}{next(_counter):x}"

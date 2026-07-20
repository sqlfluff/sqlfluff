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
"""

from __future__ import annotations

import itertools

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

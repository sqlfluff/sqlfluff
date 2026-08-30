"""Persistent caching of lint results between runs.

Linting a file is expensive: it is templated, lexed, parsed and then walked
once per rule. For a project of any size most files are unchanged between one
invocation and the next -- the classic case being ``sqlfluff lint`` run from a
pre-commit hook -- and so all of that work is repeated for no benefit.

This module implements an opt-in, on-disk cache which allows those files to be
skipped entirely. The design is deliberately conservative:

* **Only clean files are cached.** An entry is written only for a file which
  produced *no* violations at all (not even warnings, and not templating or
  parsing errors). Anything with something to report is always re-linted, so
  the cache can never suppress a diagnostic the user has not already resolved.
* **A hit must be provably equivalent.** The key covers everything which can
  change the result for a file: the SQLFluff version, the set of installed
  plugins, the file's fully resolved configuration, the state the templater
  reads from outside the file, and the bytes of the file itself.
* **Caching is opt-in per templater.** ``RawTemplater.cache_fingerprint()``
  returns ``None`` by default, which disables caching. A templater has to
  positively declare what external state it reads before its files become
  eligible, so a third party templater is never cached by accident.
* **The cache never changes behaviour on failure.** Any problem reading,
  writing or keying is logged and degrades to "no cache" for that file or that
  run. It is never surfaced to the user as an error.

Entries also carry the file statistics (character and segment counts) that
:class:`~sqlfluff.core.linter.linted_dir.LintedDir` derives from a parsed
file, so that a cached run produces the same serialised output as an uncached
one rather than reporting zeroes.
"""

import hashlib
import json
import logging
import os
import tempfile
import time
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Optional, TypedDict

from sqlfluff.core.helpers.hashing import hash_file_bytes, hash_strings

# NOTE: These two are private to `plugin.host`, and reused here deliberately
# rather than reimplemented. `_discover_plugins` is the single definition of
# what counts as an installed SQLFluff plugin, and the fingerprint has to agree
# with it exactly or the cache will miss a plugin the linter is using.
# `_get_sqlfluff_version` reads the installed distribution metadata directly,
# which avoids importing the top level `sqlfluff` package from inside it.
from sqlfluff.core.plugin.host import _discover_plugins, _get_sqlfluff_version

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.config import FluffConfig

linter_logger: logging.Logger = logging.getLogger("sqlfluff.linter")

# Bump this whenever the on-disk layout or the meaning of a key changes. A
# mismatch discards the whole cache rather than risking a stale hit.
CACHE_SCHEMA_VERSION = 1

#: The default cache directory, resolved relative to the working directory.
DEFAULT_CACHE_DIR = ".sqlfluff_cache"

#: The file within the cache directory which holds the entries.
CACHE_FILENAME = "cache.json"

#: Entries not seen for this long are dropped when the cache is written. This
#: bounds growth as files are renamed or deleted without needing to stat every
#: path we have ever recorded.
ENTRY_TTL_SECONDS = 30 * 24 * 60 * 60  # 30 days

#: The statistics keys which a cache entry is expected to carry, in the order
#: ``file_statistics()`` produces them. The order is preserved on the way in
#: and out so that a cached record serialises identically to a linted one --
#: JSON objects keep insertion order, and a reordered ``statistics`` block
#: would be a visible difference in ``--format json`` output.
_STATISTICS_KEYS = ("source_chars", "templated_chars", "segments", "raw_segments")


class CacheEntry(TypedDict):
    """A single cached result.

    Attributes:
        key: The hex digest which must match for this entry to be a hit.
        statistics: The file statistics recorded by ``LintedDir``, replayed on
            a hit so that serialised output is unaffected by caching.
        last_seen: Unix timestamp of the last run which wrote or hit this entry.
    """

    key: str
    statistics: dict[str, int]
    last_seen: int


def config_digest(config: "FluffConfig") -> str:
    """Return a stable digest of a fully resolved config object.

    This uses :meth:`FluffConfig.iter_vals`, which already excludes the derived
    and non-serialisable entries (``dialect_obj``, ``templater_obj`` and the
    resolved rule allow/deny lists). Each of those is a pure function of values
    which *are* included, so excluding them loses no information.

    The type name of each value is included alongside its representation so
    that, for example, a section label cannot collide with a key whose value is
    an empty string.
    """
    hasher = hashlib.sha256()
    for indent, key, value in config.iter_vals():
        hash_strings(hasher, str(indent), key, type(value).__name__, repr(value))
    return hasher.hexdigest()


def run_fingerprint() -> str:
    """Return a digest of the state which invalidates the *whole* cache.

    That is the SQLFluff version plus the name and version of every installed
    SQLFluff plugin. A change to any of those can change the result for every
    file, so rather than repeating it in each key we store it once in the cache
    header and discard the file when it moves.
    """
    hasher = hashlib.sha256()
    hash_strings(hasher, "schema", str(CACHE_SCHEMA_VERSION))
    hash_strings(hasher, "sqlfluff", _get_sqlfluff_version())
    try:
        plugins = sorted((name, version) for _, name, version in _discover_plugins())
    except Exception as err:  # pragma: no cover
        # Plugin discovery walks installed distributions and so can fail on a
        # broken environment. Fold the failure into the digest: it is stable
        # for as long as the failure is, and changes when it is fixed.
        linter_logger.debug("Cache: plugin discovery failed: %s", err)
        plugins = [("<discovery-failed>", str(err))]
    for name, version in plugins:
        hash_strings(hasher, "plugin", name, version)
    return hasher.hexdigest()


def _coerce_entry(value: Any) -> Optional[CacheEntry]:
    """Validate one deserialised entry, returning None if it is not usable.

    The cache file is ordinary JSON on disk which a user may have truncated,
    hand edited or shared between incompatible versions. Every field is checked
    rather than trusted, because a malformed entry that we accepted could cause
    a file to be silently skipped.
    """
    if not isinstance(value, dict):
        return None
    key = value.get("key")
    statistics = value.get("statistics")
    last_seen = value.get("last_seen")
    if not isinstance(key, str) or not key:
        return None
    # NOTE: `isinstance(True, int)` is True, so booleans are excluded
    # explicitly. They should never appear, but a hand edited file might.
    if not isinstance(last_seen, int) or isinstance(last_seen, bool):
        return None
    if not isinstance(statistics, dict):
        return None
    if set(statistics) != set(_STATISTICS_KEYS):
        return None
    # Counts of characters and segments; a negative one could only come from a
    # hand edited file, and would be replayed straight into `--format json`.
    if not all(
        isinstance(v, int) and not isinstance(v, bool) and v >= 0
        for v in statistics.values()
    ):
        return None
    return CacheEntry(
        key=key,
        # Rebuild in canonical order rather than trusting the order in the
        # file, so that a hand edited cache cannot change output ordering.
        statistics={k: statistics[k] for k in _STATISTICS_KEYS},
        last_seen=last_seen,
    )


class LintCache:
    """An on-disk cache of files which linted clean.

    A cache is only useful across runs, so the lifecycle is:

    #. :meth:`load` reads and validates any existing cache file.
    #. :meth:`check` is called once per file *before* linting. A hit returns
       the statistics to replay; a miss returns ``None`` and retains the key it
       computed from the file as it stood before the run touched it.
    #. :meth:`record` is called for each file which linted clean. It stores a
       result only if the file still matches that key, so an entry is always
       backed by a lint of exactly the contents it names.
    #. :meth:`persist` writes the file back atomically.

    All of this happens in the main process. Workers never touch the cache, so
    parallel linting needs no coordination.
    """

    def __init__(self, cache_dir: str, root_config: "FluffConfig") -> None:
        self.cache_dir = cache_dir
        self.cache_path = os.path.join(cache_dir, CACHE_FILENAME)
        self.root_config = root_config
        self.run_fingerprint = run_fingerprint()
        self._entries: dict[str, CacheEntry] = {}
        # Keys computed during `check`, so that `record` can require the file
        # to be unchanged since before it was linted.
        self._pending_keys: dict[str, str] = {}
        # Everything a key needs from a file's configuration, memoised per
        # *directory* for the run. `make_child_from_path` builds a whole
        # `FluffConfig`, which expands a fresh dialect object every time;
        # measured at tens of milliseconds per call, it would otherwise
        # dominate the cost of a lookup and undo most of the benefit of a hit.
        # What it resolves depends only on the file's directory (config files
        # are discovered by walking directories), so one entry per directory is
        # exact rather than approximate.
        #
        # Only the derived strings are kept, never the `FluffConfig` itself, so
        # the expanded dialect it holds is released instead of being pinned for
        # the run once per directory in the project.
        #
        # NOTE: Inline `-- sqlfluff:` directives are deliberately not applied
        # here. The linter applies them after reading the file, and they live
        # in the file's own bytes, which the key already covers.
        self._directory_keys: dict[str, Optional[tuple[str, str, str]]] = {}
        # Templater fingerprints, memoised for the duration of the run and
        # keyed on the config rather than the directory, so that directories
        # which share a config also share the work. Computing one can mean
        # walking whole directory trees. Memoising here rather than inside the
        # templater keeps the lifetime tied to a single run, so a long lived
        # process which lints, edits a macro, and lints again still sees the
        # change.
        self._templater_digests: dict[tuple[str, str], Optional[str]] = {}
        # Cleared when a write fails; the cache then degrades to a no-op rather
        # than repeatedly retrying an operation we know is broken.
        self._writable = True
        self.hits = 0
        self.misses = 0

    # ### Construction

    @classmethod
    def from_config(
        cls, config: "FluffConfig", user_rules: Optional[Sequence[Any]] = None
    ) -> Optional["LintCache"]:
        """Build a cache from config, or return None if caching is disabled.

        Returns ``None`` (rather than an inert cache) when caching is off, so
        that callers can skip the per-file key work entirely.

        Args:
            config: The root config for the run.
            user_rules: Rule classes passed programmatically to
                :class:`Linter`. Their presence disables caching entirely; see
                below.

        Caching is declined outright when an API caller has supplied
        ``Linter(user_rules=...)``. Every other input to a lint result can be
        identified by something stable -- a file by its bytes, config by its
        values, a plugin by its version -- but a rule class handed to us
        in-process has no such identity. Its *name* would not change when its
        body did, so keying on it would let an edited rule be masked by a
        cached clean result. Declining is the same trade made for templaters
        which do not declare what they read.
        """
        if not config.get("cache", default=False):
            return None
        if user_rules:
            linter_logger.warning(
                "Lint caching is disabled because this Linter was given "
                "custom rules, whose definitions cannot be fingerprinted."
            )
            return None
        cache_dir = config.get("cache_dir", default=DEFAULT_CACHE_DIR)
        if not cache_dir:  # pragma: no cover
            cache_dir = DEFAULT_CACHE_DIR
        cache = cls(os.path.abspath(str(cache_dir)), config)
        cache.load()
        return cache

    # ### Loading and persisting

    def load(self) -> None:
        """Read the cache file, tolerating anything unexpected.

        A cache which cannot be read is simply an empty cache. This covers a
        first run, a truncated file, a file written by a different schema
        version, and a file written by a different SQLFluff or plugin version.
        """
        try:
            with open(self.cache_path, encoding="utf-8") as f:
                payload = json.load(f)
        except FileNotFoundError:
            linter_logger.debug("Cache: no existing cache at %s", self.cache_path)
            return
        except (OSError, ValueError) as err:
            linter_logger.debug("Cache: discarding unreadable cache: %s", err)
            return

        if not isinstance(payload, dict):
            linter_logger.debug("Cache: discarding cache with unexpected structure.")
            return
        if payload.get("schema_version") != CACHE_SCHEMA_VERSION:
            linter_logger.debug("Cache: discarding cache from a different schema.")
            return
        if payload.get("run_fingerprint") != self.run_fingerprint:
            linter_logger.debug(
                "Cache: discarding cache from a different sqlfluff or plugin set."
            )
            return
        entries = payload.get("entries")
        if not isinstance(entries, dict):
            linter_logger.debug("Cache: discarding cache with unexpected entries.")
            return

        for path, raw_entry in entries.items():
            if not isinstance(path, str):  # pragma: no cover
                continue
            entry = _coerce_entry(raw_entry)
            if entry is not None:
                self._entries[path] = entry
        linter_logger.debug("Cache: loaded %s entries.", len(self._entries))

    def persist(self) -> None:
        """Write the cache back to disk atomically.

        The file is written to a temporary file in the same directory and then
        moved into place, so a concurrent reader sees either the old file or
        the new one and never a partial write. Two runs writing at once resolve
        as last-writer-wins, which is safe: a lost write only costs a miss on
        the next run.
        """
        if not self._writable:
            return
        now = int(time.time())
        cutoff = now - ENTRY_TTL_SECONDS
        entries = {
            path: entry
            for path, entry in self._entries.items()
            if entry["last_seen"] >= cutoff
        }
        payload = {
            "schema_version": CACHE_SCHEMA_VERSION,
            "run_fingerprint": self.run_fingerprint,
            "entries": entries,
        }
        try:
            # Whether *this* run created the directory decides whether we may
            # write a `.gitignore` into it; see `_write_gitignore`. Asking
            # `makedirs` to fail if it already exists answers that atomically.
            # Checking `isdir()` first and then creating would not: another
            # process can win the race in between, and we would then claim a
            # directory we did not make.
            try:
                os.makedirs(self.cache_dir, exist_ok=False)
            except FileExistsError:
                pass
            else:
                self._write_gitignore()
            # An explicit mkstemp plus os.replace is the portable way to get an
            # atomic swap: on Windows os.replace cannot act on an open handle,
            # so the temporary file has to be closed first.
            fd, tmp_path = tempfile.mkstemp(dir=self.cache_dir, suffix=".tmp")
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    json.dump(payload, f)
                os.replace(tmp_path, self.cache_path)
            except BaseException:
                # Never leave a stray temporary file behind, including on
                # KeyboardInterrupt.
                try:
                    os.unlink(tmp_path)
                except OSError:  # pragma: no cover
                    pass
                raise
        except Exception as err:
            # Broader than the OSError we expect from a read-only or full
            # filesystem, deliberately: this runs at the very end of a lint
            # run, and failing to save an optimisation must never be the thing
            # that loses the user their results. `BaseException` is not caught,
            # so Ctrl-C still stops the run.
            linter_logger.warning("Unable to write sqlfluff cache: %s", err)
            self._writable = False
            return
        linter_logger.debug("Cache: wrote %s entries.", len(entries))

    def _write_gitignore(self) -> None:
        """Make the cache directory self-ignoring for git.

        Users should not have to remember to add the cache directory to their
        ``.gitignore``, and a cache accidentally committed to a repository is
        both noise and a source of confusing hits.

        Only called for a directory this run just created. ``cache_dir`` is
        user-configurable and may point somewhere that already exists and holds
        other things; dropping a ``.gitignore`` containing ``*`` into a
        directory we did not make would silently hide the user's own untracked
        files from git.
        """
        gitignore_path = os.path.join(self.cache_dir, ".gitignore")
        if os.path.exists(gitignore_path):  # pragma: no cover
            return
        try:
            with open(gitignore_path, "w", encoding="utf-8") as f:
                f.write("# Created automatically by sqlfluff.\n*\n")
        except OSError as err:  # pragma: no cover
            # Not being able to write this is not a reason to give up on the
            # cache itself.
            linter_logger.debug("Cache: could not write .gitignore: %s", err)

    # ### Keying

    @staticmethod
    def _normalise(fname: str) -> str:
        """Normalise a path for use as a cache key.

        Absolute paths mean the cache is unambiguous regardless of the working
        directory a run was launched from. It also means the cache is specific
        to one checkout, which is the intent: it is a local build artefact.
        """
        return os.path.normcase(os.path.abspath(fname))

    def _directory_key(self, fname: str) -> Optional[tuple[str, str, str]]:
        """Config-derived key parts for the directory containing a file.

        Returns ``(templater name, templater fingerprint, config digest)``, or
        ``None`` if files in this directory cannot be cached. Memoised: see
        `_directory_keys`.
        """
        # Normalised so that two spellings of the same directory share an
        # entry rather than each paying for their own resolution.
        dirname = os.path.dirname(self._normalise(fname))
        if dirname in self._directory_keys:
            return self._directory_keys[dirname]

        result: Optional[tuple[str, str, str]] = None
        file_config = self.root_config.make_child_from_path(fname)
        templater = file_config.get("templater_obj")
        if templater is not None:
            cfg_digest = config_digest(file_config)
            memo_key = (templater.name, cfg_digest)
            if memo_key in self._templater_digests:
                fingerprint = self._templater_digests[memo_key]
            else:
                fingerprint = templater.cache_fingerprint(file_config)
                self._templater_digests[memo_key] = fingerprint
            if fingerprint is None:
                # The templater has not declared itself cacheable.
                linter_logger.debug(
                    "Cache: templater %r opts out of caching.", templater.name
                )
            else:
                result = (templater.name, fingerprint, cfg_digest)

        self._directory_keys[dirname] = result
        return result

    def _file_key(self, fname: str) -> Optional[str]:
        """Compute the cache key for a file, or None if it cannot be cached.

        The key deliberately covers more than the file: two projects can share
        a file verbatim and still lint it differently.
        """
        try:
            parts = self._directory_key(fname)
            if parts is None:
                return None
            templater_name, fingerprint, cfg_digest = parts
            hasher = hashlib.sha256()
            hash_strings(hasher, "run", self.run_fingerprint)
            hash_strings(hasher, "templater", templater_name, fingerprint)
            hash_strings(hasher, "config", cfg_digest)
            hash_file_bytes(fname, hasher)
            return hasher.hexdigest()
        except Exception as err:
            # Config resolution, templater fingerprinting and file reading can
            # all fail on a project we would otherwise decline to lint. The
            # cache must not be the thing that reports it: we fall back to
            # linting the file, which will raise or report properly.
            linter_logger.debug("Cache: unable to key %r: %s", fname, err)
            return None

    # ### Use

    def check(self, fname: str) -> Optional[dict[str, int]]:
        """Return the cached statistics for a file, or None to lint it.

        On a miss the computed key is retained, so that :meth:`record` can
        require the file to be unchanged before storing a result for it.
        """
        key = self._file_key(fname)
        if key is None:
            self.misses += 1
            return None
        normalised = self._normalise(fname)
        entry = self._entries.get(normalised)
        if entry is not None and entry["key"] == key:
            # Refresh the timestamp so an actively used entry is never aged out.
            entry["last_seen"] = int(time.time())
            self.hits += 1
            return dict(entry["statistics"])
        self._pending_keys[normalised] = key
        self.misses += 1
        return None

    def record(self, fname: str, statistics: dict[str, int]) -> None:
        """Record that a file linted clean.

        Only ever called for a file which produced no violations at all.

        The key is recomputed here and required to match the one taken in
        :meth:`check`. That guards the window between the two: if the file were
        edited while the run was in progress, the key taken before linting and
        the result produced afterwards would describe different contents, and
        storing either would be a claim we never actually verified. Requiring
        the file to be unchanged across the whole run means an entry is always
        backed by a lint of exactly the contents it names.

        The cost is one extra read and hash per clean file, which is
        negligible beside the templating, parsing and rule pass it replaces.
        """
        normalised = self._normalise(fname)
        key = self._pending_keys.pop(normalised, None)
        if key is None:
            # We never computed a key for this file, which means it is not
            # cacheable (or `check` was not called). Don't guess.
            return
        if self._file_key(fname) != key:
            linter_logger.debug(
                "Cache: %r changed while it was being linted; not recording.", fname
            )
            return
        self._entries[normalised] = CacheEntry(
            key=key,
            statistics={k: int(statistics.get(k, 0)) for k in _STATISTICS_KEYS},
            last_seen=int(time.time()),
        )

    def forget(self, fname: str) -> None:
        """Drop the pending key for a file which will not be recorded.

        `check` holds a key for every miss so that `record` can verify it. For
        a file which turns out not to be cacheable that key is never claimed,
        and on a project where most files have violations -- exactly the
        projects which get no benefit from the cache -- holding one per file
        for the whole run is wasted memory.
        """
        self._pending_keys.pop(self._normalise(fname), None)

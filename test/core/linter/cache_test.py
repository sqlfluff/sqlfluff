"""Tests for the lint result cache.

The cache trades correctness risk for speed: a hit means a file is not linted
at all. So the tests here are weighted heavily towards proving that a hit only
happens when it is *safe*, and that every input which can change a file's
result also changes its key.

The integration tests all follow the same shape: lint a project twice and
assert on `LintingResult.files_cached`, which counts the files the second run
did not have to look at.
"""

import json
import os
import time

import pytest

from sqlfluff.cli.commands import fix
from sqlfluff.cli.commands import lint as lint_command
from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.config import clear_config_caches
from sqlfluff.core.linter.cache import (
    CACHE_FILENAME,
    CACHE_SCHEMA_VERSION,
    ENTRY_TTL_SECONDS,
    LintCache,
    _coerce_entry,
    config_digest,
    run_fingerprint,
)
from sqlfluff.core.templaters import JinjaTemplater, RawTemplater
from sqlfluff.core.templaters.placeholder import PlaceholderTemplater
from sqlfluff.core.templaters.python import PythonTemplater
from sqlfluff.utils.testing.cli import invoke_assert_code

CLEAN_SQL = "SELECT\n    a,\n    b\nFROM tbl\n"
DIRTY_SQL = "select  a,b from tbl\n"


# ###
# Fixtures and helpers
# ###


def write(path, content):
    """Write text to a path, creating parents as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return str(path)


def rewrite_config(project_root, body):
    """Rewrite a project's `.sqlfluff` as a fresh process would see it.

    Config file loading is memoised for the lifetime of the process, so a
    test which edits a config file and re-lints in the same process would
    otherwise still be reading the old values. Clearing it here reproduces
    what actually happens between two CLI invocations.
    """
    write(project_root / ".sqlfluff", body)
    clear_config_caches()


@pytest.fixture
def project(tmp_path):
    """A minimal linted project with its cache directory alongside it."""
    root = tmp_path / "project"
    root.mkdir()
    write(root / ".sqlfluff", "[sqlfluff]\ndialect = ansi\n")
    return root


def make_config(project_root, cache_dir=None, **overrides):
    """Build a config rooted at the project, with caching enabled."""
    values = {
        "cache": True,
        "cache_dir": str(cache_dir or (project_root.parent / "cache")),
    }
    values.update(overrides)
    return FluffConfig.from_path(str(project_root), overrides=values)


def lint(project_root, config):
    """Lint a project and return the result."""
    return Linter(config=config).lint_paths((str(project_root),))


# ###
# Unit tests: key derivation
# ###


class TestConfigDigest:
    """`config_digest` has to react to config but not to object identity."""

    def test_stable_across_equivalent_configs(self, project):
        """Two separately built but identical configs agree."""
        assert config_digest(make_config(project)) == config_digest(
            make_config(project)
        )

    def test_reacts_to_a_changed_value(self, project):
        """Changing a rule selection changes the digest."""
        before = config_digest(make_config(project))
        after = config_digest(make_config(project, rules="LT01"))
        assert before != after

    def test_reacts_to_a_changed_dialect(self, project):
        """Changing dialect changes the digest.

        `dialect_obj` is excluded from `iter_vals`, so this proves the digest
        is picking up the underlying `dialect` string rather than relying on
        the derived object.
        """
        before = config_digest(make_config(project, dialect="ansi"))
        after = config_digest(make_config(project, dialect="postgres"))
        assert before != after

    def test_reacts_to_a_nested_value(self, project):
        """A value nested inside a rule section still counts."""
        before = config_digest(make_config(project))
        rewrite_config(
            project,
            "[sqlfluff]\ndialect = ansi\n"
            "[sqlfluff:rules:capitalisation.keywords]\ncapitalisation_policy = lower\n",
        )
        assert config_digest(make_config(project)) != before


def test__cache_run_fingerprint_is_stable():
    """The run fingerprint doesn't move between calls in one environment."""
    assert run_fingerprint() == run_fingerprint()


def test__cache_run_fingerprint_reacts_to_version(monkeypatch):
    """A new SQLFluff version invalidates every entry."""
    before = run_fingerprint()
    monkeypatch.setattr(
        "sqlfluff.core.linter.cache._get_sqlfluff_version", lambda: "0.0.0-test"
    )
    assert run_fingerprint() != before


def test__cache_run_fingerprint_reacts_to_plugins(monkeypatch):
    """Installing or upgrading a plugin invalidates every entry.

    A plugin can add, remove or change rules, which changes the result for
    every file in the project.
    """
    before = run_fingerprint()
    monkeypatch.setattr(
        "sqlfluff.core.linter.cache._discover_plugins",
        lambda: iter([(None, "made-up-plugin", "1.0.0")]),
    )
    assert run_fingerprint() != before


# ###
# Unit tests: entry validation
# ###


VALID_ENTRY = {
    "key": "abc",
    "statistics": {
        "source_chars": 1,
        "templated_chars": 2,
        "segments": 3,
        "raw_segments": 4,
    },
    "last_seen": 1234,
}


def test__cache_coerce_entry_accepts_a_valid_entry():
    """A well formed entry survives validation intact."""
    entry = _coerce_entry(VALID_ENTRY)
    assert entry is not None
    assert entry["key"] == "abc"
    assert entry["last_seen"] == 1234


def test__cache_coerce_entry_canonicalises_statistics_order():
    """Statistics come back in canonical order regardless of file order.

    JSON objects preserve insertion order, and these values are serialised
    straight into `--format json` output, so a reordered cache file must not
    reorder the output.
    """
    scrambled = dict(VALID_ENTRY)
    scrambled["statistics"] = dict(reversed(list(VALID_ENTRY["statistics"].items())))
    entry = _coerce_entry(scrambled)
    assert entry is not None
    assert list(entry["statistics"]) == [
        "source_chars",
        "templated_chars",
        "segments",
        "raw_segments",
    ]


@pytest.mark.parametrize(
    "mutation,reason",
    [
        ({"key": ""}, "empty key"),
        ({"key": 5}, "non-string key"),
        ({"last_seen": "yesterday"}, "non-integer timestamp"),
        ({"last_seen": True}, "boolean timestamp"),
        ({"statistics": []}, "non-mapping statistics"),
        ({"statistics": {"source_chars": 1}}, "missing statistics keys"),
        (
            {
                "statistics": {
                    "source_chars": 1,
                    "templated_chars": 2,
                    "segments": 3,
                    "raw_segments": 4,
                    "extra": 5,
                }
            },
            "unexpected statistics key",
        ),
        (
            {
                "statistics": {
                    "source_chars": "1",
                    "templated_chars": 2,
                    "segments": 3,
                    "raw_segments": 4,
                }
            },
            "non-integer statistic",
        ),
        (
            {
                "statistics": {
                    "source_chars": -1,
                    "templated_chars": 2,
                    "segments": 3,
                    "raw_segments": 4,
                }
            },
            "negative statistic",
        ),
    ],
)
def test__cache_coerce_entry_rejects_malformed(mutation, reason):
    """A malformed entry is dropped rather than trusted.

    The cache file is plain JSON on disk which anything could have written, and
    a bad entry we accepted would silently skip a file.
    """
    payload = dict(VALID_ENTRY)
    payload.update(mutation)
    assert _coerce_entry(payload) is None, reason


def test__cache_coerce_entry_rejects_non_mapping():
    """An entry which isn't an object at all is dropped."""
    assert _coerce_entry("not an entry") is None


# ###
# Unit tests: load and persist
# ###


class TestLoadAndPersist:
    """The cache file is untrusted input and a shared resource."""

    def test_from_config_returns_none_when_disabled(self, project):
        """No cache object at all when caching is off, so there's no cost."""
        assert LintCache.from_config(make_config(project, cache=False)) is None

    def test_from_config_declines_with_user_rules(self, project):
        """Custom rules passed to `Linter` disable caching entirely.

        Regression test. Every other input to a result has a stable identity --
        a file its bytes, config its values, a plugin its version -- but a rule
        class handed to us in-process has none: its name would not change when
        its body did. Keying on it would let an edited rule be masked by a
        cached clean result, so we decline instead.
        """
        assert LintCache.from_config(make_config(project), user_rules=[object]) is None

    def test_from_config_builds_when_enabled(self, project, tmp_path):
        """The configured directory is respected and made absolute."""
        cache = LintCache.from_config(make_config(project, cache_dir=tmp_path / "c"))
        assert cache is not None
        assert cache.cache_dir == os.path.abspath(str(tmp_path / "c"))

    def test_missing_file_loads_empty(self, project, tmp_path):
        """A first run is just an empty cache."""
        cache = LintCache(str(tmp_path / "nope"), make_config(project))
        cache.load()
        assert cache._entries == {}

    @pytest.mark.parametrize(
        "content",
        [
            "not json at all",
            "[]",
            '{"schema_version": 999, "run_fingerprint": "x", "entries": {}}',
            '{"schema_version": 1, "run_fingerprint": "wrong", "entries": {}}',
            '{"schema_version": 1, "entries": "not a mapping"}',
        ],
        ids=["invalid", "wrong-type", "wrong-schema", "wrong-run", "bad-entries"],
    )
    def test_unusable_file_loads_empty(self, project, tmp_path, content):
        """Anything we can't fully validate is treated as no cache at all."""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        write(cache_dir / CACHE_FILENAME, content)
        cache = LintCache(str(cache_dir), make_config(project))
        cache.load()
        assert cache._entries == {}

    def test_persist_writes_a_loadable_file(self, project, tmp_path):
        """A persisted cache reloads with the same entries."""
        cache_dir = str(tmp_path / "cache")
        target = write(project / "a.sql", CLEAN_SQL)
        cache = LintCache(cache_dir, make_config(project))
        assert cache.check(target) is None
        cache.record(target, {"source_chars": 1})
        cache.persist()

        reloaded = LintCache(cache_dir, make_config(project))
        reloaded.load()
        assert reloaded.check(target) is not None

    def test_persist_writes_a_gitignore(self, project, tmp_path):
        """The cache directory ignores itself, so it can't be committed."""
        cache_dir = tmp_path / "cache"
        cache = LintCache(str(cache_dir), make_config(project))
        cache.persist()
        assert (cache_dir / ".gitignore").read_text(encoding="utf-8").endswith("*\n")

    def test_no_gitignore_in_a_directory_we_did_not_create(self, project, tmp_path):
        """A pre-existing `cache_dir` is not silently made git-ignored.

        Regression test. `cache_dir` is user-configurable and may point at a
        directory which already holds other things; writing a `.gitignore`
        containing `*` there would hide the user's own untracked files.
        """
        cache_dir = tmp_path / "existing"
        cache_dir.mkdir()
        write(cache_dir / "something_of_theirs.txt", "keep me")
        cache = LintCache(str(cache_dir), make_config(project))
        cache.persist()
        assert (cache_dir / CACHE_FILENAME).exists()
        assert not (cache_dir / ".gitignore").exists()

    def test_persist_leaves_no_temporary_files(self, project, tmp_path):
        """The atomic write cleans up after itself."""
        cache_dir = tmp_path / "cache"
        cache = LintCache(str(cache_dir), make_config(project))
        cache.persist()
        assert sorted(os.listdir(cache_dir)) == [".gitignore", CACHE_FILENAME]

    def test_persist_prunes_expired_entries(self, project, tmp_path):
        """Entries which haven't been seen for a long time are dropped.

        Without this the file grows forever as files are renamed or deleted.
        """
        cache_dir = tmp_path / "cache"
        cache = LintCache(str(cache_dir), make_config(project))
        cache._entries["stale"] = {
            "key": "k",
            "statistics": dict(VALID_ENTRY["statistics"]),
            "last_seen": int(time.time()) - ENTRY_TTL_SECONDS - 10,
        }
        cache._entries["fresh"] = {
            "key": "k",
            "statistics": dict(VALID_ENTRY["statistics"]),
            "last_seen": int(time.time()),
        }
        cache.persist()
        payload = json.loads((cache_dir / CACHE_FILENAME).read_text(encoding="utf-8"))
        assert list(payload["entries"]) == ["fresh"]

    def test_persist_survives_an_unwritable_directory(
        self, project, tmp_path, monkeypatch
    ):
        """A cache we can't write is a warning, never a failure.

        Read-only checkouts and locked-down CI images are both real, and
        neither should stop a lint run.
        """
        cache_dir = tmp_path / "cache"
        cache = LintCache(str(cache_dir), make_config(project))

        def _boom(*args, **kwargs):
            raise OSError("read-only file system")

        # Creating the directory is the first thing `persist` does, so this is
        # where a read-only location actually fails.
        monkeypatch.setattr("sqlfluff.core.linter.cache.os.makedirs", _boom)
        cache.persist()
        assert cache._writable is False
        assert not cache_dir.exists()
        # A second attempt is skipped rather than retried.
        cache.persist()

    def test_hit_refreshes_last_seen(self, project, tmp_path):
        """An actively used entry is never aged out."""
        cache_dir = str(tmp_path / "cache")
        target = write(project / "a.sql", CLEAN_SQL)
        cache = LintCache(cache_dir, make_config(project))
        cache.check(target)
        cache.record(target, {"source_chars": 1})
        entry = next(iter(cache._entries.values()))
        entry["last_seen"] = int(time.time()) - ENTRY_TTL_SECONDS - 10
        assert cache.check(target) is not None
        assert entry["last_seen"] > int(time.time()) - 10


# ###
# Unit tests: check and record
# ###


class TestCheckAndRecord:
    """The narrow contract between the cache and the linter."""

    def test_record_without_check_is_ignored(self, project, tmp_path):
        """We never invent a key we didn't compute before linting.

        The key has to describe the contents we read *before* the file was
        linted; deriving it afterwards would race with anything that rewrote
        the file in between.
        """
        target = write(project / "a.sql", CLEAN_SQL)
        cache = LintCache(str(tmp_path / "cache"), make_config(project))
        cache.record(target, {"source_chars": 1})
        assert cache._entries == {}

    def test_check_counts_hits_and_misses(self, project, tmp_path):
        """Hit and miss counters track what actually happened."""
        target = write(project / "a.sql", CLEAN_SQL)
        cache = LintCache(str(tmp_path / "cache"), make_config(project))
        assert cache.check(target) is None
        cache.record(target, {"source_chars": 1})
        assert cache.check(target) is not None
        assert (cache.hits, cache.misses) == (1, 1)

    def test_check_returns_a_copy(self, project, tmp_path):
        """A caller mutating the returned statistics can't corrupt the cache."""
        target = write(project / "a.sql", CLEAN_SQL)
        cache = LintCache(str(tmp_path / "cache"), make_config(project))
        cache.check(target)
        cache.record(target, dict(VALID_ENTRY["statistics"]))
        returned = cache.check(target)
        assert returned is not None
        returned["source_chars"] = -1
        assert cache.check(target)["source_chars"] == 1

    def test_file_changed_during_the_run_is_not_recorded(self, project, tmp_path):
        """A file edited mid-run is not recorded against either version.

        The key is taken before linting and the result arrives afterwards. If
        the file changed in between, neither the old key nor the new one is
        backed by a lint of those exact contents, so recording either would be
        an unverified claim. This is the check that closes that window.
        """
        target = project / "a.sql"
        write(target, CLEAN_SQL)
        cache = LintCache(str(tmp_path / "cache"), make_config(project))
        assert cache.check(str(target)) is None
        # Simulate an edit landing while the linter was working on it.
        write(target, DIRTY_SQL)
        cache.record(str(target), dict(VALID_ENTRY["statistics"]))
        assert cache._entries == {}

    def test_pending_keys_are_released_for_uncacheable_files(self, project):
        """A file which will never be recorded doesn't hold its key.

        Regression test. `check` retains a key for every miss so that `record`
        can verify it. On a project where most files have violations -- the
        projects that get no benefit from the cache in the first place --
        holding one key per file for the whole run is wasted memory.
        """
        write(project / "clean.sql", CLEAN_SQL)
        write(project / "dirty.sql", DIRTY_SQL)
        linter = Linter(config=make_config(project))
        linter.lint_paths((str(project),))
        # Both files missed, but only the clean one is kept as an entry and
        # neither is left dangling in the pending map.
        cache = LintCache.from_config(make_config(project))
        assert cache is not None
        assert len(cache._entries) == 1
        assert cache._pending_keys == {}

    def test_missing_file_is_not_keyable(self, project, tmp_path):
        """A file which disappeared is a miss, not an exception."""
        cache = LintCache(str(tmp_path / "cache"), make_config(project))
        assert cache.check(str(project / "gone.sql")) is None

    def test_templater_opt_out_disables_keying(self, project, tmp_path, monkeypatch):
        """A templater returning None means no key and therefore no caching."""
        monkeypatch.setattr(
            JinjaTemplater, "cache_fingerprint", lambda self, config: None
        )
        target = write(project / "a.sql", CLEAN_SQL)
        cache = LintCache(str(tmp_path / "cache"), make_config(project))
        assert cache.check(target) is None
        cache.record(target, {"source_chars": 1})
        assert cache._entries == {}

    def test_templater_fingerprint_is_memoised_per_run(
        self, project, tmp_path, monkeypatch
    ):
        """Files sharing a config only fingerprint the templater once.

        Fingerprinting walks whole directory trees, so doing it per file would
        make the cache slower than the linting it replaces on large projects.
        """
        calls = []

        def _counting_fingerprint(self, config):
            calls.append(1)
            return ""

        monkeypatch.setattr(JinjaTemplater, "cache_fingerprint", _counting_fingerprint)
        cache = LintCache(str(tmp_path / "cache"), make_config(project))
        for name in ("a.sql", "b.sql", "c.sql"):
            cache.check(write(project / name, CLEAN_SQL))
        assert len(calls) == 1

    def test_config_is_resolved_once_per_directory(self, project, monkeypatch):
        """Files in one directory share a single config resolution.

        `make_child_from_path` builds a whole `FluffConfig`, expanding a fresh
        dialect object each time -- tens of milliseconds. Doing that per file
        costs more than the linting a hit avoids, so this is load bearing
        rather than a micro-optimisation.
        """
        calls = []
        original = FluffConfig.make_child_from_path

        def _counting(self, path, *args, **kwargs):
            calls.append(path)
            return original(self, path, *args, **kwargs)

        monkeypatch.setattr(FluffConfig, "make_child_from_path", _counting)
        cache = LintCache(str(project.parent / "cache"), make_config(project))
        for name in ("a.sql", "b.sql", "c.sql"):
            cache.check(write(project / name, CLEAN_SQL))
        assert len(calls) == 1

    def test_resolved_configs_are_not_retained(self, project):
        """The memo keeps derived strings, not `FluffConfig` objects.

        Each config holds a freshly expanded dialect. Pinning one per directory
        for the length of the run would trade the time saved for a lot of
        memory on a project with many directories.
        """
        cache = LintCache(str(project.parent / "cache"), make_config(project))
        cache.check(write(project / "a.sql", CLEAN_SQL))
        assert cache._directory_keys
        for value in cache._directory_keys.values():
            assert value is None or all(isinstance(part, str) for part in value)

    def test_config_is_resolved_per_directory_not_globally(self, project):
        """Subdirectories with their own config still get their own key.

        Memoising by directory must not let a nested `.sqlfluff` be missed.
        """
        rewrite_config(
            project / "sub",
            "[sqlfluff]\n[sqlfluff:rules:capitalisation.keywords]\n"
            "capitalisation_policy = lower\n",
        )
        cache = LintCache(str(project.parent / "cache"), make_config(project))
        top = cache._file_key(write(project / "a.sql", CLEAN_SQL))
        nested = cache._file_key(write(project / "sub" / "a.sql", CLEAN_SQL))
        assert top is not None
        assert nested is not None
        assert top != nested


# ###
# Templater declarations
# ###


class UnknownTemplater(RawTemplater):
    """A stand-in for a templater SQLFluff doesn't ship."""

    name = "unknown"


class DerivedJinjaTemplater(JinjaTemplater):
    """A stand-in for a templater which renders through a project.

    `DbtTemplater` and `SQLMeshTemplater` are both real examples.
    """

    name = "derived_jinja"


def test__templater_jinja_is_cacheable(project):
    """The Jinja templater declares the paths it reads."""
    config = make_config(project)
    templater = config.get("templater_obj")
    assert isinstance(templater, JinjaTemplater)
    assert templater.cache_fingerprint(config) is not None


def test__templater_jinja_subclass_is_not_cacheable(project):
    """A subclass of `JinjaTemplater` does not inherit the opt-in.

    Regression test. The Jinja declaration covers what *Jinja* reads; a
    subclass which renders through a project reads a great deal more --
    SQLMesh loads project context, dbt a compiled manifest. Inheriting an
    opt-in that was never made for you is exactly how a stale hit hides a
    real violation.
    """
    assert DerivedJinjaTemplater().cache_fingerprint(make_config(project)) is None


def test__templater_raw_is_cacheable():
    """The raw templater reads nothing outside the file."""
    assert RawTemplater().cache_fingerprint(None) == ""


def test__templater_unknown_subclass_is_not_cacheable():
    """A templater we don't control opts out until it says otherwise.

    This is the safe default: we cannot know what external state a third party
    templater reads, and guessing wrong means silently skipping a file which
    should have reported a violation.
    """
    assert UnknownTemplater().cache_fingerprint(None) is None


@pytest.mark.parametrize("templater", [PythonTemplater(), PlaceholderTemplater()])
def test__templater_config_only_templaters_are_cacheable(templater):
    """Templaters whose whole context is config declare no external state."""
    assert templater.cache_fingerprint(None) == ""


class TestJinjaFingerprint:
    """The Jinja templater's declaration of what it reads from disk."""

    def _config(self, project, **section):
        body = "[sqlfluff]\ndialect = ansi\n[sqlfluff:templater:jinja]\n"
        body += "".join(f"{k} = {v}\n" for k, v in section.items())
        rewrite_config(project, body)
        return make_config(project)

    def test_no_paths_configured(self, project):
        """With nothing configured the fingerprint is still stable."""
        config = self._config(project)
        templater = config.get("templater_obj")
        assert templater.cache_fingerprint(config) == templater.cache_fingerprint(
            config
        )

    @pytest.mark.parametrize(
        "setting",
        [
            "load_macros_from_path",
            "exclude_macros_from_path",
            "loader_search_path",
            "library_path",
        ],
    )
    def test_reacts_to_content_of_each_configured_path(self, project, setting):
        """Editing a file under any configured path changes the fingerprint.

        All four settings feed the Jinja environment, so all four have to be
        covered; missing one would let a macro edit go unnoticed.
        """
        macro_dir = project / "macros"
        write(macro_dir / "m.sql", "{% macro f() %}1{% endmacro %}")
        config = self._config(project, **{setting: "macros"})
        templater = config.get("templater_obj")
        before = templater.cache_fingerprint(config)
        write(macro_dir / "m.sql", "{% macro f() %}2{% endmacro %}")
        assert templater.cache_fingerprint(config) != before

    def test_reacts_to_a_new_macro_file(self, project):
        """Adding a macro file changes the fingerprint."""
        write(project / "macros" / "m.sql", "{% macro f() %}1{% endmacro %}")
        config = self._config(project, load_macros_from_path="macros")
        templater = config.get("templater_obj")
        before = templater.cache_fingerprint(config)
        write(project / "macros" / "n.sql", "{% macro g() %}2{% endmacro %}")
        assert templater.cache_fingerprint(config) != before


# ###
# Integration: linting a project twice
# ###


class TestLintPathsIntegration:
    """End to end behaviour through `Linter.lint_paths`."""

    def test_disabled_by_default(self, project):
        """Nothing is cached and no directory appears unless asked for."""
        write(project / "a.sql", CLEAN_SQL)
        config = FluffConfig.from_path(str(project), overrides={"dialect": "ansi"})
        assert lint(project, config).files_cached == 0

    def test_path_with_no_sql_writes_nothing(self, project, tmp_path):
        """A path containing no SQL doesn't even open the cache.

        Building one reads the cache file and enumerates installed plugins,
        which is measurable and pointless when there is nothing to lint.
        """
        cache_dir = tmp_path / "cache"
        result = lint(project, make_config(project, cache_dir=cache_dir))
        assert result.files_cached == 0
        assert not cache_dir.exists()

    def test_clean_file_is_skipped_on_the_second_run(self, project):
        """The headline behaviour."""
        write(project / "a.sql", CLEAN_SQL)
        assert lint(project, make_config(project)).files_cached == 0
        assert lint(project, make_config(project)).files_cached == 1

    def test_dirty_file_is_never_skipped(self, project):
        """A file with violations is re-linted every time.

        If it were cached the user would stop being told about the violation.
        """
        write(project / "a.sql", DIRTY_SQL)
        first = lint(project, make_config(project))
        second = lint(project, make_config(project))
        assert second.files_cached == 0
        assert len(second.get_violations()) == len(first.get_violations())

    def test_mixed_project_only_skips_the_clean_files(self, project):
        """Clean and dirty files in one run are partitioned correctly."""
        write(project / "clean.sql", CLEAN_SQL)
        write(project / "dirty.sql", DIRTY_SQL)
        lint(project, make_config(project))
        second = lint(project, make_config(project))
        assert second.files_cached == 1
        assert [v.rule_code() for v in second.get_violations()]

    def test_editing_a_file_invalidates_it(self, project):
        """A changed file is linted again."""
        target = project / "a.sql"
        write(target, CLEAN_SQL)
        lint(project, make_config(project))
        write(target, DIRTY_SQL)
        result = lint(project, make_config(project))
        assert result.files_cached == 0
        assert result.get_violations()

    def test_reverting_a_file_hits_the_old_entry(self, project):
        """An entry stays valid for content it was recorded against.

        Entries are keyed by content, not by path alone, so a revert is a hit
        rather than a miss.
        """
        target = project / "a.sql"
        write(target, CLEAN_SQL)
        lint(project, make_config(project))
        write(target, DIRTY_SQL)
        lint(project, make_config(project))
        write(target, CLEAN_SQL)
        assert lint(project, make_config(project)).files_cached == 1

    def test_changing_config_invalidates(self, project):
        """A config change re-lints everything it applies to."""
        write(project / "a.sql", CLEAN_SQL)
        lint(project, make_config(project))
        rewrite_config(
            project,
            "[sqlfluff]\ndialect = ansi\n"
            "[sqlfluff:rules:capitalisation.keywords]\ncapitalisation_policy = lower\n",
        )
        result = lint(project, make_config(project))
        assert result.files_cached == 0
        assert result.get_violations()

    def test_changing_an_override_invalidates(self, project):
        """CLI overrides are part of the key, not just files on disk."""
        write(project / "a.sql", CLEAN_SQL)
        lint(project, make_config(project))
        assert lint(project, make_config(project, rules="LT01")).files_cached == 0

    def test_changing_the_run_fingerprint_invalidates(self, project, monkeypatch):
        """Upgrading SQLFluff throws the whole cache away."""
        write(project / "a.sql", CLEAN_SQL)
        lint(project, make_config(project))
        monkeypatch.setattr(
            "sqlfluff.core.linter.cache._get_sqlfluff_version", lambda: "0.0.0-test"
        )
        assert lint(project, make_config(project)).files_cached == 0

    def test_changing_a_macro_invalidates(self, project):
        """Editing a macro re-lints every file which could have used it.

        This is the case a naive content hash gets wrong: the SQL file is
        untouched, but what it renders to has changed.
        """
        write(project / "macros" / "m.sql", "{% macro f() %}a{% endmacro %}")
        write(
            project / ".sqlfluff",
            "[sqlfluff]\ndialect = ansi\n"
            "[sqlfluff:templater:jinja]\nload_macros_from_path = macros\n",
        )
        write(project / "a.sql", "SELECT {{ f() }}\nFROM tbl\n")
        lint(project, make_config(project))
        assert lint(project, make_config(project)).files_cached == 1
        write(project / "macros" / "m.sql", "{% macro f() %}b{% endmacro %}")
        assert lint(project, make_config(project)).files_cached == 0

    def test_templater_opt_out_disables_caching(self, project, monkeypatch):
        """A templater which declines is never cached, however clean the file.

        This is what keeps dbt projects out of the cache.
        """
        monkeypatch.setattr(
            JinjaTemplater, "cache_fingerprint", lambda self, config: None
        )
        write(project / "a.sql", CLEAN_SQL)
        lint(project, make_config(project))
        assert lint(project, make_config(project)).files_cached == 0

    def test_corrupt_cache_file_is_ignored(self, project, tmp_path):
        """A damaged cache costs a slow run, not a failed one."""
        cache_dir = tmp_path / "cache"
        write(project / "a.sql", CLEAN_SQL)
        lint(project, make_config(project, cache_dir=cache_dir))
        write(cache_dir / CACHE_FILENAME, "{ truncated")
        assert (
            lint(project, make_config(project, cache_dir=cache_dir)).files_cached == 0
        )

    def test_cache_file_has_the_expected_shape(self, project, tmp_path):
        """The on-disk format is versioned and fingerprinted."""
        cache_dir = tmp_path / "cache"
        write(project / "a.sql", CLEAN_SQL)
        lint(project, make_config(project, cache_dir=cache_dir))
        payload = json.loads((cache_dir / CACHE_FILENAME).read_text(encoding="utf-8"))
        assert payload["schema_version"] == CACHE_SCHEMA_VERSION
        assert payload["run_fingerprint"] == run_fingerprint()
        assert len(payload["entries"]) == 1


class TestOutputParity:
    """A cached run has to report the same thing as an uncached one."""

    def _records(self, result):
        """Records with timings dropped.

        Timings are deliberately *not* replayed: reporting the cost of work
        which didn't happen would make `--persist-timing` misleading.
        """
        return [
            {k: v for k, v in record.items() if k != "timings"}
            for record in result.as_records()
        ]

    def test_records_match(self, project):
        """Serialised records are identical apart from timings."""
        write(project / "clean.sql", CLEAN_SQL)
        write(project / "dirty.sql", DIRTY_SQL)
        uncached = lint(project, make_config(project, cache=False))
        lint(project, make_config(project))
        cached = lint(project, make_config(project))
        assert cached.files_cached == 1
        assert self._records(cached) == self._records(uncached)

    def test_statistics_are_replayed(self, project):
        """Character and segment counts survive a cache hit.

        They are pure functions of the file and its config, so the same key
        implies the same statistics.
        """
        write(project / "a.sql", CLEAN_SQL)
        uncached = lint(project, make_config(project, cache=False))
        lint(project, make_config(project))
        cached = lint(project, make_config(project))
        assert cached.files_cached == 1
        assert (
            cached.as_records()[0]["statistics"]
            == uncached.as_records()[0]["statistics"]
        )

    def test_timings_are_empty_for_a_cached_file(self, project):
        """No work happened, so no time is reported for it."""
        write(project / "a.sql", CLEAN_SQL)
        lint(project, make_config(project))
        cached = lint(project, make_config(project))
        assert cached.as_records()[0]["timings"] == {}

    def test_counts_match(self, project):
        """File and cleanliness counts are unaffected by caching."""
        write(project / "clean.sql", CLEAN_SQL)
        write(project / "dirty.sql", DIRTY_SQL)
        uncached = lint(project, make_config(project, cache=False))
        lint(project, make_config(project))
        cached = lint(project, make_config(project))
        assert cached.stats(1, 0) == uncached.stats(1, 0)

    def test_exit_status_matches(self, project):
        """A run which is entirely cache hits still passes."""
        write(project / "a.sql", CLEAN_SQL)
        lint(project, make_config(project))
        cached = lint(project, make_config(project))
        assert cached.stats(1, 0)["status"] == "PASS"


class TestNoqaInteraction:
    """`noqa` comments change what a file reports without changing its rules."""

    def test_fully_suppressed_file_is_cached(self, project):
        """A file whose violations are all masked by noqa reports nothing.

        Caching it is safe rather than merely convenient: the `noqa` comment
        is part of the file, so removing it changes the key.
        """
        target = project / "a.sql"
        write(target, "select  a,b from tbl  -- noqa\n")
        lint(project, make_config(project))
        assert lint(project, make_config(project)).files_cached == 1

    def test_removing_a_noqa_re_reports(self, project):
        """Deleting the suppression brings the violations back."""
        target = project / "a.sql"
        write(target, "select  a,b from tbl  -- noqa\n")
        lint(project, make_config(project))
        write(target, DIRTY_SQL)
        result = lint(project, make_config(project))
        assert result.files_cached == 0
        assert result.get_violations()

    def test_unused_noqa_is_not_cached(self, project):
        """A file whose only finding is an unused noqa is not cached.

        Those warnings are generated from the ignore mask on demand rather than
        stored on the file, so a naive "no violations" test would call this
        file clean and lose the warning on the next run.
        """
        write(project / "a.sql", "SELECT\n    a,\n    b\nFROM tbl  -- noqa: LT02\n")
        lint(project, make_config(project, warn_unused_ignores=True))
        result = lint(project, make_config(project, warn_unused_ignores=True))
        assert result.files_cached == 0


class TestFixInteraction:
    """Caching has to behave under `fix`, which rewrites files."""

    def test_fixed_file_is_cached_on_the_next_run(self, project):
        """After a fix the new contents are keyed, not the old ones."""
        target = project / "a.sql"
        write(target, DIRTY_SQL)
        Linter(config=make_config(project)).lint_paths(
            (str(project),), fix=True, apply_fixes=True
        )
        # The file has been rewritten, so the first pass over the new contents
        # is a miss...
        assert lint(project, make_config(project)).files_cached == 0
        # ...and the second is a hit.
        assert lint(project, make_config(project)).files_cached == 1

    def test_unfixable_file_is_never_cached(self, project):
        """A file left with violations after fixing keeps being reported."""
        write(project / "a.sql", "SELECT DISTINCT(a)\nFROM tbl\n")
        for _ in range(2):
            result = Linter(config=make_config(project)).lint_paths(
                (str(project),), fix=True, apply_fixes=True
            )
        assert result.files_cached == 0


class TestLintedDirBookkeeping:
    """A cached file has no `LintedFile`, so the metadata has to stand alone."""

    def test_records_exist_without_files(self, project):
        """Records and counts are present even though `.files` is empty."""
        write(project / "a.sql", CLEAN_SQL)
        lint(project, make_config(project))
        cached = lint(project, make_config(project))
        linted_dir = cached.paths[0]
        assert linted_dir.files == []
        assert len(linted_dir.as_records()) == 1
        assert linted_dir.stats() == {
            "files": 1,
            "clean": 1,
            "unclean": 0,
            "violations": 0,
        }

    def test_discarding_fixes_does_not_trip_over_a_cached_record(self, project):
        """The tmp/prs error map is populated for cached records too.

        `discard_fixes_for_lint_errors_in_files_with_tmp_or_prs_errors` indexes
        that map by the filepath of every record, so a cached record with no
        entry would raise a KeyError.
        """
        write(project / "clean.sql", CLEAN_SQL)
        write(project / "broken.sql", "SELECT FROM FROM;\n")
        lint(project, make_config(project))
        cached = lint(project, make_config(project))
        assert cached.files_cached == 1
        cached.discard_fixes_for_lint_errors_in_files_with_tmp_or_prs_errors()


class TestParallel:
    """Caching is a main-process concern, but it has to survive workers."""

    def test_cache_works_with_multiple_processes(self, project):
        """Files linted in worker processes are still cached afterwards.

        The runner returns `LintedFile` objects to the main process, which is
        where recording happens, so no coordination between workers is needed.
        This test exists to keep that true.
        """
        for name in ("a.sql", "b.sql", "c.sql"):
            write(project / name, CLEAN_SQL)
        config = make_config(project, processes=2)
        assert lint(project, config).files_cached == 0
        assert lint(project, make_config(project, processes=2)).files_cached == 3


# ###
# CLI
# ###


class TestCli:
    """The flags which turn caching on and point it somewhere."""

    @staticmethod
    def _lint_cli(project_root, *extra):
        return invoke_assert_code(
            ret_code=0,
            args=[lint_command, [str(project_root), "--dialect", "ansi", *extra]],
        )

    def test_no_cache_directory_without_the_flag(self, project, tmp_path):
        """Caching stays off unless asked for, so nothing appears on disk."""
        write(project / "a.sql", CLEAN_SQL)
        self._lint_cli(project, "--cache-dir", str(tmp_path / "cache"))
        assert not (tmp_path / "cache").exists()

    def test_cache_flag_creates_the_cache(self, project, tmp_path):
        """`--cache` writes a cache in the requested directory."""
        write(project / "a.sql", CLEAN_SQL)
        cache_dir = tmp_path / "cache"
        self._lint_cli(project, "--cache", "--cache-dir", str(cache_dir))
        assert (cache_dir / CACHE_FILENAME).exists()

    def test_config_alone_enables_caching(self, project, tmp_path, monkeypatch):
        """No flag is needed if the root config asks for a cache.

        Like `processes`, this is a run-level setting read from the root
        config, so the test runs from inside the project rather than pointing
        at it from outside.
        """
        cache_dir = tmp_path / "cache"
        rewrite_config(
            project,
            f"[sqlfluff]\ndialect = ansi\ncache = True\n"
            f"cache_dir = {cache_dir.as_posix()}\n",
        )
        write(project / "a.sql", CLEAN_SQL)
        monkeypatch.chdir(project)
        self._lint_cli(project)
        assert (cache_dir / CACHE_FILENAME).exists()

    def test_no_cache_flag_beats_config(self, project, tmp_path, monkeypatch):
        """`--no-cache` overrides `cache = True` in the config file."""
        cache_dir = tmp_path / "cache"
        rewrite_config(
            project,
            f"[sqlfluff]\ndialect = ansi\ncache = True\n"
            f"cache_dir = {cache_dir.as_posix()}\n",
        )
        write(project / "a.sql", CLEAN_SQL)
        monkeypatch.chdir(project)
        self._lint_cli(project, "--no-cache")
        assert not cache_dir.exists()

    def test_relative_cache_dir_is_resolved_from_the_working_directory(
        self, tmp_path, monkeypatch
    ):
        """A relative `cache_dir` lands in the same place on every run.

        `cache_dir` ends in `_dir`, which the config loader would otherwise
        resolve relative to the *config file* -- but only once the directory
        exists, because resolution goes through `glob`. That would put the
        cache in one place on the first run and another on the second.

        The config therefore lives in a *parent* of the working directory, so
        the two candidate bases genuinely differ: resolving against the config
        file would give ``<tmp>/.sqlfluff_cache`` and against the working
        directory ``<tmp>/work/.sqlfluff_cache``. Running from the config's own
        directory would make both answers identical and prove nothing.
        """
        write(
            tmp_path / ".sqlfluff",
            "[sqlfluff]\ndialect = ansi\ncache = True\ncache_dir = .sqlfluff_cache\n",
        )
        clear_config_caches()
        work = tmp_path / "work"
        work.mkdir()
        write(work / "a.sql", CLEAN_SQL)
        monkeypatch.chdir(work)

        for _ in range(2):
            self._lint_cli(work)
            assert (work / ".sqlfluff_cache" / CACHE_FILENAME).exists()
            # Never beside the config file.
            assert not (tmp_path / ".sqlfluff_cache").exists()

    def test_second_run_reports_the_same_result(self, project, tmp_path):
        """A cached run produces the same output and exit code as the first."""
        cache_dir = str(tmp_path / "cache")
        write(project / "clean.sql", CLEAN_SQL)
        write(project / "dirty.sql", DIRTY_SQL)
        first = invoke_assert_code(
            ret_code=1,
            args=[
                lint_command,
                [
                    str(project),
                    "--dialect",
                    "ansi",
                    "--format",
                    "json",
                    "--cache",
                    "--cache-dir",
                    cache_dir,
                ],
            ],
        )
        second = invoke_assert_code(
            ret_code=1,
            args=[
                lint_command,
                [
                    str(project),
                    "--dialect",
                    "ansi",
                    "--format",
                    "json",
                    "--cache",
                    "--cache-dir",
                    cache_dir,
                ],
            ],
        )

        def _strip(output):
            return [
                {k: v for k, v in record.items() if k != "timings"}
                for record in json.loads(output)
            ]

        assert _strip(second.stdout) == _strip(first.stdout)

    def test_fix_accepts_the_flags(self, project, tmp_path):
        """`fix` takes the same options as `lint`."""
        cache_dir = tmp_path / "cache"
        write(project / "a.sql", DIRTY_SQL)
        invoke_assert_code(
            ret_code=0,
            args=[
                fix,
                [
                    str(project),
                    "--dialect",
                    "ansi",
                    "--cache",
                    "--cache-dir",
                    str(cache_dir),
                    "--disable-progress-bar",
                ],
            ],
        )
        assert (cache_dir / CACHE_FILENAME).exists()

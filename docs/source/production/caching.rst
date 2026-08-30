.. _caching:

Caching lint results
====================

Most of the time SQLFluff spends on a project goes on files which have not
changed. In a pre-commit hook or a tight edit-and-lint loop, that is nearly all
of them. SQLFluff can remember which files came back clean and skip them
entirely on the next run.

Caching is **off by default**. Turn it on for a single run with
:code:`--cache`, or for a project by setting it in config:

.. code-block:: cfg

    [sqlfluff]
    cache = True

.. code-block:: text

    sqlfluff lint --cache .
    sqlfluff fix --cache .

The cache lives in :code:`.sqlfluff_cache` in the working directory by default.
Use :code:`--cache-dir` or the :code:`cache_dir` config value to put it
somewhere else. A relative path is resolved from the working directory. If
*SQLFluff* creates the directory it also writes a :code:`.gitignore` into it,
so that the cache cannot be committed by accident; a directory which already
exists is left alone, in case it is somewhere you keep other things.

Like :code:`processes`, :code:`cache` and :code:`cache_dir` are read from the
*root* configuration for the run -- the config found from the working directory
-- rather than from a :code:`.sqlfluff` in a subdirectory.

To start again from scratch, delete the cache directory. There is no separate
command for it, and nothing else in a project depends on it.

What gets cached
----------------

Only files which produced **nothing at all**: no violations, no warnings, no
templating or parsing errors, and no unused :code:`-- noqa` comments. A file
with anything to report is linted again on every run, so enabling the cache can
never make a diagnostic disappear that you have not already dealt with.

That is a deliberately narrow rule, and it is where the benefit comes from: on
a project which is already passing, almost every file qualifies.

What invalidates an entry
-------------------------

An entry records that *a specific file, under a specific set of inputs, linted
clean*. It is only used again when all of those inputs match. Any of the
following makes a file get linted again:

* The file's contents change (its bytes are hashed, so a change of encoding
  counts too).
* Its resolved configuration changes -- including a :code:`.sqlfluff` higher up
  the tree, a :code:`pyproject.toml`, or a command line override such as
  :code:`--rules`.
* A file the templater reads changes. For the Jinja templater that means
  anything under :code:`load_macros_from_path`,
  :code:`exclude_macros_from_path`, :code:`loader_search_path` or
  :code:`library_path`: editing a macro re-lints every file which could have
  used it, and so does adding, removing or renaming one.
* The SQLFluff version changes.
* An installed SQLFluff plugin is added, removed or upgraded.

The last two discard the entire cache rather than individual entries, because
either can change the result for every file.

Caching is declined outright, rather than keyed, when a :class:`Linter` is
constructed with :code:`user_rules` from the Python API. Every other input has
a stable identity -- a file has its bytes, config its values, a plugin its
version -- but a rule class passed in-process has none: its name would not
change when its body did, so a cached clean result could hide an edited rule.

The cache also has to notice a macro reached through a symbolic link, so
directory fingerprinting follows links (with cycle protection) rather than
using the default non-following walk.

Which templaters can be cached
------------------------------

* :code:`raw` -- cached. It reads nothing outside the file.
* :code:`jinja` -- cached. The external files it reads are fingerprinted.
* :code:`python` -- cached. Its whole context comes from config.
* :code:`placeholder` -- cached. Its whole context comes from config.
* :code:`dbt` -- **not cached.**
* :code:`sqlmesh` -- **not cached.**
* Any third party templater -- **not cached**, unless it opts in (see below).

The opt-in is per *exact* class and is never inherited. A templater which
subclasses a cacheable one -- as both :code:`dbt` and :code:`sqlmesh` subclass
:code:`jinja` -- reads whatever its parent reads *and more*, so inheriting the
parent's declaration would be claiming something the subclass never verified.

dbt models are excluded because their rendering depends on the compiled
manifest -- other models, seeds, packages, the selected target, and any
:code:`env_var()` calls. None of that can be derived from the model file plus
its SQLFluff config, so there is no honest way to key it. Enabling
:code:`cache` in a dbt project is not an error; those files are simply always
linted.

Third party templaters are excluded by default for the same reason: SQLFluff
cannot know what external state a templater it did not write reads. A templater
opts in by implementing :code:`cache_fingerprint`:

.. code-block:: python

    from typing import Optional

    from sqlfluff.core.config import FluffConfig
    from sqlfluff.core.helpers.hashing import hash_path_contents
    from sqlfluff.core.templaters import RawTemplater


    class MyTemplater(RawTemplater):
        name = "my_templater"

        def cache_fingerprint(self, config: FluffConfig) -> Optional[str]:
            """Digest the state this templater reads from outside the file."""
            # Return "" if there is no such state, a digest of it if there is,
            # or None to decline caching entirely.
            return hash_path_contents([config.get("my_templater_path")])

Using the cache in CI
---------------------

.. warning::

    Treat the cache directory as being exactly as trusted as your working
    tree. An entry is a stored assertion that a file was clean, and *SQLFluff*
    acts on it without re-checking. Anyone who can write to the cache can
    therefore make a file be skipped.

    That is unremarkable locally -- someone who can write your cache can also
    write your SQL -- but it matters if you restore the cache in CI with
    something like ``actions/cache``. A cache key shared with pull requests
    from forks means an untrusted branch can save a cache that a later run on
    a trusted branch restores, silently suppressing findings.

    If you cache the directory in CI, scope the cache key so that untrusted
    branches cannot write an entry a trusted run will read. If you cannot,
    don't restore it.

Caveats
-------

* **Timings are not replayed.** A cached file reports no timing information in
  :code:`--format json` or :code:`--persist-timing`, because no work happened.
  Everything else, including the character and segment statistics, is identical
  to an uncached run.
* **There is no parse tree for a cached file.** Code using the Python API which
  reads :code:`LintedDir.files` or :code:`.tree` will not see cached files, for
  the same reason. Leave caching off in that case.
* **Concurrent runs are safe but not co-operative.** The cache file is replaced
  atomically, so a reader always sees a complete file. Two runs finishing at
  once resolve as last-writer-wins, which costs a cache miss on the next run
  and nothing else.
* **Keep the fingerprinted directories small.** The Jinja fingerprint hashes
  everything under the configured macro, loader and library paths on every run.
  Pointing :code:`loader_search_path` at a large tree makes that hashing cost
  more than the linting it saves.
* **The cache is a local build artefact.** It records absolute paths and is
  keyed to the installed SQLFluff and plugin versions. Don't commit it or share
  it between machines.
* **A broken cache is never fatal.** A cache which cannot be read, parsed or
  validated is discarded, and one which cannot be written produces a warning.
  Either way the run proceeds normally, just without the speedup.

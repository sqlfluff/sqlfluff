# Developing Rules

`Rules` in `SQLFluff` are implemented as classes inheriting from `BaseRule`.
SQLFluff crawls through the parse tree of a SQL file, calling the rule's
`_eval()` function for each segment in the tree. For many rules, this allows
the rule code to be really streamlined and only contain the logic for the rule
itself, with all the other mechanics abstracted away.

## Running Tests

The majority of the test cases for most bundled rules are *"yaml test cases"*,
i.e. test cases defined in [yaml](https://yaml.org/) files. You can find those [yaml fixtures on github](https://github.com/sqlfluff/sqlfluff/tree/main/test/fixtures/rules/std_rule_cases).
While this provides a very simple way to *write* tests, it can be occasionally tedious
to *run* specific tests.

Within either a `tox` environment or `virtualenv` (as described in the [contributing.md](https://github.com/sqlfluff/sqlfluff/blob/main/CONTRIBUTING.md)
file), you can either run all of the rule yaml tests with:

```sh
pytest test/rules/yaml_test_cases_test.py -vv
```

...or to just run tests for a specific rule, there are two options for a syntax to select
only those tests:

```sh
pytest -vv test/rules/ -k RF01
```

The `-k` option simply searches for the content of the argument being in the name
of the test, which will match any single or combo tests for that rule. By convention,
any test cases for a rule should include the code for that rule.

## Flagging Fixes That May Change the Meaning

A fix should change how a query is written, not what it does. `utils/fix_safety.py`
looks for fixes that may break this in the dialect fixtures. For each statement, it
runs `sqlfluff fix` and asks the database's own parser (an *oracle*) for the
statement's syntax tree before and after the fix. If the trees differ, or the database
can't parse the fixed statement, the fix is flagged, and the statement is fixed again
with one rule at a time to try to name the rules that did it.

A flagged fix needs a person to look at it, because two different trees can still mean
the same thing: `schema.table.column` and `table.column` differ, but can name the same
column in PostgreSQL. And a fix that isn't flagged isn't proven safe. The check only
sees:

- the statements in the fixtures, each on its own and without templating;
- the rules it fixes with, and their settings (see below);
- what the oracle's parser keeps: comments aren't in either tree, and DuckDB's
  `json_serialize_sql` only handles `SELECT` statements.

With `--rules`, the check fixes with exactly those rules. Otherwise it fixes with
every rule, or with the `rules` and `exclude_rules` of the `--config` file. The rule
settings are the defaults, or those of `--config`, which is the only config file read.

`test/fixtures/fix_safety/historical_corruptions.yml` holds the corrupted fixes from
closed `fix corrupts sql` issues, and what each oracle makes of them, misses included.

There are oracles for DuckDB and PostgreSQL ([pglast](https://pglast.readthedocs.io/),
PostgreSQL's own parser). The `fix-safety` tox environment installs them and checks
both dialects:

```sh
tox -e fix-safety
```

Arguments after `--` replace the default `--dialect duckdb --dialect postgres`.
Or run it directly, for some dialects, fixtures or rules, or with a config file:

```sh
python utils/fix_safety.py --dialect duckdb --dialect postgres
python utils/fix_safety.py --dialect postgres --filter "create_function*"
python utils/fix_safety.py --dialect postgres --rules CV11 --config my.sqlfluff
```

`utils/fix_safety_known_failures.yml` lists the fixes that a default run, without
`--rules` and `--config`, flags, each with the reason a person gave after looking at
it: a rewrite whose change is meant, like ST06 reordering the columns of a `SELECT`,
or a bug to fix. In a default run, listed fixes don't fail the check, and a listed
statement that's judged and passes does, so the list stays current: when you fix a
bug, remove its entry. With `--rules` or `--config`, the list isn't used, and every
flagged fix fails the check.

The check exits with:

- 1 when a fix was flagged that isn't listed, or, in a default run, a listed statement
  passes.
- 2 when the check couldn't judge all it should: a dialect has no oracle or its oracle
  isn't installed, no fixture file matches, a fixture file couldn't be parsed, fixing
  a statement raised or timed out (after 30 seconds, where there's `SIGALRM`, i.e. not
  on Windows), or the oracle could judge none of a dialect's statements. Usage errors
  and unexpected errors exit with 2 too.
- 0 when neither applies.

When both 1 and 2 apply, the exit code is 1.

## Rule State

One rule instance lints many files: the linter reuses it for every file whose
`rules` config, `rule_allowlist` and `rule_denylist` are the same, and files may
be linted at the same time on different threads. So don't keep per-file state
on `self`. Values that come from the rule's own `config_keywords` are fixed for
the instance and safe to cache. Anything else, such as core config
(`context.config`) or the dialect (`context.dialect`), must be read from the
`RuleContext` on each `_eval()` or `_eval_rust()` call. Keep working state for
that call in local variables.

## Traversal Options

### `crawl_behaviour`

Some rules are a poor fit for the simple traversal pattern described above.
Typical reasons include:

* The rule only looks at a small portion of the file (e.g. the beginning or
  end).
* The rule needs to traverse the parse tree in a non-standard way.

Each rule must provide a `crawl_behaviour` field, either directly or through
inheritance, which controls how the parse tree is traversed. Most rules use a
`SegmentSeekerCrawler`, which calls `_eval()` for every segment of the given
type(s). A rule that only needs to look at the whole file once can set
`crawl_behaviour = RootOnlyCrawler()` instead, so that `_eval()` is only called
*once*, with the root segment of the tree. This can be much more efficient,
especially on large files. For example, see rules `LT13` and `LT12`, which only
look at the beginning or end of the file, respectively. The available crawlers
are defined in `src/sqlfluff/core/rules/crawlers.py`.

### `_works_on_unparsable`

By default, `SQLFluff` calls `_eval()` for all segments, even "unparsable"
segments, i.e. segments that didn't match the parsing rules in the dialect.
This causes issues for some rules. If so, setting `_works_on_unparsable`
to `False` tells SQLFluff not to call `_eval()` for unparsable segments and
their descendants.

## Performance-related Options

These are other options a rule can set to make linting faster.

### `provide_raw_stack`

Some rules use the `RuleContext.raw_stack` property to access earlier segments
in the traversal. This can be useful, but it adds significant overhead to the
linting process, so it is not populated by default. A rule that needs it can
request it when defining its crawler by passing `provide_raw_stack=True`, for
example `crawl_behaviour = SegmentSeekerCrawler({"newline"},
provide_raw_stack=True)`.

### `lint_phase`

There are two phases of rule running.

1. The `main` phase is appropriate for most rules. These rules are assumed to
interact and potentially cause a cascade of fixes requiring multiple passes.
These rules run the `runaway_limit` number of times (default 10).

2. The `post` phase is for post-processing rules, not expected to trigger
any downstream rules, e.g. capitalization fixes. They are run in a
post-processing loop at the end. This loop is identical to the `main` loop,
but is only run 2 times at the end (once to fix, and once again to confirm no
remaining issues).

The two phases add complexity, but they also improve performance by allowing
SQLFluff to run fewer rules during the `main` phase, which often runs several
times.

::: tip NOTE
`post` rules also run on the *first* pass of the `main` phase so that
any issues they find will be presented in the list of issues output by
`sqlfluff fix` and `sqlfluff lint`.
:::

# Reference implementation validation

## Public Parquet integration

On Linux x86-64 and Python 3.12, built the public producer at
[`e7813a27b1d`](https://github.com/dataders/dbt-core/commit/e7813a27b1d)
as an ABI3 wheel and installed it into the consumer test environment.

- All 130 plugin tests passed, including five live producer integrations.
- The templater requests both `--generate-info-schema` and `--feature write_render_trace`.
- The new artifact contract test inspects actual
  `target/info_schema/v1/dbt.render_traces.parquet` files before the
  loader removes its temporary target. It checks signed 64-bit protocol,
  ingestion and offset fields; nested ordered events; and invocation identity.
  Loaded source, rendered SQL and event order match the producer rows exactly.
- Live source fixes, recompilation/idempotence, CLI persistence, disabled models
  and parallel workers run against that same wheel.
- Repository-wide pre-commit checks passed.

This verifies the producer/consumer artifact contract. The separate
[nested-loop LT02 fix cycle](https://github.com/dataders/sqlfluff-dbt2-indent-repro)
remains unresolved and is not covered by those capitalization-fix integrations.

## Historical JSON producer validation

Validated on Windows x86-64, Python 3.13.5, against the Python ABI3 wheel built
from dbt PR [#16870](https://github.com/dbt-labs/dbt/pull/16870), revision
`3116b949886d85aae646cc1479e7f703b88865d1` (including recursive-loop, include and super fixes,
and the subsequent CodeScene refactor).

## Checks

- Passed 101 ordinary consumer tests, four live integration tests and seven
  legacy-plugin version-selection tests (112 tests total).
- Passed the repository's complete pre-commit checks, including formatting,
  linting, type checking, spelling and YAML checks.
- Built the source distribution and a `py3-none-any` wheel. The wheel contains
  only the Python plugin and metadata, with no native runtime or renderer.
- Recorded 21 real runtime artifacts with `scripts/record_traces.py`.
  Only paths and invocation IDs are normalized for portability; event data,
  source and rendered output come directly from the upstream exporter.
- Python regression tests consume those artifacts without importing or running
  dbt. They check source coordinates, literal fixing, generated output,
  identical branches, loops, captures, macros, Unicode/CRLF, whitespace and noqa.
- Runtime invocation tests check the upstream feature flag, fresh target paths,
  CLI vars and manifest/source identity, and reject stale or ambiguous traces.
- Progress tests check compilation headers before runtime startup, one pair per
  batch, failure reporting, individual-file fallback and silent API calls.
  Real CLI tests exercise human, quiet and JSON output on success and failure;
  debug logging exposes captured dbt output and per-file trace reuse.
- Version-selection tests check both templaters' guidance and lazy import
  behavior, including dbt v2 prereleases and legacy Python dbt.
- The opt-in live tests compile the DuckDB fixture using the actual upstream
  build, checks a pre-injection trace with an ephemeral dependency, fixes source,
  recompiles idempotently and persists a source fix through the real SQLFluff CLI.
  A two-model pass, including elif, uses one real compile with two lint workers.
  A disabled model produces a skip warning without a templater error.
  Fixes also preserve the source's final newline when dbt strips it from a
  wholly literal model's rendered output.
  The review regression pass checks thirteen models with raw whitespace control,
  nested named blocks, empty/nonempty for/else and filtered loops using two
  workers, preserving tags, stripped whitespace and unexecuted source. It also
  checks nested break/continue, top-level returns and named-block returns.
  Generated output with no editable source origin is mapped conservatively, so
  it cannot become an insertion in the original source; surrounding proven
  literal spans remain fixable. Recursive direct/transformed output and empty
  child calls, including for/else, also preserve balanced layout and safe source
  fixes using explicit empty-loop closing events.

The debug runtime needed `RUST_LOG=debug` and `DBT_LOG_LEVEL=debug` in the test
environment. Those are inherited by child processes, not forced by the plugin.

## Limits

This is a tested consumer of the proposed artifact, not a claim that the
unreleased API is stable or that all Fusion/dbt v2 projects are supported.
Validation does not cover live warehouse introspection, all adapters,
product-specific factories, release builds or other operating systems.
The reference implementation deliberately rejects unsaved source and
unmappable inputs; snapshot rewriting, branch exploration and
broader compatibility coverage remains follow-up work.

# Reference implementation validation

Validated on Windows x86-64, Python 3.13.5, against the Python ABI3 wheel built
from dbt PR [#16870](https://github.com/dbt-labs/dbt/pull/16870), revision
`f18017bc7ca07f9d68f6316d06c4b9e580209b8b`.

## Checks

- Passed 55 ordinary consumer tests, seven legacy-plugin version-selection
  tests and the live integration test (63 tests total).
- Passed the repository's complete pre-commit checks, including formatting,
  linting, type checking, spelling and YAML checks.
- Built the source distribution and a `py3-none-any` wheel. The wheel contains
  only the Python plugin and metadata, with no native runtime or renderer.
- Recorded 14 real runtime artifacts with `scripts/record_traces.py`.
  Only paths and invocation IDs are normalized for portability; event data,
  source and rendered output come directly from the upstream exporter.
- Python regression tests consume those artifacts without importing or running
  dbt. They check source coordinates, literal fixing, generated output,
  identical branches, loops, captures, macros, Unicode/CRLF, whitespace and noqa.
- Runtime invocation tests check the upstream feature flag, fresh target paths,
  CLI vars and manifest/source identity, and reject stale or ambiguous traces.
- Version-selection tests check both templaters' guidance and lazy import
  behavior, including dbt v2 prereleases and legacy Python dbt.
- The opt-in live test compiles the DuckDB fixture using the actual upstream
  build, checks a pre-injection trace with an ephemeral dependency, fixes source,
  recompiles idempotently and persists a source fix through the real SQLFluff CLI.

The debug runtime needed `RUST_LOG=debug` and `DBT_LOG_LEVEL=debug` in the test
environment. Those are inherited by child processes, not forced by the plugin.

## Limits

This is a tested consumer of the proposed artifact, not a claim that the
unreleased API is stable or that all Fusion/dbt v2 projects are supported.
Validation does not cover live warehouse introspection, all adapters,
product-specific factories, release builds or other operating systems.
The reference implementation deliberately rejects unsaved source and
unmappable inputs; snapshot rewriting, disabled models, branch exploration and
project batching remain follow-up work.

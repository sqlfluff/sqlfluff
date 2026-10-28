# Experimental dbt v2 templater for SQLFluff

This is a reference consumer for the render-trace API proposed in
[dbt-labs/dbt#16870](https://github.com/dbt-labs/dbt/pull/16870). It shows how a
Python SQLFluff plugin can lint and fix original Jinja SQL using provenance from
dbt's actual Rust renderer.

**The upstream API is not released.** Installing a stock dbt v2 package is not
currently sufficient. Use a build of that PR to try this draft. This plugin
contains no dbt binary, Rust code, renderer patches or commit-specific runtime
checks.

## Choose the matching templater

| Runtime | Package | SQLFluff configuration |
| --- | --- | --- |
| Legacy Python dbt Core 1.x | `sqlfluff-templater-dbt` | `templater = dbt` |
| Rust dbt v2, with the proposed trace API | `sqlfluff-templater-dbt2` | `templater = dbt2` |

The [legacy templater](../sqlfluff-templater-dbt/README.md) cannot use Rust dbt's
Python namespace as if it contained the old compiler internals. Both plugins
report the correct package and configuration when the wrong generation is
selected. The legacy package also constrains its dependency to dbt Core 1.x.
Use the matching runtime in the environment where you install that plugin.

## Install and try the reference implementation

With a development install of this SQLFluff checkout active:

```sh
python -m pip install -e ./plugins/sqlfluff-templater-dbt2
```

Install a dbt-core wheel built from the upstream PR in the same Python
environment. [UPSTREAM.md](UPSTREAM.md) documents the tested revision and build
steps. The default invocation uses this interpreter's `dbt.cli.main.cli()` in a
child process, keeping dbt execution isolated from SQLFluff.

```ini
[sqlfluff]
templater = dbt2
dialect = duckdb

[sqlfluff:templater:dbt2]
project_dir = /absolute/path/to/project
profiles_dir = /absolute/path/to/profiles
# profile = my_profile
# target = dev
timeout = 300

# Optional: use a separately installed, trace-capable dbt CLI instead.
# runtime_path = /absolute/path/to/dbt

[sqlfluff:templater:dbt2:context]
some_variable = value
```

`context` is forwarded as dbt CLI vars. The selected runtime is responsible for
project semantics, packages, adapters and warehouse access. Compilation can make
introspective warehouse queries, as with the existing dbt templater.

```sh
sqlfluff lint path/to/model.sql
sqlfluff fix path/to/model.sql
```

The Python plugin intentionally does not declare a dependency on a released dbt
version that lacks the proposed exporter. Before publication, that requirement
must name the first upstream release shipping a supported trace API. The
eventual normal installation can then obtain the upstream runtime through pip.

## How the consumer works

1. Compile the selected models together once per lint pass with `--feature write_render_trace`, using fresh
   temporary target and log directories. Load the manifest and sidecars once,
   then serve per-file traces from memory after removing the temporary output.
2. Read the model's `*.render_trace.json` sidecar. Verify its source path, exact
   input, node identity and invocation against that compilation's manifest.
3. Validate protocol version, render stage, UTF-8 byte boundaries, literal
   equality and event coverage. Translate events into SQLFluff source slices.
4. Run SQLFluff's usual lexer, parser, rules and fixer on that `TemplatedFile`.

dbt performs all rendering and execution. Python only lexically classifies the
original Jinja source to account for source-only tags and skipped text. The
consumer never guesses an executed branch from identical output strings.
Repeated loop output can map to the same original source region. Generated
macro output remains nonliteral and is not eligible for direct source fixes.

The trace describes Jinja SQL **before ephemeral CTE injection**. The consumer
uses the trace's own `rendered` string, not the final compiled SQL file.
Unknown, stale, ambiguous or incomplete provenance is rejected.
Unbalanced Jinja layout is rejected before lexer work is dispatched, so malformed
traces from an older exporter produce templater errors instead of block-stack
panics in lint workers.

## Tests

Ordinary tests use 14 artifacts captured from the actual upstream PR runtime.
They require no dbt installation or Rust compiler:

```sh
python -m pytest plugins/sqlfluff-templater-dbt2/test
```

With a trace-capable dbt-core build installed, enable the live test:

```sh
# POSIX shell; in PowerShell use $env:SQLFLUFF_DBT2_INTEGRATION = "1".
SQLFLUFF_DBT2_INTEGRATION=1 python -m pytest plugins/sqlfluff-templater-dbt2/test/live_test.py
```

That test compiles a DuckDB project with config(), return(), ref(), loops and an
ephemeral parent; fixes the original source; recompiles to check idempotence;
and runs the real SQLFluff CLI to persist a source fix.

To regenerate recorded artifacts using that same installed runtime:

```sh
python plugins/sqlfluff-templater-dbt2/scripts/record_traces.py
```

See [VALIDATION.md](VALIDATION.md) for executed checks.

## Scope of this draft

This is a reference implementation, not a claim of Core-templater parity.
It requires current on-disk source. The normal CLI/lint-paths flow compiles all
selected files in one invocation and reuses those traces for that lint pass.
A new pass recompiles; changed per-file settings use a separate invocation,
and source edited after the batch is rejected. Direct process() calls outside
a lint pass compile individually.
Unsaved buffers, disabled models, source-rewritten snapshots and alternate
branch renders still need work. Broad adapter/warehouse and product-specific
Fusion compatibility remain unvalidated.

The upstream flag and schema are experimental. A stable upstream contract and
compatibility tests would let one plugin support multiple dbt releases by
protocol version, without carrying patched runtimes. See [OPTIONS.md](OPTIONS.md)
for the alternatives and [UPSTREAM.md](UPSTREAM.md) for interface assumptions.

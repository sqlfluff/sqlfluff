# Relationship to the upstream dbt contribution

This SQLFluff draft consumes the artifact proposed by
[dbt-labs/dbt#16870](https://github.com/dbt-labs/dbt/pull/16870). The producer is
implemented in dbt; this repository implements the consumer.

The tested producer revision is
[`f18017bc7`](https://github.com/alanmcruickshank/dbt/commit/f18017bc7ca07f9d68f6316d06c4b9e580209b8b),
based on upstream `4b4701c77`. It reports `dbt-oss 2.0.8`. A released binary
with the same version number does not contain the proposed feature merely
because its version matches. The revision identifies our validation build;
the plugin does not pin or inspect commit hashes.

## Build the prerequisite

Follow dbt's contributor setup for its Rust toolchain and Protocol Buffers
compiler, then build and install its Python distribution:

```sh
git clone https://github.com/alanmcruickshank/dbt.git
cd dbt
git checkout f18017bc7ca07f9d68f6316d06c4b9e580209b8b
python -m pip install maturin
python -m maturin build --manifest-path crates/dbt-sa-python/Cargo.toml --out dist
# Install the wheel produced above into the SQLFluff test environment:
python -m pip install /path/to/dbt/dist/dbt_core-<version>-<platform>.whl
```

These commands build dbt's own wheel, not a runtime bundled in this plugin.
For a standalone dbt CLI built from the same PR, configure `runtime_path`.

On our Windows debug build, both `RUST_LOG=debug` and `DBT_LOG_LEVEL=debug` were
needed to avoid an upstream tracing-initialization panic that also occurs
without trace export. Set these for local testing of that build. The plugin
inherits the caller's environment and does not force debug settings for users.
Release-build behavior has not been validated.

## Contract used by SQLFluff

The consumer invokes:

```sh
dbt compile --select path:models/example.sql --feature write_render_trace
```

The [producer's design notes](https://github.com/alanmcruickshank/dbt/blob/f18017bc7ca07f9d68f6316d06c4b9e580209b8b/docs/architecture/render-trace.md)
and [short JSON example](https://github.com/alanmcruickshank/dbt/blob/f18017bc7ca07f9d68f6316d06c4b9e580209b8b/crates/dbt-tasks-sa/tests/fixtures/render_trace/example.render_trace.json)
describe the format. SQLFluff depends on:

- Protocol version 1 and the `jinja_before_ephemeral_injection` render stage.
- Exact source and rendered strings, without applying source-rewriting offsets
  to a different file or applying pre-injection offsets to final compiled SQL.
- Ordered literal, expression, macro, layout and loop events with half-open
  UTF-8 byte ranges. Repeated source ranges and nested macro ranges are allowed.
- Source, model and invocation identity matching the freshly emitted manifest.
- A requested trace coming from a fresh render, even when compiled SQL is cached.

The Python adapter validates these assumptions before constructing writable
source mappings. It accepts compatible producer versions without an exact dbt
version or commit requirement; changes in the event vocabulary or semantics
must be explicitly supported before they can be used for fixing.

## What acceptance would and would not solve

If shipped as a supported upstream interface, this exporter would remove our
need to patch dbt or distribute native binaries. The plugin could be maintained
and released alongside SQLFluff. It would need a minimum trace-capable dbt
release and a tested protocol compatibility range.

Merging an experimental internal flag alone would not establish a stable
contract. Maintainers still need to agree versioning, invocation availability,
cache behavior, and event semantics. Older dbt versions would require an upgrade.

The current artifact does not map generated snapshot inputs back to original
definitions or explore unexecuted branches. Those require further upstream
provenance or separate consumer work. The Python-only test corpus demonstrates
useful source diagnostics and fixing; it does not establish full parity across
adapters, warehouses, platforms or product-specific execution factories.

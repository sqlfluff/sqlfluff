# Relationship to the upstream dbt contribution

This SQLFluff draft consumes the artifact proposed by
[dbt-labs/dbt#16870](https://github.com/dbt-labs/dbt/pull/16870). The producer is
implemented in dbt; this repository implements the consumer.

## Parquet producer

Use the [producer follow-up](https://github.com/alanmcruickshank/dbt/pull/1)
to dbt-labs/dbt#16870. The validated Parquet producer revision is
[`e7813a27b1d`](https://github.com/dataders/dbt-core/commit/e7813a27b1d).
It publishes protocol-v2 rows, including ingestion timestamps, to
`target/info_schema/v1/dbt.render_traces.parquet`.
A stock released dbt build does not provide this experimental API.
The plugin selects compatibility by protocol, not commit hash or version label.

## Build the prerequisite

Follow dbt's contributor prerequisites, including its Rust toolchain and
Protocol Buffers compiler (`protoc`). Check `protoc --version` before building.
Then build the public producer and install its wheel into the SQLFluff environment:

```sh
git clone --branch codex/render-trace-columnar-dbt https://github.com/dataders/dbt-core.git
cd dbt-core
git checkout e7813a27b1d
uvx maturin build --manifest-path crates/dbt-sa-python/Cargo.toml --out dist
uv pip install --python /path/to/sqlfluff/.venv/bin/python dist/dbt_core-<version>-<platform>.whl
```

These commands build dbt's own wheel; the plugin bundles no native runtime.
The debug runtime validation sets `RUST_LOG=debug` and `DBT_LOG_LEVEL=debug`
to avoid an upstream tracing-initialization panic also seen without trace export.
Those settings are inherited by subprocesses, not forced on users by the plugin.
Release builds have not been validated.

## Legacy JSON producer

Protocol-v1 JSON support remains available for the original proposal. Earlier
validation used public producer
[`3116b9498`](https://github.com/alanmcruickshank/dbt/commit/3116b949886d85aae646cc1479e7f703b88865d1).
That historical revision is distinct from the Parquet producer above. The
intermediate single-file Parquet and parallel-array JSON formats are not supported.

## Contract used by SQLFluff

The consumer invokes:

```sh
dbt compile --select path:models/example.sql --generate-info-schema --feature write_render_trace
```

The [producer's design notes](https://github.com/dataders/dbt-core/blob/e7813a27b1d/docs/architecture/render-trace.md)
and the [Parquet compatibility contract](README.md#parquet-producer-compatibility)
describe the format. `--generate-info-schema` is required to publish the public table. SQLFluff depends on:

- Protocol version 1 (JSON sidecars) or version 2 (nested Parquet snapshot), and
  the `jinja_before_ephemeral_injection` render stage. See the
  [Parquet compatibility contract](README.md#parquet-producer-compatibility).
- Exact source and rendered strings, without applying source-rewriting offsets
  to a different file or applying pre-injection offsets to final compiled SQL.
- Ordered literal, expression, macro, layout and loop events with half-open
  UTF-8 byte ranges. Repeated source ranges and nested macro ranges are allowed.
- Source, model and invocation identity matching the freshly emitted manifest.
- A requested trace coming from a fresh render, even when compiled SQL is cached.
- Disabled nodes emit no stub. Their full source path and explicit disabled status
  in the same invocation's manifest distinguish a skip from missing output.

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

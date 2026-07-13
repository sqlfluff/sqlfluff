# sqlfluffrs_benchmarks

TPC-H and TPC-DS lex/parse benchmarks for the sqlfluff Rust parser.

The query fixtures are **not committed to this repository**. They are downloaded
at build time by [`build.rs`](build.rs) from the [Apache Doris](https://github.com/apache/doris)
project at a pinned commit and cached under the crate's `OUT_DIR`. Fetching only
happens when the `fetch` feature is enabled, so a normal `cargo build --workspace`
(and CI) never touches the network.

## Usage

```sh
# Criterion benchmarks (downloads fixtures on first run, then caches them):
cargo bench -p sqlfluffrs_benchmarks --features fetch

# Only TPC-H, or only TPC-DS:
cargo bench -p sqlfluffrs_benchmarks --features fetch -- tpch
cargo bench -p sqlfluffrs_benchmarks --features fetch -- tpcds

# Only the native AST path (root_parse: parse + materialise the Rust Node AST;
# the parse_* benchmarks measure call_rule_as_root's MatchResult only):
cargo bench -p sqlfluffrs_benchmarks --features fetch -- native_ast

# Timing + parser-stats harness (per-query breakdown, then suite summaries):
cargo run -p sqlfluffrs_benchmarks --example time_tpc --features fetch --release
```

Without `--features fetch` the fixtures are absent and the bench/example fail
fast at runtime with a message pointing back to this flag.

## Fixture provenance

The SQL is fetched from [Apache Doris](https://github.com/apache/doris) at commit
[`3a2d9d55`](https://github.com/apache/doris/tree/3a2d9d55f1e8e2d74187179ef89c36c8562815fd)
(`tools/tpch-tools/queries`, `tools/tpcds-tools/queries/sf1`), itself derived
from the [TPC-H](https://www.tpc.org/tpch/) and [TPC-DS](https://www.tpc.org/tpcds/)
benchmark specifications. The queries serve only as representative real-world
SQL inputs for benchmarking the lexer and parser; no TPC benchmark results are
produced or published, and no claims of TPC compliance are made.

`build.rs` normalizes each file (Unix line endings, trailing whitespace
stripped) so lexer inputs are stable across platforms. TPC-DS queries 14, 23,
24, and 39 are defined as two independent statements; Doris stores these as
`query{n}.sql` + `query{n}_1.sql`, and the build script consolidates each pair
into a single `{n}.sql`, separated by a blank line.

| Suite   | Queries     | Source path                                  |
|---------|-------------|----------------------------------------------|
| TPC-H   | 22 (Q1–Q22) | `tools/tpch-tools/queries/q{n}.sql`          |
| TPC-DS  | 99 (Q1–Q99) | `tools/tpcds-tools/queries/sf1/query{n}.sql` |

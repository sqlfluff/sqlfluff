# Rust Components — AI Assistant Instructions

Guidance for SQLFluff's Rust components (`sqlfluffrs/`). This file orients and routes; it
does not embed long code samples (those rot). For anything detailed, follow the links.

## What this is

An optional, experimental Rust acceleration of SQLFluff's lexing and parsing, shipped as a
PyO3 extension. It is a **table-driven, iterative** lexer + parser whose output must match
the Python parser exactly (Python is the source of truth). It accelerates Python; it does
not replace it. Python selects it via the `use_rust_parser = auto|true|false` config key.

## Workspace map

A Cargo workspace (see [`Cargo.toml`](Cargo.toml) `[workspace].members`):

| Crate | Purpose |
|-------|---------|
| `sqlfluffrs_types` | Shared types: `GrammarId`, `GrammarInst`, `GrammarTables`, `Token`, `ParseMode`, `MatchResult`. |
| `sqlfluffrs_lexer` | Text → tokens. → [`sqlfluffrs_lexer/README.md`](sqlfluffrs_lexer/README.md) |
| `sqlfluffrs_dialects` | **Generated** grammar tables + lexer matchers per dialect. `build.rs` runs the codegen. |
| `sqlfluffrs_parser` | The parser engine. → [`sqlfluffrs_parser/README.md`](sqlfluffrs_parser/README.md) + [`ENGINE.md`](ENGINE.md) |
| `sqlfluffrs_python` / root `src/` | PyO3 bindings + `sqlfluffrs.pyi` type stubs. |

## ⚠️ Golden rule: don't edit generated dialect files

Files under `sqlfluffrs_dialects/src/dialect/**` are **generated** from the Python dialect
definitions and are **not** in version control. Editing them is pointless — the next
`cargo build` overwrites them. To change a dialect:

1. Edit the Python in `src/sqlfluff/dialects/dialect_*.py`.
2. Regenerate: `python utils/rustify.py build` (or `tox -e generate-rs`).

The full pipeline is documented in [`ENGINE.md` §6](ENGINE.md).

## Build & test

```bash
cd sqlfluffrs
cargo build                 # debug; build.rs regenerates dialects if Python sources changed
cargo build --release       # optimized
cargo test                  # Rust unit + integration tests (incl. parity fixtures)
cargo clippy                # lint
cargo fmt                   # format
```

From the repo root:

```bash
tox -e generate-rs          # regenerate the dialect tables
tox -e build-rs             # build the Python wheel via maturin
tox -e py311-rust -- -n 6   # full Python test suite against the Rust parser
```

## Parity contract

Rust output must match the Python parser's YAML fixtures under
`test/fixtures/dialects/<dialect>/`, verified by `sqlfluffrs/tests/fixture_tests.rs` and
`yaml_compare.rs`. The invariants the engine must hold, and a step-by-step **runbook for
debugging a fixture mismatch**, are in [`ENGINE.md` §4 and §7](ENGINE.md). To localise a
divergence, use `python utils/parity_diff.py --dialect <d> --fixture <name>`.

## Performance contract

Engine changes are under a **hard no-regression benchmark gate**. Before/after any change to
`sqlfluffrs_parser`, capture a baseline and run the gate — see [`PERF.md`](PERF.md)
(`tox -e perf-baseline-rust`, then `tox -e perf-gate-rust`).

## Coding standards

- Idiomatic Rust: prefer iterators, pattern matching, and ownership over cloning.
- Error handling: return `Result` and use `?`. Avoid `unwrap()`/`expect()` outside tests.
- Naming: `snake_case` items, `PascalCase` types, `SCREAMING_SNAKE_CASE` consts.
- Run `cargo fmt` and `cargo clippy` before committing.
- Keep the engine's hot loop free of `dyn` dispatch and avoidable allocations (see
  [`PERF.md`](PERF.md) and [`ENGINE.md` §3](ENGINE.md)).

## See also

- [`ENGINE.md`](ENGINE.md) — engine architecture, parity invariants, codegen pipeline, debugging.
- [`PERF.md`](PERF.md) — the benchmark gate.
- Root `AGENTS.md` — general project overview. `src/sqlfluff/AGENTS.md` — Python standards.

# Rust Components - AI Assistant Instructions

This file provides guidance for SQLFluff's Rust components.

## Overview

The `sqlfluffrs/` directory contains an **experimental Rust implementation** of performance-critical SQLFluff components. This is an ongoing effort to accelerate lexing and parsing operations while maintaining compatibility with the Python implementation.

## Project Status

**Current state**: Opt-in beta, gated by config (`core.use_rust_parser = auto`).
Shipped as the `sqlfluff[rs]` extra since 4.0; planned to become the default
from 5.0.

**What's migrated:**
- **Lexer** — done; Rust tokenizes and returns `RsToken`s that Python wraps.
- **Parser** — core done for **all dialects**, but **hybrid**: Rust returns a
  lightweight `MatchResult` (slices/classes/inserts); Python's
  `MatchResult.apply()` still builds the `BaseSegment` AST. A parallel,
  id-addressable Rust arena (`_rs_tree`, `RsTree`/`RsHandle`) is built and cached
  as the substrate for Rust-side rules (read-only to Python today).
- **Linting rules & fixing** — **not migrated**; 100% Python. One **experimental
  prototype** exists: `RsTree.cp01_violations(...)` runs CP01's detection loop
  natively over the arena (validated at parity with stock CP01), but it is **not
  wired into rule dispatch** — the Python rule still runs. It currently lives in
  the parser crate (`parser/rules_cp01.rs`) as scaffolding; a production home (a
  `rules` module) and dispatch/gating are pending an arena public-API decision.
  See `parser/rules_cp01.rs` and PR #7984.

**Not a replacement**: the Rust components work alongside Python. When
`sqlfluffrs` is unavailable, Python falls back transparently (auto mode).

## Structure

This is a **Cargo workspace** with several member crates — not a single `src/`
tree. The root crate (`sqlfluffrs`) is a thin PyO3 extension module that
aggregates the others; the real work lives in the member crates.

```
sqlfluffrs/
├── Cargo.toml              # Workspace root + root crate (cdylib + rlib)
├── pyproject.toml          # Python packaging (maturin) for the extension
├── sqlfluffrs.pyi          # Python type stubs (Rs* names); + py.typed marker
├── src/                    # Root crate — aggregation only
│   ├── lib.rs              #   Library root
│   ├── python.rs           #   #[pymodule] — registers all PyO3 classes
│   └── test_harness.rs     #   Fixture-comparison test helpers
├── tests/                  # Integration tests (YAML/fixture parity vs Python)
├── benches/                # Criterion benchmarks (parser_bench, …)
│
├── sqlfluffrs_types/       # LEAF crate — core data types (no internal deps):
│   └── src/                #   Token, PositionMarker, Slice, config/, templater/,
│                           #   GrammarInst / GrammarTables (flattened grammar)
├── sqlfluffrs_dialects/    # Dialect grammars + lexers (GENERATED — see below)
│   ├── build.rs            #   Reruns utils/rustify.py when Python dialects change
│   └── src/                #   block_comment.rs + generated dialect/<name>/*
├── sqlfluffrs_lexer/       # Tokenization        (deps: types, dialects)
├── sqlfluffrs_parser/      # Largest crate — table-driven + recursive parser
│   └── src/parser/         #   core.rs, frame.rs, cache.rs, table_driven/*
├── sqlfluffrs_python/      # PyO3 wrapper shims (PyToken, PyPositionMarker, …)
└── sqlfluffrs_benchmarks/  # TPC-H / TPC-DS fixture helpers
```

**Internal dependency graph:**

```
types ← dialects ← lexer ← parser ← root crate (sqlfluffrs) & benchmarks
sqlfluffrs_python depends only on types; lexer/parser pull it in under
the `python` feature.
```

> **Generated code:** the `dialect/<name>/{mod,matcher,parser}.rs` files under
> `sqlfluffrs_dialects/src/` are produced by `utils/rustify.py` from the Python
> dialect definitions — **never hand-edit them**. See "Syncing with Python".

## Rust Development Setup

### Requirements

- **Rust**: Install via [rustup](https://rustup.rs/)
  ```bash
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
  ```
- **Cargo**: Comes with Rust installation
- **Python development headers**: Required for PyO3 bindings

### Building Rust Components

```bash
# Navigate to Rust directory
cd sqlfluffrs

# Build Rust library
cargo build

# Build release (optimized)
cargo build --release

# Run Rust tests
cargo test

# Run with output
cargo test -- --nocapture

# Check code without building
cargo check

# Format code
cargo fmt

# Lint code
cargo clippy
```

### Python Integration

The Rust components are exposed to Python via **PyO3** and packaged with
**maturin** (see `pyproject.toml`). The extension is built with the `python`
feature enabled, which pulls in `pyo3` and the `*/python` features of the lexer
and parser crates.

```bash
# Build + install the extension into the active venv (rebuilds on Rust changes)
cd sqlfluffrs
maturin develop            # debug
maturin develop --release  # optimized — use this for benchmarking

# A plain pip install also works (invokes maturin under the hood):
pip install -e ./sqlfluffrs/
```

> Building the extension triggers `sqlfluffrs_dialects/build.rs`, which runs
> `utils/rustify.py` to (re)generate dialect sources. It needs Python able to
> `import sqlfluff`, so build from an environment where the repo's `src/` is on
> `PYTHONPATH` (the build script handles this for isolated build envs).

## Rust Coding Standards

### Style

- **Follow Rust conventions**: Use `rustfmt` for formatting
- **Naming**:
  - `snake_case` for functions, variables, modules
  - `PascalCase` for types, structs, enums, traits
  - `SCREAMING_SNAKE_CASE` for constants
- **Idiomatic Rust**: Prefer iterators, pattern matching, and ownership patterns

### Error Handling

**Prefer `Result` and `?` operator:**
```rust
fn parse_token(input: &str) -> Result<Token, ParseError> {
    let trimmed = input.trim();
    if trimmed.is_empty() {
        return Err(ParseError::EmptyInput);
    }
    Ok(Token::new(trimmed))
}

fn process() -> Result<(), ParseError> {
    let token = parse_token("  SELECT  ")?;  // Use ? operator
    // ... use token
    Ok(())
}
```

**Avoid `unwrap()` and `expect()` in production code:**
```rust
// ❌ Bad: Can panic
let value = some_option.unwrap();

// ✅ Good: Handle None case
let value = match some_option {
    Some(v) => v,
    None => return Err(Error::MissingValue),
};

// ✅ Also good: Use ? with Option
let value = some_option.ok_or(Error::MissingValue)?;
```

**Exception**: `unwrap()` and `expect()` are acceptable in tests.

### Testing

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_token_parsing() {
        let result = parse_token("SELECT");
        assert!(result.is_ok());
        assert_eq!(result.unwrap().value, "SELECT");
    }

    #[test]
    fn test_empty_input_fails() {
        let result = parse_token("");
        assert!(result.is_err());
    }
}
```

Run tests:
```bash
cargo test
cargo test --lib          # Library tests only
cargo test --release      # Optimized build
```

## Python-Rust Interface (PyO3)

### Exposing Rust to Python

The public API is **class-based**, not free functions. The `#[pyclass]` wrappers
live in the `sqlfluffrs_python` crate and in each component crate's `python.rs`
(e.g. `PyLexer`, `PyParser`); they are all registered in the root crate's
`src/python.rs`. Note the module uses the modern PyO3 `Bound` API:

```rust
// src/python.rs (abridged)
use pyo3::prelude::*;
use sqlfluffrs_lexer::{PyLexer, PySQLLexError};
use sqlfluffrs_parser::{PyMatchResult, PyNode, PyParser, RsParseError};
use sqlfluffrs_python::token::{PyCaseFold, PyToken};

#[pymodule(name = "sqlfluffrs", module = "sqlfluffrs")]
fn sqlfluffrs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyToken>()?;
    m.add_class::<PyLexer>()?;
    m.add_class::<PyParser>()?;
    m.add_class::<PyNode>()?;
    m.add_class::<PyMatchResult>()?;
    m.add("RsParseError", m.py().get_type::<RsParseError>())?;
    Ok(())
}
```

These classes are surfaced to Python under their `Rs*` aliases (e.g. `PyLexer`
→ `RsLexer`, `PyParser` → `RsParser`); the Python side imports them in
`src/sqlfluff/core/parser/{lexer.py,rust_parser.py}` behind a try/except so a
missing extension degrades to pure Python.

### Type Stubs

Public types are declared in `sqlfluffrs.pyi` under their `Rs*` names, e.g.:

```python
class RsLexer:
    def _lex(self, lex_input: object) -> object: ...

class RsParser:
    def parse_match_result_from_tokens(self, ...) -> RsMatchResult: ...
```

## Architecture

The pipeline is **lex → parse**, with dialect grammars supplied as flat tables.

### Lexer (`sqlfluffrs_lexer`)

`Lexer` (in `sqlfluffrs_lexer/src/lexer.rs`) turns a SQL string (plus templater
metadata) into a `Vec<Token>` using the dialect's `LexMatcher`s. Tokens and
`PositionMarker`s are defined in `sqlfluffrs_types`.

### Grammar representation (`sqlfluffrs_types`)

Python's grammar AST (`Sequence`, `OneOf`, `Bracketed`, `Delimited`, `Ref`,
`StringParser`, …) is **not** modelled as a tree of trait objects. Instead it is
**flattened by codegen** into compact static tables — `GrammarInst` (~20 bytes
each) indexed by `GrammarId`, plus side tables (`CHILD_IDS`, `TERMINATORS`,
`STRINGS`, `AUX_DATA`, `SIMPLE_HINTS`, …). See `grammar_inst.rs` /
`grammar_tables.rs`. This keeps a dialect ~1 MB instead of tens of MB of boxed
nodes and avoids per-node heap allocation.

### Parser (`sqlfluffrs_parser`)

A **table-driven** engine walks those tables. The hot path is the iterative,
frame-based executor in `src/parser/table_driven/` (one module per grammar
variant: `sequence.rs`, `oneof.rs`, `bracketed.rs`, `delimited.rs`,
`anynumberof.rs`, `ref_grammar.rs`, plus `iterative.rs` driving the frame stack).
`oneof.rs` uses pre-computed `SimpleHint`s to prune alternatives cheaply. The
parser produces a `MatchResult`, not a finished AST (Python builds the AST — see
Project Status).

### Dialect support (`sqlfluffrs_dialects`)

All Python dialects are mirrored here as **generated** modules. Each dialect gets
`matcher.rs` (lexers + keyword sets) and `parser.rs` (the grammar tables above),
dispatched through a generated `Dialect` enum. Do not edit by hand — regenerate
via `utils/rustify.py` (see "Syncing with Python").

## Performance Considerations

### Benchmarking

Use Criterion for benchmarks:

```rust
// benches/lexer_bench.rs
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn lexer_benchmark(c: &mut Criterion) {
    c.bench_function("lex_simple_select", |b| {
        b.iter(|| {
            let sql = black_box("SELECT * FROM users WHERE id = 1");
            lex(sql)
        });
    });
}

criterion_group!(benches, lexer_benchmark);
criterion_main!(benches);
```

Run benchmarks:
```bash
cargo bench
```

Criterion measures the Rust internals in isolation. To see how the cost is
split across the **Python↔Rust boundary** when SQLFluff actually drives the
Rust parser, use the per-stage profiler instead (see below).

### Profiling the Python↔Rust parse path

`RustParser.parse()` (in `src/sqlfluff/core/parser/rust_parser.py`) is a fast
Rust core wrapped in O(nodes) Python work. The profiler splits a parse into
four stages so you can see where the time goes:

- `rust_core` — the Rust parse (`parse_match_result_from_tokens`)
- `convert` — rebuilding the result as a Python `MatchResult`
- `apply` — building the `BaseSegment` tree (`MatchResult.apply`)
- `apply_as_node` — building the `_rs_node` tree

Enable it via the `SQLFLUFF_RS_PROFILE` env var or `set_profiling(True)`, then
read the most recent parse with `get_parse_profile()`. The benchmark harness
surfaces it directly (overall + small/medium/large file buckets):

```bash
# Requires the Rust parser (--compare or --rust-only); no effect on pure Python.
python utils/benchmark_parsing.py --dialect ansi --rust-only --profile
```

As a rule of thumb, the Python-side stages dominate parse time on small/medium
files (the FFI/tree-build overhead is not yet amortised), while `rust_core`
dominates on large files.

### Optimization

- Use `cargo build --release` for production builds
- Profile with `cargo flamegraph` or `perf`
- Prefer zero-copy operations where possible
- Use `&str` over `String` when ownership not needed

## Development Workflow

### Making Changes

1. **Edit Rust code** in the relevant member crate (e.g. `sqlfluffrs_parser/src/`)
2. **Run tests:**
   ```bash
   cargo test                 # workspace-wide
   cargo test -p sqlfluffrs_parser   # a single crate
   ```
3. **Format code:**
   ```bash
   cargo fmt
   ```
4. **Lint:**
   ```bash
   cargo clippy
   ```
5. **Build Python extension:**
   ```bash
   maturin develop --release
   ```
6. **Test Python integration:**
   ```python
   import sqlfluffrs
   # exercise RsLexer / RsParser from Python
   ```

### Syncing with Python

The dialect grammars/lexers are **generated from the Python dialect
definitions** in `src/sqlfluff/dialects/`. After changing a Python dialect (or
the generators in `utils/build_*.py`):

1. **Regenerate the Rust dialect sources:**
   ```bash
   # From repository root, in an env where `import sqlfluff` works
   source venv/bin/activate
   python utils/rustify.py build      # `check` verifies output is up to date (CI)
   ```
   (A normal `cargo build` / `maturin develop` also triggers this via
   `sqlfluffrs_dialects/build.rs` when Python sources are newer.)

2. **Confirm parity against the Python suite:**
   ```bash
   tox -e py312
   ```
   Cross-language parity is also checked by the Rust integration tests in
   `tests/` (e.g. `fixture_tests.rs`), which compare Rust parse output against
   the YAML fixtures used by the Python tests.

## Common Tasks

### Adjusting Lexing Behaviour

1. Edit the lexer engine in `sqlfluffrs_lexer/src/lexer.rs`.
2. Note: the per-dialect lexer matchers/keywords are **generated** into
   `sqlfluffrs_dialects/src/dialect/<name>/matcher.rs` — to change *those*,
   edit the Python dialect and regenerate (next section), don't hand-edit.
3. Write tests, run `cargo test`.

### Updating a Dialect

Dialect grammars are generated, so the source of truth is **Python**:

1. Edit `src/sqlfluff/dialects/dialect_<name>.py` (keywords, grammar, etc.).
2. Regenerate: `python utils/rustify.py build`.
3. Test parity: `cargo test` (fixtures) and `tox -e py312-rust`.

### Exposing a New Class to Python

1. Add a `#[pyclass]` in `sqlfluffrs_python` (or the owning component crate's
   `python.rs`).
2. Register it in the root crate's `src/python.rs`:
   ```rust
   m.add_class::<PyMyThing>()?;
   ```
3. Add the corresponding `Rs*` type to `sqlfluffrs.pyi`.
4. Wire it into the Python side (`src/sqlfluff/core/parser/…`) behind the
   existing try/except import so a missing extension still degrades gracefully.
5. Rebuild with `maturin develop` and test.

## Testing

### Rust Unit Tests

```bash
# All tests
cargo test

# Specific test
cargo test test_lexer_keywords

# Show output
cargo test -- --nocapture

# With release optimizations
cargo test --release
```

### Integration with Python Tests

Rust components are tested via Python test suite:

```bash
# Ensure Rust extension is built
cd sqlfluffrs && pip install -e . && cd ..

# Run Python tests
tox -e py312
```

## Resources

- **Rust Book**: https://doc.rust-lang.org/book/
- **PyO3 Guide**: https://pyo3.rs/
- **Cargo Book**: https://doc.rust-lang.org/cargo/
- **Rust by Example**: https://doc.rust-lang.org/rust-by-example/

## Current Limitations

- **Lexing and parsing only** — linting rules and the fix/format pipeline are
  still entirely Python; the Rust node tree (`_rs_node`) has no consumers yet.
- **Hybrid parse** — Rust returns a `MatchResult`; Python still builds the AST.
- **Performance gains scale with file size** — small files see little benefit
  because of the Python↔Rust crossing overhead.
- All shipped dialects are mirrored and parity-tested against the Python
  fixtures, so dialect *coverage* is not a current limitation.

## Contributing to Rust Components

Rust contributions are welcome but should:
- Maintain API compatibility with Python
- Include tests
- Follow Rust conventions
- Update Python type stubs
- Sync with Python implementation via `rustify.py`

---

**See also:**
- Root `AGENTS.md` for general project overview
- `src/sqlfluff/AGENTS.md` for Python coding standards
- `sqlfluffrs/README.md` for Rust-specific README

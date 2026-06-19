# The Rust Parser Engine

Authoritative description of how `sqlfluffrs_parser` works, the invariants it must
preserve to stay compatible with Python, and how to debug a divergence. If you are
modifying anything under `sqlfluffrs_parser/src/parser/`, read this first.

For the data-layout/lookup-table mechanics and the grammar-variant catalogue, the
crate README is accurate and is **not** duplicated here — see
[`sqlfluffrs_parser/README.md`](sqlfluffrs_parser/README.md). For lexer internals see
[`sqlfluffrs_lexer/README.md`](sqlfluffrs_lexer/README.md).

## 1. Mental model

The engine is **table-driven** and **iterative**. If you arrive expecting a recursive
tree of `Box<dyn Matcher>` objects that call each other — that mental model is wrong and
no longer exists in this codebase. Instead:

- **Grammar is data, not code.** Every grammar rule is a `GrammarInst` (20 bytes) in a
  flat static array, addressed by a `GrammarId` (a `u32` index). Rules reference each
  other by index, never by pointer. The tables are immutable `&'static` data generated
  from the Python dialects (see §5).
- **Parsing is a loop over an explicit frame stack**, not recursion. This is what lets
  the parser handle deeply nested SQL without overflowing the call stack (the depth guard
  `DEFAULT_MAX_PARSE_DEPTH = 600` is a logical limit, not a stack limit).

## 2. Data layout (contract)

A `GrammarId` indexes parallel static arrays (`instructions`, `child_ids`, `terminators`,
`strings`, …) bundled in `GrammarTables` (`sqlfluffrs_types`). The contract a refactor must
respect:

- IDs are array **indices**, not pointers; tables are **immutable and `'static`**.
- Children of a rule are a contiguous slice `child_ids[first_child_idx .. +child_count]`.
- Per-field byte details live in `sqlfluffrs_types::grammar_inst` — point there rather
  than restating them here (they change; this contract does not).

See the README's diagram for the picture.

## 3. The frame state machine

The loop lives in [`table_driven/iterative.rs`](sqlfluffrs_parser/src/parser/table_driven/iterative.rs)
(`parse_table_iterative_match_result`), driven off an explicit stack of `TableParseFrame`.
Two enums in [`parser/frame.rs`](sqlfluffrs_parser/src/parser/frame.rs) define the machine:

**`FrameState`** — where a frame is in its lifecycle:

| State | Meaning |
|-------|---------|
| `Initial` | First entry: compute terminators + `max_idx`, maybe check cache, push first child. |
| `WaitingForChild { child_index }` | A child frame was pushed; resume when its result lands. |
| `Combining` | All children done; assemble this frame's `MatchResult`. |
| `Complete(Arc<MatchResult>)` | Result ready to return to the parent frame. |

**`FrameContext`** — per-variant scratch state carried across states. One variant per
compound grammar: `SequenceTableDriven`, `OneOfTableDriven`, `DelimitedTableDriven`,
`BracketedTableDriven`, `AnyNumberOfTableDriven`, `RefTableDriven` (plus `None` for the
terminal parsers). Each holds what that handler needs between `WaitingForChild` resumes
(e.g. `OneOfTableDriven.longest_match`, `SequenceTableDriven.start_idx`).

Dispatch is a static `match` on `GrammarVariant` (a jump table) in three places —
`*_initial`, `*_waiting_for_child`, `*_combining` — one handler module per variant under
[`table_driven/`](sqlfluffrs_parser/src/parser/table_driven/). **There is deliberately no
`dyn` trait dispatch in this loop**; introducing a vtable here is a performance regression
(see [`PERF.md`](PERF.md)).

Entry points (`parser/core.rs`): `call_rule_as_root()` returns a `MatchResult`
(Python then calls `apply()` to build its own segments); `root_parse()` returns a
materialised `Node` for Rust-side use. Construct with `Parser::new(...)` or
`Parser::new_with_max_parse_depth(...)`.

## 4. The Python-parity contract

The engine must produce the same parse tree as the Python parser (`sqlfluff/core`), which
is the source of truth. These are the invariants the iterative engine exists to preserve;
a refactor may not change any of them without a corresponding Python change. The
single-source-of-truth helpers that encode them live in
[`table_driven/parity.rs`](sqlfluffrs_parser/src/parser/table_driven/parity.rs) — grep
`MIRRORS` to enumerate the whole surface.

1. **Longest match wins.** `OneOf` selects the alternative that consumes the most tokens
   (not the first that matches); ties resolve to the earliest-listed alternative. Mirrors
   Python `longest_match`.
2. **Parse modes.** `ParseMode` (Strict / Greedy / GreedyOnceStarted) governs whether an
   unmatched tail is an error or is absorbed as unparsable. Mirrors Python `ParseMode`.
3. **Terminators bound the window.** Each compound rule computes a trimmed `max_idx` from
   its terminators before matching children; children see the parent's terminators per the
   reset/combine rules. The `max_idx` used to populate the cache key MUST equal the one
   used to look it up (see §5 — getting this wrong silently corrupts results).
4. **Match accounting.** Empty vs. non-empty matches, `insert_segments` (meta Indent/
   Dedent), and child-match nesting must match Python's `MatchResult` shape so `apply()`
   yields identical segments.

## 5. Optimizations and their correctness conditions

Each optimization (detailed in the README) is valid **only because** an invariant holds —
do not break the precondition:

- **Simple-hint pruning** (`OneOf`) skips alternatives that cannot start with the current
  token. Valid only because hints are computed to never exclude a viable longest match.
- **Bracket pre-matching** gives O(1) "find the closing bracket" — valid because bracket
  pairs are fixed at lex time.
- **Frame cache** (`parser/cache.rs`, keyed `TableCacheKey { pos, grammar_id, max_idx }`)
  memoises complete results for cacheable variants. Valid only if the cacheable-set and the
  `max_idx` formula are **identical at store and lookup** — both go through one helper in
  `parity.rs` precisely so they cannot drift.

## 6. The codegen pipeline (Python → tables)

The dialect tables are **generated, not hand-written**:

```
src/sqlfluff/dialects/dialect_*.py        # grammar definitions (source of truth)
        │
        ├── utils/build_parsers.py         # flattens the grammar AST → instruction tables
        ├── utils/build_lexers.py          # lexer matchers + keywords
        └── utils/rustify.py build         # orchestrates, emits Rust
        │
        ▼
sqlfluffrs_dialects/build.rs               # mtime-triggers the above on `cargo build`
        │   (cargo:rerun-if-changed on the Python sources)
        ▼
sqlfluffrs_dialects/src/dialect/<name>/{parser,matcher}.rs   # GENERATED, not in VCS
        │
        ▼
the engine (this crate) interprets the tables
```

> **Golden rule:** never edit files under `sqlfluffrs_dialects/src/dialect/`. They are
> regenerated and your changes will be lost. To change a dialect, edit the Python in
> `src/sqlfluff/dialects/` and run `python utils/rustify.py build` (or `tox -e generate-rs`).

## 7. Debugging a fixture mismatch

When a parity fixture fails (`sqlfluffrs/tests/fixture_tests.rs` /
`yaml_compare.rs` compare Rust output to the Python-generated `*.yml` under
`test/fixtures/dialects/<dialect>/`):

1. **Reproduce narrowly:** `cargo test --test yaml_compare <name>` (or `fixture_tests`).
2. **Localise the divergence** with the differential debugger:
   `python utils/parity_diff.py --dialect <d> --fixture <name>` (or `--sql "<snippet>"` for
   an ad-hoc query) prints the first divergent node — its grammar path, the kind of
   difference, and the differing subtree on each side — instead of "trees differ".
3. **Trace the engine** for deep cases: rebuild with the `verbose-debug` feature
   (`cargo test --features verbose-debug ...`) to emit the `vdebug!` frame trace, and use
   `Parser::dump_table_driven_grammar_info(...)` to inspect the resolved tables.
4. **Map the symptom to an invariant** (§4): wrong alternative chosen → invariant 1
   (longest match / hints); trailing tokens dropped or an unexpected error → invariant 2/3
   (parse mode / terminators); right tokens but wrong nesting or missing meta → invariant 4.
5. **Lock it in:** add a minimal reproducer as a normal dialect fixture
   (`test/fixtures/dialects/<dialect>/<name>.sql`), generate its expected tree with
   `tox -e generate-fixture-yml`, and commit both. The `pyXXX-rust` suite then parses it
   with the Rust parser and asserts it matches, guarding against recurrence.

## See also

- [`README` (this crate)](sqlfluffrs_parser/README.md) — table layout, variants, optimizations.
- [`AGENTS.md`](AGENTS.md) — workspace map and build/test commands.
- [`PERF.md`](PERF.md) — the no-regression benchmark gate every engine change must pass.

# The Rust Parser Engine

How `sqlfluffrs_parser` works, the invariants that keep it compatible with Python, and how
to debug a divergence. Read this before changing anything under `sqlfluffrs_parser/src/parser/`.

Table-layout mechanics and the grammar-variant catalogue live in
[`sqlfluffrs_parser/README.md`](sqlfluffrs_parser/README.md); lexer internals in
[`sqlfluffrs_lexer/README.md`](sqlfluffrs_lexer/README.md).

## 1. Mental model

- **Grammar is data.** Each rule is a 20-byte `GrammarInst` in a flat `&'static` array,
  addressed by a `GrammarId` (`u32` index); rules reference each other by index. The tables
  are generated from the Python dialects (see the codegen pipeline section).
- **Parsing is iterative.** The engine drives an explicit stack of frames, so nesting depth
  is bounded by `DEFAULT_MAX_PARSE_DEPTH` (600) rather than the call stack.

## 2. Data layout

A `GrammarId` indexes parallel `&'static` arrays (`instructions`, `child_ids`,
`terminators`, `strings`, …) held in `GrammarTables` (`sqlfluffrs_types`). Contract:

- IDs are array indices into immutable tables.
- A rule's children are the slice `child_ids[first_child_idx .. +child_count]`.
- Field-level byte layout lives in `sqlfluffrs_types::grammar_inst`; the points above are
  the stable contract. (The README has the diagram.)

## 3. The frame state machine

The loop is `parse_table_iterative_match_result` in
[`table_driven/iterative.rs`](sqlfluffrs_parser/src/parser/table_driven/iterative.rs), over
a stack of `TableParseFrame`. Two enums in
[`parser/frame.rs`](sqlfluffrs_parser/src/parser/frame.rs) define it.

**`FrameState`** — a frame's lifecycle position:

| State | Meaning |
|-------|---------|
| `Initial` | Compute terminators + `max_idx`, check cache, push first child. |
| `WaitingForChild { child_index }` | A child frame was pushed; resume when its result lands. |
| `Combining` | All children done; assemble this frame's `MatchResult`. |
| `Complete(Arc<MatchResult>)` | Result ready to return to the parent. |

**`FrameContext`** — per-variant scratch carried across resumes; one variant per compound
grammar (`Sequence(SequenceState)`, `OneOf(OneOfState)`, `Delimited(DelimitedState)`,
`Bracketed(BracketedState)`, `AnyNumberOf(AnyNumberOfState)`, `Ref(RefState)`), plus `None`
for terminal parsers. Each named state struct holds what its handler needs between resumes
(e.g. `OneOfState::longest_match`); `as_*_mut()` accessors on `FrameContext` return the
typed `&mut *State` for one variant.

Dispatch is a static `match` on `GrammarVariant` — a jump table — at `*_initial`,
`*_waiting_for_child`, and `*_combining`, with one handler module per variant under
[`table_driven/`](sqlfluffrs_parser/src/parser/table_driven/). Keep it static: a trait
object here costs a vtable load per transition on the hottest path.
Bracketed and Delimited additionally dispatch their `WaitingForChild` resume on the
sub-state enum (`BracketedPhase` / `DelimitedPhase`) to one method per phase.

**Results hand-off.** A frame doesn't return to its parent directly. When a child reaches
`Complete`, the loop writes `(Arc<MatchResult>, end_pos, element_key)` into
`TableParseFrameStack.results` keyed by the child's `frame_id`. The parent — parked in
`WaitingForChild` — reclaims it on resume via its own `last_child_frame_id`. The `Arc` keeps
the hand-off clone-free; `element_key` carries OneOf's per-element identity to AnyNumberOf
(for `max_times_per_element`) and is `None` otherwise.

**MatchResult.** A match is described, not materialised: a `MatchResult` carries the matched
token span, optional `matched_class` (the segment type to create), `insert_segments` (meta
Indent/Dedent to splice in), and `child_matches`. `Combining` assembles a parent's
`MatchResult` from its `child_matches`; Python later calls `apply()` to turn the tree into
real segments. The output pipeline is: engine → `Arc<MatchResult>` → `apply_as_root()` →
`Node` tree → (linter facade) arena → Python. The engine's job ends at a correct
`MatchResult`; everything downstream depends on its shape staying stable, so a refactor must
never change *what* gets recorded in `matched_class` / `insert_segments` / `child_matches`.

Entry points (`parser/core.rs`): `call_rule_as_root()` returns a `MatchResult` (Python then
calls `apply()`); `root_parse()` returns a materialised `Node`. Build with `Parser::new(...)`
or `Parser::new_with_max_parse_depth(...)`.

## 4. Python-parity contract

The Python parser (`sqlfluff/core`) is the source of truth; the engine must produce the same
tree. The helpers that encode these invariants live in
[`table_driven/parity.rs`](sqlfluffrs_parser/src/parser/table_driven/parity.rs) — grep
`MIRRORS` for the full surface.

1. **Longest match wins.** `OneOf` picks the alternative that consumes the most tokens; ties
   go to the earliest listed. (Python `longest_match`.)
2. **Parse modes.** `ParseMode` (Strict / Greedy / GreedyOnceStarted) decides whether an
   unmatched tail errors or is absorbed as unparsable.
3. **Terminators bound the window.** Each compound rule trims `max_idx` by its terminators
   before matching children; children inherit the parent's terminators per the reset/combine
   rule.
4. **Match accounting.** Empty vs non-empty matches, `insert_segments` (meta Indent/Dedent),
   and child nesting must match Python's `MatchResult` so `apply()` yields identical segments.

## 5. Optimizations and their preconditions

Each optimization holds only while its precondition does:

- **Simple-hint pruning** (`OneOf`) skips alternatives that can't start with the current
  token — safe because hints never exclude a viable longest match.
- **Bracket pre-matching** gives O(1) closing-bracket lookup — bracket pairs are fixed at
  lex time.
- **Frame cache** (`parser/cache.rs`, key `TableCacheKey { pos, grammar_id, max_idx }`)
  memoises complete results for cacheable variants. The cacheable-set and the `max_idx`
  formula run through one helper, `frame_cache_key` (in `table_driven/iterative.rs`), so
  the store key and lookup key are computed identically.

> **Pitfall:** if the store and lookup `max_idx` ever diverge, a result caches under one key
> and reads under another — silent corruption. That single shared `frame_cache_key` is what
> prevents it; keep both paths going through it.

## 6. Codegen pipeline (Python → tables)

The dialect tables are generated:

```
src/sqlfluff/dialects/dialect_*.py        # grammar definitions (source of truth)
        │
        ├── utils/build_parsers.py         # flattens the grammar AST → instruction tables
        ├── utils/build_lexers.py          # lexer matchers + keywords
        └── utils/rustify.py build         # orchestrates, emits Rust
        │
        ▼
sqlfluffrs_dialects/build.rs               # mtime-triggers the above on `cargo build`
        ▼
sqlfluffrs_dialects/src/dialect/<name>/{parser,matcher}.rs   # generated, not in VCS
        ▼
the engine (this crate) interprets the tables
```

> **Golden rule:** never edit files under `sqlfluffrs_dialects/src/dialect/**` — they are
> regenerated and your edits are lost. Change a dialect in `src/sqlfluff/dialects/` and run
> `python utils/rustify.py build` (or `tox -e generate-rs`).

## 7. Debugging a fixture mismatch

Parity fixtures (`sqlfluffrs/tests/fixture_tests.rs` / `yaml_compare.rs`) compare Rust output
to the Python-generated `*.yml` under `test/fixtures/dialects/<dialect>/`. When one fails:

1. **Reproduce narrowly:** `cargo test --test yaml_compare <name>` (or `fixture_tests`).
2. **Localise the divergence:** `python utils/parity_diff.py --dialect <d> --fixture <name>`
   (or `--sql "<snippet>"`) prints the first divergent node — grammar path, kind, and the
   differing subtree on each side.
3. **Trace deep cases:** rebuild with `--features verbose-debug` for the `vdebug!` frame
   trace, and use `Parser::dump_table_driven_grammar_info(...)` to inspect resolved tables.
4. **Map symptom → invariant (see the Python-parity contract):** wrong alternative → #1 (longest match / hints); trailing
   tokens dropped or an unexpected error → #2/#3 (parse mode / terminators); right tokens but
   wrong nesting or missing meta → #4.
5. **Lock it in:** add a minimal reproducer as a dialect fixture
   (`test/fixtures/dialects/<dialect>/<name>.sql`), generate its tree with
   `tox -e generate-fixture-yml`, and commit both. The `pyXXX-rust` suite then guards it.

## 8. Glossary

Position indices recur across the variant handlers with consistent meaning (defined on
`FrameContext` in [`parser/frame.rs`](sqlfluffrs_parser/src/parser/frame.rs)):

| Name | Meaning |
|------|---------|
| `start_idx` | Fixed token position where this grammar began matching. Never mutated; the backtrack origin. |
| `matched_idx` | The *committed* frontier — position reached by everything matched and accepted so far. Advances only when a child match is folded in. |
| `working_idx` | An *in-progress probe* position while trying the next child/delimiter. May run ahead of `matched_idx` and roll back if the probe fails. |
| `max_idx` | The *ceiling* — largest position this grammar may consume, derived from terminators + the parent's ceiling. Matching never crosses it. |
| `parent_max_idx` | The ceiling inherited from the parent (input bound). |
| `calculated_max_idx` | The frame's own effective ceiling, computed in `Initial`. Authoritative for matching and the cache key — not `parent_max_idx`. |
| `child_index` | The resume cursor stored in `WaitingForChild`; variant-specific (element index for Sequence, candidates-tried count for OneOf). |

Two `longest_match` shapes exist deliberately: `OneOf` keeps the *longest clean* match
(clean beats unclean at equal length), `AnyNumberOf` keeps the *longest by end position*
only. Both rules live in one policy-tagged helper, `parity::is_better_candidate`
(`LongestClean` vs `LongestEnd`); the fields document which policy applies.

## See also

- [`sqlfluffrs_parser/README.md`](sqlfluffrs_parser/README.md) — table layout, variants, optimizations.
- [`AGENTS.md`](AGENTS.md) — workspace map and build/test commands.

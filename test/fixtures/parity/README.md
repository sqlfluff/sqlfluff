# Parity test cases

Data-driven regression cases for the Python-vs-Rust engine parity suite.
These fixtures are consumed by `test/core/parser/parity/cases_test.py`; the
shared capture/compare machinery (and the full strictness contract) lives in
`test/core/parser/parity/compare.py`.

Parity tests are **differential**: the same input is run through two engine
paths and the results must be identical. That's why cases carry only the
input (SQL), the environment (dialect, config) and metadata - never an
expected output. The Python engine is always the reference.

## What do we mean by "strict" comparisons?

Every comparison captures at **maximal** strictness:

- the parse tree in tuple form with raws, metas and **position markers**,
- `stringify()` bytes (which carry UnparsableSegment "Expected:" messages),
- the raw round-trip,
- per-segment normalization kwargs
  (`quoted_value` / `escape_replacements` / `trim_chars` / `casefold`),
- every leaf segment's full `class_types` set, not just its primary type
  (`to_tuple()`/`stringify()` only ever show the primary type; a bare-class
  `Ref` that wraps a token in an ancestor class can get the primary type
  right while still losing class-level types from the token's own lineage),
- for raised exceptions: type, message, and `SQLBaseError`
  position/flag attributes (`PanicException` included),
- for lexer cases: token class, raw, type, class_types, position marker and
  normalization kwargs, plus lex errors with their messages.

Every case is captured at this same full strictness. A known divergence is
declared per-leg with an `xfail` entry instead, which becomes a **strict**
xfail: the moment the underlying gap is fixed, CI flags the stale marker.

## Case format

Each `*.yml` file groups cases for one theme. Top-level keys are case names;
an optional `_meta: {kind: ...}` key selects the driver:

- `parser` (default) - runs each case on two legs:
  - `python_vs_rust`: pure-Python `Parser` vs `RustParser` (legacy
    convert+apply build path),
  - `native_vs_legacy`: `RustParser`'s fused native-AST build path vs its
    legacy path (Python-vs-legacy parity follows transitively).
- `lexer` - one leg (`lexer`): `PyLexer` vs `PyRsLexer` token streams.
- `invariants` - one leg (`invariants`): checks that the raw `RsMatchResult`
  is structurally well-formed (bounds, ordering, overlap, zero-length
  rules). This audits one engine directly rather than comparing two: a
  violation is a rust-core bug by definition.

Case fields:

| Field         | Meaning |
|---------------|---------|
| `sql`         | Inline SQL input (mutually exclusive with `sql_fixture`). |
| `sql_fixture` | Path under `test/fixtures/dialects/` to read the SQL from - use this when the repro is an already-shipped dialect fixture. |
| `dialect`     | Dialect label; defaults to `ansi`. |
| `configs`     | Optional config mapping. Plain keys are `FluffConfig` overrides (e.g. `max_parse_depth`); dotted keys are section paths applied via `set_value` (e.g. `indentation.indented_joins`), matching how ini-file values are typed (as int rather than bool). |
| `templater`   | Set to `jinja` to drive the case through the Linter (template placeholder tokens; violations are compared too). |
| `context`     | Jinja context variables for templated cases. |
| `pins`        | REQUIRED, human documentation: the bug class this case pins, with issue/commit references where they exist. |
| `expect`      | Optional sanity expectation(s), checked against the reference leg only, so the case keeps testing something real: `tree`, `clean_tree` (tree with no unparsable segments), `error`, `quoted_kwargs`. String or list. |
| `xfail`       | Optional mapping of leg name → reason. Produces a strict xfail for that leg only. |

## Adding a parity regression

1. Minimize the repro to SQL + dialect + config.
2. Add a case to the matching theme file (or start a new one) with a `pins`
   description of the bug class.
3. If the divergence is real and still open, declare it under `xfail` for
   the diverging leg with a precise reason - CI will flag the marker as
   stale the moment the engine gap closes, prompting its removal.
4. Well-formed SQL that belongs in the dialect corpus should go to
   `test/fixtures/dialects/` instead (the whole corpus is swept three-way by
   `test/core/parser/parity/corpus_test.py`); reference it here via
   `sql_fixture` only if it needs a pinned parity annotation.

## Related testing

- `test/core/parser/parity/corpus_test.py` - three-way sweep of every
  dialect fixture at the same strictness.
- `test/core/parser/parity/special_cases_test.py` - parity-adjacent checks
  that need Python-side instrumentation rather than a plain SQL-plus-config
  case, e.g. codegen object-lifetime and hash-seed-stability probes on
  `utils/build_parsers.py`/`utils/build_lexers.py`.

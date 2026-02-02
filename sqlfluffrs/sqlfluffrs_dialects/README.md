# sqlfluffrs_dialects

Auto-generated SQL dialect definitions for lexing and parsing.

## Generation

Most content is **auto-generated** from Python grammar definitions:

```bash
tox -e generate-rs
```

This runs `utils/build_dialects.py` → `utils/rustify.py` to produce static Rust tables.

## What Gets Generated

Each dialect (ansi, tsql, postgres, etc.) produces:

- **`matcher.rs`** — `LexMatcher` array for tokenization, keyword sets
- **`grammar.rs`** — `GrammarTables` struct with all parsing rules

The `Dialect` enum dispatches to the correct tables:

```rust
impl Dialect {
    pub fn get_lexers(&self) -> &[LexMatcher];
    pub fn get_keywords(&self) -> (&HashSet<&str>, &HashSet<&str>);
    pub fn get_root_grammar(&self) -> RootGrammar;
}
```

## Manual Code

Only `block_comment.rs` is manually maintained—it handles nested `/* ... /* ... */ ... */` comments which require stateful parsing that can't be expressed as simple regex matchers.

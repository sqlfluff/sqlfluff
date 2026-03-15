# sqlfluffrs_types

Core types shared across lexer, parser, and dialect crates.

## Grammar Table System

The key innovation is representing grammars as flat lookup tables instead of heap-allocated trees.

### GrammarInst (20 bytes)

Each grammar rule is a single struct:

```rust
pub struct GrammarInst {
    pub variant: GrammarVariant,      // What kind: Sequence, OneOf, Ref, etc.
    pub flags: GrammarFlags,          // Bitflags: optional, allow_gaps, etc.
    pub parse_mode: ParseMode,        // Strict, Greedy, GreedyOnceStarted
    pub first_child_idx: u32,         // → index into child_ids table
    pub child_count: u16,
    pub first_terminator_idx: u32,    // → index into terminators table
    pub terminator_count: u16,
    pub template_idx: u32,            // → index into strings table
}
```

### GrammarTables Layout

```
GrammarTables {
    instructions: [GrammarInst; N]     // Main table, indexed by GrammarId
    child_ids:    [u32; ...]           // Flattened children for all grammars
    terminators:  [u32; ...]           // Flattened terminators
    strings:      [&str; ...]          // Ref names, keywords, templates
    aux_data:     [u32; ...]           // Extra data (delimiters, bracket types)
}
```

**Example**: A `Sequence([Ref("A"), Ref("B")])` at index 5:

```
instructions[5] = GrammarInst {
    variant: Sequence,
    first_child_idx: 12,    // children start at child_ids[12]
    child_count: 2,         // 2 children
    ...
}
child_ids[12] = 8   // GrammarId for Ref("A")
child_ids[13] = 9   // GrammarId for Ref("B")
```

### Why Tables?

- **20 bytes/rule** vs ~376 bytes for `Arc<Grammar>` enum
- **Zero allocations** — all data is `&'static`
- **Cache-friendly** — sequential memory access
- **Generated** — Python builds the tables at build time

## Token

Represents a lexed SQL element:

```rust
pub struct Token {
    pub token_type: String,           // "keyword", "identifier", etc.
    pub raw: String,                   // Original text
    pub pos_marker: Option<PositionMarker>,
    pub is_code: bool,
    pub is_whitespace: bool,
    pub matching_bracket_idx: Option<usize>,  // Pre-computed for O(1) lookup
    // ...
}
```

## LexMatcher

Defines how to recognize a token:

```rust
pub struct LexMatcher {
    pub name: String,
    pub mode: LexerMode,  // String, Regex, FancyRegex, or Function
    pub token_class_func: TokenGenerator,
    pub subdivider: Option<Box<LexMatcher>>,
    // ...
}
```

Matchers are tried in priority order; first match wins.

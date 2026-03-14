# sqlfluffrs_parser

Table-driven, iterative SQL parser.

## How the Lookup Tables Work

Grammar rules are stored as flat arrays, not tree structures. A `GrammarId` (u32) indexes into these tables:

```
┌─────────────────────────────────────────────────────────────────┐
│ GrammarTables                                                   │
├─────────────────────────────────────────────────────────────────┤
│ instructions: [Inst₀, Inst₁, Inst₂, Inst₃, ...]                │
│                  ↑                                              │
│                  └── GrammarId indexes here                     │
├─────────────────────────────────────────────────────────────────┤
│ child_ids: [3, 7, 2, 8, 9, 4, ...]                              │
│             ↑─────↑                                             │
│             └─────┴── Inst.first_child_idx + child_count        │
├─────────────────────────────────────────────────────────────────┤
│ strings: ["SelectStatement", "FROM", "keyword", ...]            │
│                ↑                                                │
│                └── Inst.template_idx indexes here               │
└─────────────────────────────────────────────────────────────────┘
```

**Looking up children of grammar 5:**
```rust
let inst = tables.instructions[5];
let children = &tables.child_ids[inst.first_child_idx .. inst.first_child_idx + inst.child_count];
// children = [3, 7] → these are GrammarIds to recurse into
```

**Looking up a Ref name:**
```rust
let inst = tables.instructions[grammar_id];
let name = tables.strings[inst.template_idx];  // "SelectStatementSegment"
```

## Iterative Parsing

Instead of recursive function calls (which can stack overflow on deep SQL), we use an explicit frame stack:

```rust
while let Some(frame) = stack.top() {
    match (frame.grammar_variant, frame.state) {
        (Sequence, Initial) => {
            // Push first child onto stack
            stack.push(child_frame);
            frame.state = WaitingForChild(0);
        }
        (Sequence, WaitingForChild(i)) => {
            // Child finished, accumulate result
            frame.accumulated.push(child_result);
            if more_children {
                stack.push(next_child_frame);
                frame.state = WaitingForChild(i + 1);
            } else {
                frame.state = Done;
            }
        }
        (_, Done) => {
            stack.pop();
            // Return result to parent frame
        }
    }
}
```

Each grammar variant (Sequence, OneOf, Delimited, etc.) has handlers for its state transitions.

## Grammar Variants

| Variant | Behavior |
|---------|----------|
| `Sequence` | Match children in order: A then B then C |
| `OneOf` | Try children until one matches |
| `AnyNumberOf` | Match 0+ of any child, in any order |
| `Delimited` | Match element-delimiter-element pattern |
| `Bracketed` | Match `(` content `)` with pre-computed bracket pairs |
| `Ref` | Look up named rule by string, recurse |
| `StringParser` | Match literal token text |
| `TypedParser` | Match token by type (keyword, identifier) |

## Key Optimizations

### Simple Hints

For `OneOf`, avoid trying branches that can't possibly match:

```rust
// If first token is "SELECT", skip branches that must start with "INSERT"
if !branch.can_start_with(current_token) {
    continue;  // Prune this branch
}
```

### Bracket Pre-matching

During lexing, we compute matching bracket indices:

```rust
token[3] = "("   matching_bracket_idx = Some(7)
token[7] = ")"   matching_bracket_idx = Some(3)
```

Parser uses this for O(1) "find closing bracket" instead of scanning.

### Terminator Caching

When parsing `Delimited`, we check "is this token a terminator?" repeatedly. Cache these results:

```rust
terminator_cache: HashMap<(position, grammar_id), bool>
```

## Output

Parser returns `MatchResult`—a lightweight description of what matched:

```rust
MatchResult {
    matched_slice: 0..5,           // Token indices
    matched_class: "SelectStatement",
    child_matches: [...],          // Nested results
}
```

Call `.apply(tokens)` to materialize into a `Node` tree when needed. This lets Python build its own segment types from match results.

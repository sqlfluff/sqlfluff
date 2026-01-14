# sqlfluffrs_lexer

Converts SQL text into tokens.

## How It Works

```
Input: "SELECT id FROM users"

For each position:
  1. Try matchers in priority order (keywords, operators, identifiers, etc.)
  2. First match wins → consume that text
  3. Build Token with position info
  4. Repeat until EOF

Output: [Token("SELECT"), Token("id"), Token("FROM"), Token("users")]
```

## Matcher Priority

Matchers from `sqlfluffrs_dialects` are ordered so that:

1. Block comments `/* ... */`
2. Line comments `-- ...`
3. Quoted strings `'...'`, `"..."`
4. Numbers
5. Multi-char operators `>=`, `<>`
6. Single-char operators `=`, `<`
7. Keywords (case-insensitive)
8. Identifiers
9. Whitespace

First match wins—so `>=` is matched as one operator, not `>` then `=`.

## Subdividing

Some tokens get split after initial matching:

```
'hello world' → [SingleQuote, StringContent, SingleQuote]
```

The `subdivider` field on `LexMatcher` handles this.

## Template Blocks

For Jinja-templated SQL, `BlockTracker` assigns UUIDs to template regions:

```
{% for x in items %}  ← enter block, push UUID
  SELECT {{ x }}
{% endfor %}          ← exit block, pop UUID
```

This ensures template blocks get consistent identities across lexer passes.

## Output

```rust
pub fn lex(&self, input: LexInput) -> (Vec<Token>, Vec<SQLLexError>)
```

Returns both tokens and errors—lexing continues past errors for better diagnostics.

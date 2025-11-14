# Rust Components - AI Assistant Instructions

This file provides guidance for SQLFluff's Rust components.

## Overview

The `sqlfluffrs/` directory contains an **experimental Rust implementation** of performance-critical SQLFluff components. This is an ongoing effort to accelerate lexing and parsing operations while maintaining compatibility with the Python implementation.

## Project Status

**Current state**: Experimental and under development

**Goals:**
- Accelerate lexing performance (tokenization)
- Speed up parsing for large SQL files
- Maintain API compatibility with Python components
- Provide optional Rust-based acceleration for production users

**Not a replacement**: The Rust components are designed to work alongside Python, not replace the entire codebase.

## Structure

```
sqlfluffrs/
├── Cargo.toml              # Rust package manifest
├── pyproject.toml          # Python packaging for Rust extension
├── LICENSE.md              # License
├── README.md               # Rust component README
├── py.typed                # Type stub marker
├── sqlfluffrs.pyi          # Python type stubs for Rust extension
└── src/                    # Rust source code
    ├── lib.rs              # Library root
    ├── python.rs           # Python bindings (PyO3)
    ├── lexer.rs            # Lexer implementation
    ├── marker.rs           # Position markers
    ├── matcher.rs          # Pattern matching
    ├── regex.rs            # Regex utilities
    ├── slice.rs            # String slicing
    ├── config/             # Configuration handling
    ├── dialect/            # Dialect definitions
    ├── templater/          # Template handling
    └── token/              # Token types
```

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

The Rust components are exposed to Python via **PyO3**:

```bash
# Build and install Python extension
cd sqlfluffrs
pip install -e .

# Or from repository root
pip install -e ./sqlfluffrs/
```

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

**Basic example** in `src/python.rs`:

```rust
use pyo3::prelude::*;

#[pyfunction]
fn tokenize(sql: &str) -> PyResult<Vec<String>> {
    let tokens = internal_tokenize(sql)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
    Ok(tokens)
}

#[pymodule]
fn sqlfluffrs(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(tokenize, m)?)?;
    Ok(())
}
```

**Python usage:**
```python
import sqlfluffrs

tokens = sqlfluffrs.tokenize("SELECT * FROM users")
print(tokens)  # ['SELECT', '*', 'FROM', 'users']
```

### Type Stubs

Provide Python type hints in `sqlfluffrs.pyi`:

```python
from typing import List

def tokenize(sql: str) -> List[str]: ...
```

## Architecture

### Lexer

The Rust lexer (`src/lexer.rs`) tokenizes SQL strings:

```rust
pub struct Lexer {
    config: LexerConfig,
}

impl Lexer {
    pub fn new(config: LexerConfig) -> Self {
        Lexer { config }
    }

    pub fn lex(&self, sql: &str) -> Result<Vec<Token>, LexError> {
        // Tokenization logic
    }
}
```

### Matcher

Pattern matching for grammar rules (`src/matcher.rs`):

```rust
pub trait Matcher {
    fn matches(&self, tokens: &[Token]) -> bool;
}

pub struct SequenceMatcher {
    matchers: Vec<Box<dyn Matcher>>,
}
```

### Dialect Support

Rust dialects mirror Python dialects (`src/dialect/`):

```rust
pub struct Dialect {
    name: String,
    reserved_keywords: HashSet<String>,
    unreserved_keywords: HashSet<String>,
}
```

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

### Optimization

- Use `cargo build --release` for production builds
- Profile with `cargo flamegraph` or `perf`
- Prefer zero-copy operations where possible
- Use `&str` over `String` when ownership not needed

## Development Workflow

### Making Changes

1. **Edit Rust code** in `src/`
2. **Run tests:**
   ```bash
   cargo test
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
   pip install -e .
   ```
6. **Test Python integration:**
   ```python
   import sqlfluffrs
   # Test Rust functions from Python
   ```

### Syncing with Python

After changing Rust lexer/parser:

1. **Regenerate dialect bindings:**
   ```bash
   # From repository root
   source .venv/bin/activate
   python utils/rustify.py build
   ```

2. **Test against Python test suite:**
   ```bash
   tox -e py312
   ```

## Common Tasks

### Adding New Lexer Pattern

1. Edit `src/lexer.rs`
2. Add pattern matching logic
3. Write tests
4. Run `cargo test`
5. Update Python bindings if needed

### Updating Dialect

1. Edit `src/dialect/<dialect>.rs`
2. Update keyword lists or grammar
3. Sync with Python via `utils/rustify.py build`
4. Test with `cargo test`

### Exposing New Function to Python

1. Add function in appropriate Rust module
2. Add Python binding in `src/python.rs`:
   ```rust
   #[pyfunction]
   fn my_new_function(input: &str) -> PyResult<String> {
       // Implementation
   }
   ```
3. Register in module:
   ```rust
   #[pymodule]
   fn sqlfluffrs(_py: Python, m: &PyModule) -> PyResult<()> {
       m.add_function(wrap_pyfunction!(my_new_function, m)?)?;
       Ok(())
   }
   ```
4. Add type stub to `sqlfluffrs.pyi`:
   ```python
   def my_new_function(input: str) -> str: ...
   ```
5. Rebuild and test

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

- Experimental and incomplete
- Not all Python features implemented
- Performance gains vary by use case
- May have compatibility issues with some dialects

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

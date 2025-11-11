# Quick Start: Running Rust Tests

## Stack Size Requirement
The Rust parser requires 16MB stack size due to deep grammar initialization chains.
**Always use:**

```bash
RUST_MIN_STACK=16777216 cargo test
RUST_MIN_STACK=16777216 cargo run
```

## Quick Commands

### Run all tests
```bash
cd sqlfluffrs
RUST_MIN_STACK=16777216 cargo test
```

### Run specific test
```bash
cd sqlfluffrs
RUST_MIN_STACK=16777216 cargo test test_name
```

### Run with debug logging
```bash
cd sqlfluffrs
RUST_MIN_STACK=16777216 RUST_LOG=debug cargo test test_name -- --nocapture
```

### Build library
```bash
cd sqlfluffrs
RUST_MIN_STACK=16777216 cargo build --lib
```

### Run benchmarks
```bash
cd sqlfluffrs
RUST_MIN_STACK=16777216 cargo bench
```

## CI/CD Integration

Add to `.github/workflows/*.yml`:
```yaml
env:
  RUST_MIN_STACK: 16777216

jobs:
  test:
    steps:
      - name: Run Rust tests
        run: cargo test
        env:
          RUST_MIN_STACK: 16777216
```

## IDE/Editor Configuration

### VS Code (launch.json)
```json
{
  "configurations": [
    {
      "type": "lldb",
      "request": "launch",
      "name": "Debug Rust Tests",
      "cargo": {
        "args": ["test", "--no-run"]
      },
      "env": {
        "RUST_MIN_STACK": "16777216"
      }
    }
  ]
}
```

### CLion
Add environment variable in Run Configuration:
```
RUST_MIN_STACK=16777216
```

## Makefile Shortcut

Add to `sqlfluffrs/Makefile`:
```makefile
export RUST_MIN_STACK=16777216

.PHONY: test build bench

test:
	cargo test

build:
	cargo build --lib

bench:
	cargo bench
```

Then simply:
```bash
cd sqlfluffrs
make test
```

## Why 16MB?

The deep cascade of lazy grammar initialization requires:
- ~2MB for the deepest grammar chains
- ~4-8MB for safety margin with complex dialects
- 16MB provides comfortable headroom for future growth

Default stack (2MB) is too small → causes stack overflow during grammar loading.

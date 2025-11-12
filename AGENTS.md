# SQLFluff AI Coding Assistant Instructions

## Project Overview

SQLFluff is a dialect-flexible SQL linter and auto-fixer supporting 25+ SQL dialects including T-SQL, PostgreSQL, BigQuery, MySQL, Snowflake, and more. The project is written primarily in **Python** with an experimental **Rust** component for performance optimization.

**Core Architecture:**
- **Parser-first design**: SQL is lexed → parsed into segment trees → linted by rules → optionally auto-fixed
- **Dialect inheritance**: Each dialect extends ANSI base grammar using `.replace()` to override specific segments
- **Segment-based AST**: Everything is a `BaseSegment` subclass forming a recursive tree structure
- **Rule crawlers**: Rules traverse segment trees to find violations and generate `LintFix` objects

## Repository Structure

```
/
├── src/sqlfluff/              # Main Python package (see src/sqlfluff/AGENTS.md)
│   ├── dialects/              # SQL dialect definitions (see src/sqlfluff/dialects/AGENTS.md)
│   ├── rules/                 # Linting rules by category
│   ├── core/                  # Parser, lexer, config infrastructure
│   ├── cli/                   # Command-line interface
│   └── api/                   # Public Python API
├── sqlfluffrs/                # Experimental Rust components (see sqlfluffrs/AGENTS.md)
├── test/                      # Test suite (see test/AGENTS.md)
│   ├── fixtures/              # Test data (SQL files, YAML expected outputs)
│   ├── dialects/              # Dialect parsing tests
│   └── rules/                 # Rule testing infrastructure
├── docs/                      # Sphinx documentation (see docs/AGENTS.md)
├── plugins/                   # Pluggable extensions (dbt templater, examples)
├── utils/                     # Build and development utilities
└── examples/                  # API usage examples
```

## Universal Conventions

### Language Support
- **Python**: 3.9 minimum, 3.12 recommended for development, 3.13 supported
- **Rust**: Experimental, used for performance-critical lexing/parsing

### Code Quality Standards
- **Formatting**: Black (Python), rustfmt (Rust)
- **Linting**: Ruff + Flake8 (Python), clippy (Rust)
- **Type Checking**: Mypy strict mode (Python)
- **Pre-commit hooks**: Run before all commits via `.venv/bin/pre-commit run --all-files`

### Testing Philosophy
- All tests must pass before merging
- Test coverage should reach 100%
- Use YAML fixtures for dialect/rule tests
- Mirror source structure in test directories

### Commit Messages
- Keep messages clear and descriptive
- Reference issue numbers when applicable
- Use conventional commit style when appropriate

## Core Commands

### Environment Setup
```bash
# Create development environment (first time)
tox -e py312 --devenv .venv
source .venv/bin/activate

# Always activate before working in a new terminal
source .venv/bin/activate
```

### Testing
```bash
# Run full test suite
tox

# Run specific Python version tests
tox -e py312

# Run with coverage
tox -e cov-init,py312,cov-report,linting,mypy

# Quick dialect test (after adding SQL fixtures)
python test/generate_parse_fixture_yml.py -d tsql
```

### Quality Checks
```bash
# Run all pre-commit checks (format, lint, type check)
.venv/bin/pre-commit run --all-files

# Individual checks
black src/ test/                # Format
ruff check src/ test/           # Lint
mypy src/sqlfluff/              # Type check
```

### Building
```bash
# Install package in editable mode (done automatically by tox --devenv)
pip install -e .

# Install plugins
pip install -e plugins/sqlfluff-templater-dbt/
```

## Architecture Principles

### Layer Separation
The codebase enforces strict architectural boundaries (via `importlinter` in `pyproject.toml`):
- `core` layer cannot import `api`, `cli`, `dialects`, `rules`, or `utils`
- `api` layer cannot import `cli`
- Dependencies flow: `linter` → `rules` → `parser` → `errors`/`types` → `helpers`

### Immutability
- Segments are immutable - never modify directly
- Use `.copy()` or `LintFix` mechanisms for changes
- Parser creates fresh tree structures

### Lazy Loading
- Dialects loaded via `dialect_selector()` or `load_raw_dialect()`
- Never import dialect modules directly
- Supports dynamic dialect discovery

## Development Workflows

### Adding Dialect Features
1. Create `.sql` test files in `test/fixtures/dialects/<dialect>/`
2. Run `python test/generate_parse_fixture_yml.py -d <dialect>` to generate expected `.yml` outputs
3. Implement grammar in `src/sqlfluff/dialects/dialect_<name>.py`
4. Use `dialect.replace()` to override inherited ANSI segments
5. Verify: `tox -e generate-fixture-yml -- -d <dialect>`

See `src/sqlfluff/dialects/AGENTS.md` for detailed dialect development guide.

### Adding Linting Rules
1. Create rule class in appropriate category under `src/sqlfluff/rules/`
2. Define metadata: `code`, `name`, `description`, `groups`
3. Implement `_eval(context: RuleContext) -> Optional[LintResult]`
4. Add YAML test cases to `test/fixtures/rules/std_rule_cases/<category>.yml`
5. Run: `tox -e py312 -- test/rules/yaml_test_cases_test.py -k <rule_code>`

### Fixing Parser Issues
1. Identify failing SQL in `test/fixtures/dialects/<dialect>/*.sql`
2. Run fixture generator to see current parse tree
3. Modify grammar segments in dialect file
4. Regenerate fixtures to verify
5. Check that changes don't break other dialects: `tox -e generate-fixture-yml`

### Documentation Updates
1. Edit source files in `docs/source/`
2. Build locally: `cd docs && make html`
3. View: `open docs/build/html/index.html`
4. Verify links and formatting

See `docs/AGENTS.md` for documentation-specific guidelines.

## Component-Specific Instructions

For detailed instructions on specific components, refer to:
- **Python source code**: `src/sqlfluff/AGENTS.md`
- **Dialect development**: `src/sqlfluff/dialects/AGENTS.md`
- **Rust components**: `sqlfluffrs/AGENTS.md`
- **Testing**: `test/AGENTS.md`
- **Documentation**: `docs/AGENTS.md`

## Common Pitfalls

### Parser Development
- ❌ Don't modify segment instances directly (immutable)
- ✅ Use `.copy()` or `LintFix` for modifications
- ❌ Don't import dialect modules directly
- ✅ Use `dialect_selector()` for lazy loading
- ❌ Don't use class references in grammar definitions
- ✅ Use `Ref("SegmentName")` string references

### Testing
- ❌ Don't put dialect-specific tests in ANSI fixtures
- ✅ Place tests in the most specific applicable dialect
- ❌ Don't forget to regenerate YAML fixtures after grammar changes
- ✅ Always run `generate_parse_fixture_yml.py` after parser edits
- ❌ Don't create monolithic test files
- ✅ Organize by segment type (e.g., `create_table.sql`, `select_statement.sql`)

### Code Quality
- ❌ Don't skip type hints
- ✅ All public functions need type annotations
- ❌ Don't bypass pre-commit hooks
- ✅ Run `.venv/bin/pre-commit run --all-files` before committing
- ❌ Don't violate import layer boundaries
- ✅ Check `pyproject.toml` importlinter contracts

## Configuration

SQLFluff uses `.sqlfluff` files (INI format) for configuration:
- Placed in project root or any parent directory
- Key sections: `[sqlfluff]`, `[sqlfluff:rules]`, `[sqlfluff:rules:<rule_code>]`
- Programmatic: `FluffConfig.from_root(overrides={...})`

## Plugin System

- Plugins live in `plugins/` directory
- Installed via `pip install -e plugins/<plugin-name>/`
- Entry points defined in plugin's `pyproject.toml`
- Examples: `sqlfluff-templater-dbt`, `sqlfluff-plugin-example`

## Quick Reference

### Most Common Tasks

```bash
# Add new SQL test case for a dialect
echo "SELECT TOP 10 * FROM users;" > test/fixtures/dialects/tsql/top_clause.sql
python test/generate_parse_fixture_yml.py -d tsql

# Test a specific rule
tox -e py312 -- test/rules/yaml_test_cases_test.py -k AL01

# Check code quality before commit
.venv/bin/pre-commit run --all-files

# Run tests for just the parser module
tox -e py312 -- test/core/parser/

# Check dialect parsing without writing fixtures
sqlfluff parse test.sql --dialect tsql
```

### Performance Tips
- Use `-k` flag in pytest to filter tests during development
- Run `generate-fixture-yml` with `-d <dialect>` to test one dialect
- Use `tox -e py312` instead of full `tox` during iteration
- Activate venv to run `pytest` directly (faster than tox for single runs)

---

**Remember**: The goal is to maintain SQLFluff as a high-quality, reliable SQL linting tool. Take time to understand the architecture, write comprehensive tests, and follow the established patterns. When in doubt, look at existing similar implementations in the codebase.

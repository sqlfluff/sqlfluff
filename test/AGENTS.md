# Testing - AI Assistant Instructions

This file provides testing guidelines for SQLFluff development.

## Testing Philosophy

SQLFluff uses comprehensive testing with:
- **High coverage requirements**: Changes should reach 100% coverage
- **Multiple test types**: Unit tests, integration tests, fixture-based tests
- **Automated verification**: All tests run via tox and CI/CD

## Test Organization

```
test/
├── conftest.py                    # Shared pytest fixtures
├── api/                           # API tests
│   ├── simple_test.py
│   └── classes_test.py
├── cli/                           # CLI tests
│   ├── commands_test.py
│   └── formatters_test.py
├── core/                          # Core component tests
│   ├── parser/
│   │   ├── grammar_test.py
│   │   └── segments_test.py
│   └── rules/
│       └── base_test.py
├── dialects/                      # Dialect parsing tests
│   ├── ansi_test.py
│   ├── tsql_test.py
│   └── postgres_test.py
├── rules/                         # Rule testing
│   ├── yaml_test_cases_test.py    # YAML-based rule tests
│   └── std_fix_auto_test.py       # Auto-fix integration tests
└── fixtures/                      # Test data
    ├── dialects/
    │   ├── ansi/
    │   │   ├── select_statement.sql
    │   │   └── select_statement.yml
    │   └── tsql/
    │       ├── select_top.sql
    │       └── select_top.yml
    └── rules/
        └── std_rule_cases/
            ├── aliasing.yml
            └── layout.yml
```

## Test Frameworks

### Pytest

Primary test framework for all Python tests.

**Key features:**
- Test discovery: `*_test.py` files
- Fixtures: Reusable test setup in `conftest.py`
- Markers: Categorize tests (`@pytest.mark.dbt`, `@pytest.mark.integration`)
- Parametrization: Run same test with different inputs

**Basic test structure:**
```python
import pytest
from sqlfluff.core import Linter

def test_simple_parsing():
    """Test basic SQL parsing."""
    linter = Linter(dialect="ansi")
    result = linter.parse_string("SELECT * FROM users")
    assert result.tree is not None
    assert result.violations == []
```

### Fixtures (Pytest)

**Common fixtures** in `conftest.py`:
- `default_config`: Default SQLFluff configuration
- `fresh_ansi_dialect`: Clean ANSI dialect instance
- `caplog`: Capture log output

**Using fixtures:**
```python
@pytest.fixture
def tsql_linter():
    """Provide T-SQL linter for tests."""
    return Linter(dialect="tsql")

def test_with_fixture(tsql_linter):
    """Test using fixture."""
    result = tsql_linter.parse_string("SELECT TOP 10 * FROM users")
    assert result.tree is not None
```

### Test Markers

**Built-in markers:**
```python
@pytest.mark.dbt
def test_dbt_templater():
    """Test requiring dbt installation."""
    pass

@pytest.mark.integration
def test_full_workflow():
    """Integration test spanning multiple components."""
    pass

@pytest.mark.parametrize("sql,expected", [
    ("SELECT * FROM t", True),
    ("SELECT", False),
])
def test_multiple_cases(sql, expected):
    """Test with multiple inputs."""
    result = is_valid_sql(sql)
    assert result == expected
```

## Dialect Testing

### SQL Fixture Files

Located in `test/fixtures/dialects/<dialect>/`:

```sql
-- test/fixtures/dialects/tsql/select_top.sql
SELECT TOP 10 * FROM users;

SELECT TOP (10) PERCENT * FROM products;

SELECT TOP 5 WITH TIES * FROM orders ORDER BY total_amount DESC;
```

**Best practices:**
- One file per segment type or feature
- Multiple test cases per file covering variations
- Use descriptive filenames
- Include comments explaining edge cases

### YAML Expected Outputs

Generated automatically by `generate_parse_fixture_yml.py`:

```yaml
# test/fixtures/dialects/tsql/select_top.yml
- file:
    statement:
    - select_statement:
      - keyword: SELECT
      - top_clause:
        - keyword: TOP
        - numeric_literal: '10'
      - whitespace: ' '
      - select_clause_element:
        - wildcard_expression:
          - wildcard_identifier:
            - star: '*'
      # ... rest of parse tree
```

**Workflow:**
1. Create `.sql` file with test cases
2. Run `python test/generate_parse_fixture_yml.py -d <dialect>`
3. Script generates `.yml` with current parse tree
4. Review `.yml` to verify correctness
5. Commit both `.sql` and `.yml` files

### Generating Fixtures

```bash
# Activate environment
source .venv/bin/activate

# Generate for specific dialect
python test/generate_parse_fixture_yml.py -d tsql

# Generate for all dialects (slow!)
python test/generate_parse_fixture_yml.py

# Using tox
tox -e generate-fixture-yml -- -d tsql
```

### Dialect Test Files

Beyond fixtures, write explicit tests in `test/dialects/<dialect>_test.py`:

```python
"""Tests specific to T-SQL dialect."""
import pytest
from sqlfluff.core import Linter

class TestTSQLDialect:
    """T-SQL dialect tests."""

    @pytest.fixture
    def linter(self):
        """Provide T-SQL linter."""
        return Linter(dialect="tsql")

    def test_top_clause(self, linter):
        """Test TOP clause parsing."""
        sql = "SELECT TOP 10 * FROM users"
        result = linter.parse_string(sql)

        # Verify parsing succeeded
        assert result.tree is not None

        # Find TOP clause in tree
        top_clause = result.tree.get_child("top_clause")
        assert top_clause is not None

    def test_table_hint(self, linter):
        """Test table hint WITH (NOLOCK)."""
        sql = "SELECT * FROM users WITH (NOLOCK)"
        result = linter.parse_string(sql)

        assert result.tree is not None
        hints = result.tree.get_child("table_hint")
        assert hints is not None
```

## Rule Testing

### YAML Test Cases

Primary method for testing rules. Located in `test/fixtures/rules/std_rule_cases/`:

```yaml
# test/fixtures/rules/std_rule_cases/aliasing.yml
rule: AL01

test_implicit_alias_fail:
  fail_str: SELECT * FROM users u

test_explicit_alias_pass:
  pass_str: SELECT * FROM users AS u

test_implicit_alias_fix:
  fail_str: SELECT * FROM users u
  fix_str: SELECT * FROM users AS u

test_with_config:
  fail_str: SELECT * FROM users AS u
  configs:
    rules:
      aliasing.table:
        aliasing: implicit
```

**YAML structure:**
- `rule`: Rule code being tested
- `test_*`: Test case name (descriptive)
- `fail_str`: SQL that should fail the rule
- `pass_str`: SQL that should pass the rule
- `fix_str`: Expected SQL after auto-fix (optional)
- `configs`: Override configuration (optional)

### Running Rule Tests

```bash
# Test specific rule
tox -e py312 -- test/rules/yaml_test_cases_test.py -k AL01

# Test all rules
tox -e py312 -- test/rules/yaml_test_cases_test.py

# Test auto-fixing
tox -e py312 -- test/rules/std_fix_auto_test.py

# Direct pytest (faster during development)
pytest test/rules/yaml_test_cases_test.py -k AL01 -v
```

### Rule Unit Tests

For complex rule logic, write explicit tests:

```python
"""Tests for Rule AL01."""
import pytest
from sqlfluff.core.rules import RuleContext
from sqlfluff.rules.aliasing.AL01 import Rule_AL01

class TestRuleAL01:
    """Tests for implicit alias rule."""

    def test_implicit_alias_detected(self):
        """Test that implicit alias is detected."""
        rule = Rule_AL01()
        # Create test context and segment
        # ... test implementation
        result = rule._eval(context)
        assert result is not None
        assert "implicit" in result.description.lower()
```

## Coverage Testing

### Running with Coverage

```bash
# Coverage for specific module
pytest test/core/parser/ --cov=src/sqlfluff/core/parser --cov-report=term-missing

# Coverage for rules (shows uncovered lines)
pytest test/rules/ --cov=src/sqlfluff/rules --cov-report=term-missing:skip-covered

# Full coverage report
pytest test/ --cov=src/sqlfluff --cov-report=term-missing

# HTML coverage report (creates htmlcov/ directory)
pytest test/ --cov=src/sqlfluff --cov-report=html
open htmlcov/index.html

# Using tox
tox -e cov-init,py312,cov-report
```

### Coverage Requirements

- New code should have high test coverage (100%)
- Changes should not decrease overall coverage
- Critical paths (parser, rules) require comprehensive coverage

## Test Commands Reference

### Quick Testing During Development

```bash
# Single test file
pytest test/core/parser/grammar_test.py -v

# Single test function
pytest test/core/parser/grammar_test.py::test_sequence_matching -v

# Tests matching pattern
pytest test/rules/ -k AL01 -v

# Specific dialect fixtures
python test/generate_parse_fixture_yml.py -d tsql

# Run and stop on first failure
pytest test/core/ -x

# Show print statements
pytest test/core/ -s

# Verbose output with captured logs
pytest test/core/ -v --log-cli-level=DEBUG
```

### Full Test Suite

```bash
# Run all tests for Python 3.12
tox -e py312

# Run with coverage
tox -e cov-init,py312,cov-report

# Run linting and type checking
tox -e linting,mypy

# Full suite (all Python versions, linting, type checking)
tox
```

### Test-Driven Development Workflow

1. **Write failing test:**
   ```python
   def test_new_feature():
       """Test new feature."""
       result = new_feature("input")
       assert result == "expected"
   ```

2. **Run test to confirm failure:**
   ```bash
   pytest test/core/new_feature_test.py::test_new_feature -v
   ```

3. **Implement feature**

4. **Run test to confirm success:**
   ```bash
   pytest test/core/new_feature_test.py::test_new_feature -v
   ```

5. **Run broader tests to check for regressions:**
   ```bash
   pytest test/core/ -v
   ```

6. **Check coverage:**
   ```bash
   pytest test/core/ --cov=src/sqlfluff/core --cov-report=term-missing
   ```

## Test Data Management

### SQL Test Files

**Location**: `test/fixtures/dialects/<dialect>/*.sql`

**Guidelines:**
- Descriptive filenames: `select_top.sql`, `merge_statement.sql`
- Multiple test cases per file
- Include edge cases and variations
- Add comments for complex cases

**Example:**
```sql
-- test/fixtures/dialects/tsql/select_top.sql

-- Basic TOP clause
SELECT TOP 10 * FROM users;

-- TOP with parentheses
SELECT TOP (10) * FROM users;

-- TOP with PERCENT
SELECT TOP 10 PERCENT * FROM users;

-- TOP with WITH TIES (requires ORDER BY)
SELECT TOP 5 WITH TIES * FROM orders ORDER BY amount DESC;
```

### YAML Expected Outputs

**Generated automatically** - do not edit manually unless absolutely necessary.

**Regenerate after grammar changes:**
```bash
python test/generate_parse_fixture_yml.py -d <dialect>
```

### Rule Test YAML Files

**Location**: `test/fixtures/rules/std_rule_cases/<category>.yml`

**Categories:**
- `aliasing.yml`: Aliasing rules (AL*)
- `layout.yml`: Layout rules (LT*)
- `capitalisation.yml`: Capitalisation rules (CP*)
- `convention.yml`: Convention rules (CV*)
- `structure.yml`: Structure rules (ST*)
- `references.yml`: Reference rules (RF*)

## Common Testing Patterns

### Testing Exceptions

```python
import pytest
from sqlfluff.core.errors import SQLParseError

def test_invalid_sql_raises():
    """Test that invalid SQL raises error."""
    with pytest.raises(SQLParseError):
        parse_invalid_sql("SELECT * FROM")
```

### Parametrized Tests

```python
@pytest.mark.parametrize("sql,expected_type", [
    ("SELECT * FROM users", "select_statement"),
    ("INSERT INTO users VALUES (1)", "insert_statement"),
    ("UPDATE users SET name = 'x'", "update_statement"),
])
def test_statement_types(sql, expected_type):
    """Test various statement types."""
    result = parse_sql(sql)
    assert result.tree.type == expected_type
```

### Fixture Parametrization

```python
@pytest.fixture(params=["ansi", "tsql", "postgres"])
def dialect_linter(request):
    """Provide linter for multiple dialects."""
    return Linter(dialect=request.param)

def test_across_dialects(dialect_linter):
    """Test behavior across multiple dialects."""
    result = dialect_linter.parse_string("SELECT * FROM users")
    assert result.tree is not None
```

---

**See also:**
- Root `AGENTS.md` for general project overview
- `src/sqlfluff/AGENTS.md` for Python coding standards
- `src/sqlfluff/dialects/AGENTS.md` for dialect development and testing

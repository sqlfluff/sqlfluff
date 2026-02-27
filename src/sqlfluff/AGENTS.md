# Python Source Code - AI Assistant Instructions

This file provides Python-specific development guidelines for SQLFluff's main source code.

## Python Standards

### Version Support
- **Minimum**: Python 3.9
- **Recommended for development**: Python 3.13
- **Maximum tested**: Python 3.14

### Code Style & Formatting

#### Black (Auto-formatter)
- Default settings (line length: 88 characters)
- Run: `black src/ test/`
- Automatically enforced via pre-commit hooks

#### Ruff (Linter)
- Fast Python linter with isort and pydocstyle integration
- Run: `ruff check src/ test/`
- Auto-fix: `ruff check --fix src/ test/`
- Checks import order, docstring style, common code smells

#### Flake8 (Additional Linting)
- Used with flake8-black plugin
- Configured in `pyproject.toml`

### Type Annotations

**Required for all public functions and methods:**

```python
from typing import Optional, Union, List, Dict, cast, TYPE_CHECKING

def parse_sql(sql: str, dialect: str = "ansi") -> Optional[BaseSegment]:
    """Parse SQL string into segment tree.

    Args:
        sql: SQL string to parse.
        dialect: SQL dialect name.

    Returns:
        Root segment or None if parsing fails.
    """
    pass
```

**Key Mypy settings** (strict mode enabled):
- `warn_unused_configs = true`
- `strict_equality = true`
- `no_implicit_reexport = true`

**Avoiding circular imports:**
```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlfluff.core.parser import BaseSegment
```

### Documentation Standards

**Google-style docstrings required:**

```python
def complex_function(param1: str, param2: int, flag: bool = False) -> Dict[str, Any]:
    """Short one-line description.

    Longer description explaining the purpose, behavior, and usage.
    Can span multiple lines when needed.

    Args:
        param1: Description of first parameter.
        param2: Description of second parameter.
        flag: Optional flag for special behavior. Defaults to False.

    Returns:
        Dictionary containing results with keys 'status', 'data', etc.

    Raises:
        ValueError: If param1 is empty.
        SQLParseError: If parsing fails.
    """
    pass
```

**Exceptions to docstring requirements:**
- Magic methods (e.g., `__init__`, `__str__`) - D105, D107 ignored
- Private methods may have simplified docstrings
- Test functions use descriptive names instead

### Import Organization

**Enforced order** (via Ruff isort):

```python
# 1. Standard library imports
import os
import sys
from typing import Optional

# 2. Third-party imports
import click
import yaml

# 3. First-party imports (sqlfluff packages)
from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules import BaseRule
```

**Import linter contracts** (in `pyproject.toml`):
- `core` cannot import from `api`, `cli`, `dialects`, `rules`, `utils`
- `api` cannot import from `cli`
- Use specific imports: `from module import SpecificClass` (not `import *`)

## Architecture & Design Patterns

### Segment System

**All AST nodes inherit from `BaseSegment`:**

```python
from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.parser.grammar import Sequence, Ref, OneOf

class SelectStatementSegment(BaseSegment):
    """A SELECT statement."""

    type = "select_statement"
    match_grammar = Sequence(
        "SELECT",
        Ref("SelectClauseSegment"),
        Ref("FromClauseSegment", optional=True),
        Ref("WhereClauseSegment", optional=True),
    )
```

**Key principles:**
- Segments are **immutable** - never modify in place
- Use `.copy()` to create modified versions
- `match_grammar` defines parsing rules recursively
- Use `Ref("SegmentName")` not direct class references

### Rule System

**Rules inherit from `BaseRule`:**

```python
from sqlfluff.core.rules import BaseRule, LintResult, LintFix, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler

class Rule_AL01(BaseRule):
    """Implicit aliasing of table not allowed."""

    groups = ("all", "aliasing")
    crawl_behaviour = SegmentSeekerCrawler({"table_reference"})

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Evaluate rule against segment.

        Args:
            context: Rule context with segment and dialect info.

        Returns:
            LintResult if violation found, None otherwise.
        """
        if context.segment.has_implicit_alias:
            return LintResult(
                anchor=context.segment,
                fixes=[LintFix.replace(context.segment, [new_segments])],
            )
        return None
```

**Rule metadata:**
- `code`: Unique identifier (e.g., "AL01", "LT02")
- `name`: Human-readable name
- `description`: What the rule checks
- `groups`: Categories like "all", "core", "aliasing"
- `crawl_behaviour`: Which segment types to examine

### Dialect System

**Dialects use inheritance and replacement:**

```python
from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser.grammar import Sequence, Ref

# Load parent dialect
ansi_dialect = load_raw_dialect("ansi")
tsql_dialect = ansi_dialect.copy_as("tsql")

# Override specific segments
tsql_dialect.replace(
    SelectStatementSegment=Sequence(
        "SELECT",
        Ref("TopClauseSegment", optional=True),  # T-SQL specific
        Ref("SelectClauseSegment"),
        Ref("FromClauseSegment", optional=True),
    ),
)
```

**Never import dialects directly:**
```python
# ❌ Wrong
from sqlfluff.dialects.dialect_tsql import tsql_dialect

# ✅ Correct
from sqlfluff.core.dialects import dialect_selector
dialect = dialect_selector("tsql")
```

## Testing Patterns

### Test File Organization

```
test/
├── core/
│   ├── parser/
│   │   ├── grammar_test.py
│   │   └── segments_test.py
│   └── rules/
│       └── base_test.py
├── dialects/
│   └── tsql_test.py
└── rules/
    ├── yaml_test_cases_test.py
    └── std_fix_auto_test.py
```

**Naming convention**: `*_test.py` (enforced by pytest)

### Pytest Fixtures

**Use fixtures in `conftest.py`:**

```python
import pytest
from sqlfluff.core import FluffConfig

@pytest.fixture
def default_config():
    """Provide default SQLFluff config for tests."""
    return FluffConfig.from_root()

def test_parser_with_config(default_config):
    """Test parser using fixture."""
    assert default_config.get("dialect") == "ansi"
```

### Test Markers

```python
import pytest

@pytest.mark.dbt
def test_dbt_templater():
    """Test requiring dbt installation."""
    pass

@pytest.mark.integration
def test_full_parse_flow():
    """Integration test for complete parsing flow."""
    pass
```

## Common Commands

### Development Workflow

```bash
# Activate virtual environment
source .venv/bin/activate

# Run tests for specific module
pytest test/core/parser/ -v

# Run with coverage
pytest test/core/ --cov=src/sqlfluff/core --cov-report=term-missing

# Test specific function
pytest test/core/parser/grammar_test.py::test_sequence_matching -v

# Run type checking
mypy src/sqlfluff/

# Format and lint
black src/ test/
ruff check --fix src/ test/
```

### Installing Dependencies

```bash
# Install main package in editable mode
pip install -e .

# Install with development dependencies
pip install -e .[dev]

# Install specific plugin
pip install -e plugins/sqlfluff-templater-dbt/
```

## Performance Considerations

### Efficient Segment Tree Traversal

```python
# ✅ Good: Use crawlers for targeted traversal
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler

crawl_behaviour = SegmentSeekerCrawler({"select_statement", "insert_statement"})

# ❌ Bad: Manual recursive traversal
def find_all_selects(segment):
    results = []
    if segment.type == "select_statement":
        results.append(segment)
    for child in segment.segments:
        results.extend(find_all_selects(child))
    return results
```

### Lazy Evaluation

```python
# ✅ Good: Lazy loading
from sqlfluff.core.dialects import dialect_selector
dialect = dialect_selector("tsql")  # Loaded on demand

# ❌ Bad: Eager imports
from sqlfluff.dialects.dialect_tsql import tsql_dialect
```

## Debugging Tips

### Parser Debugging

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use parse debugging
from sqlfluff.core import Linter
linter = Linter(dialect="tsql")
parsed = linter.parse_string("SELECT * FROM users")
print(parsed.tree.stringify())  # View parse tree
```

### Rule Debugging

```bash
# Run single rule against SQL file
sqlfluff lint test.sql --rules AL01 -v

# Show fixes without applying
sqlfluff fix test.sql --rules AL01 --diff

# Parse and show tree structure
sqlfluff parse test.sql --dialect tsql
```

## Anti-Patterns to Avoid

```python
# ❌ Don't modify segments in place
segment.raw = "NEW VALUE"  # Segments are immutable!

# ✅ Use copy or LintFix
new_segment = segment.copy(raw="NEW VALUE")

# ❌ Don't import across architectural boundaries
from sqlfluff.cli import commands  # In core/ module - violation!

# ✅ Respect layer separation
# core/ should not import from cli/, api/, dialects/, rules/

# ❌ Don't use bare except
try:
    parse_sql(sql)
except:
    pass

# ✅ Catch specific exceptions
try:
    parse_sql(sql)
except SQLParseError as e:
    logger.error(f"Parse failed: {e}")

# ❌ Don't use mutable default arguments
def process_segments(segments=[]):  # Bug waiting to happen!
    segments.append(new_segment)

# ✅ Use None and initialize
def process_segments(segments=None):
    if segments is None:
        segments = []
    segments.append(new_segment)
```

---

**See also:**
- `src/sqlfluff/dialects/AGENTS.md` for dialect-specific development
- `test/AGENTS.md` for testing conventions and commands
- Root `AGENTS.md` for general project overview

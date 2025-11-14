# Documentation - AI Assistant Instructions

This file provides guidelines for building and maintaining SQLFluff documentation.

## Documentation System

SQLFluff uses **Sphinx** for documentation generation with:
- **Source**: `docs/source/` (reStructuredText files)
- **Build output**: `docs/build/` (HTML, generated)
- **Live docs**: https://docs.sqlfluff.com
- **Auto-generated content**: API docs, rule reference, dialect lists

## Documentation Structure

```
docs/
├── source/                        # Documentation source files
│   ├── conf.py                    # Sphinx configuration
│   ├── index.rst                  # Homepage
│   ├── gettingstarted.rst         # Getting started guide
│   ├── why_sqlfluff.rst          # Project overview
│   ├── inthewild.rst             # Real-world usage
│   ├── jointhecommunity.rst      # Community info
│   ├── configuration/            # Configuration docs
│   │   ├── index.rst
│   │   └── setting_configuration.rst
│   ├── guides/                   # Developer guides
│   │   ├── index.rst
│   │   ├── first_contribution.rst
│   │   └── dialect_development.rst
│   ├── reference/                # API and rule reference
│   │   ├── index.rst
│   │   ├── rules.rst
│   │   └── api.rst
│   ├── production/               # Production deployment
│   ├── _static/                  # Static assets (CSS, images)
│   ├── _ext/                     # Sphinx extensions
│   └── _partials/                # Reusable doc fragments
├── build/                        # Generated HTML (gitignored)
├── Makefile                      # Build commands (Unix)
├── make.bat                      # Build commands (Windows)
├── requirements.txt              # Doc build dependencies
└── README.md                     # Documentation README

../generate-auto-docs.py          # Script to generate auto-docs
```

## Building Documentation Locally

### Setup

```bash
# Activate virtual environment
source .venv/bin/activate

# Install documentation dependencies
pip install -r docs/requirements.txt
```

### Building HTML Docs

```bash
# Navigate to docs directory
cd docs

# Build HTML (Unix/Linux/Mac)
make html

# Build HTML (Windows)
make.bat html

# View built documentation
open build/html/index.html  # macOS
xdg-open build/html/index.html  # Linux
# Or manually open docs/build/html/index.html in browser
```

### Clean Build

```bash
cd docs

# Clean previous build
make clean

# Build fresh
make html
```

### Live Reload During Development

For rapid iteration, use `sphinx-autobuild`:

```bash
# Install sphinx-autobuild
pip install sphinx-autobuild

# Run live-reload server
cd docs
sphinx-autobuild source build/html

# Open browser to http://127.0.0.1:8000
# Docs rebuild automatically on file changes
```

## Documentation Format

### reStructuredText (RST)

SQLFluff docs use RST format (`.rst` files).

**Basic syntax:**

```rst
Page Title
==========

Section Heading
---------------

Subsection
~~~~~~~~~~

**Bold text**

*Italic text*

``inline code``

`Link text <https://example.com>`_

- Bullet list item
- Another item

1. Numbered list
2. Second item

.. code-block:: sql

   SELECT * FROM users
   WHERE active = 1;

.. code-block:: python

   from sqlfluff.core import Linter
   linter = Linter(dialect="tsql")

.. note::
   This is a note box.

.. warning::
   This is a warning box.
```

### Cross-References

```rst
Link to another doc:
:doc:`gettingstarted`

Link to section:
:ref:`configuration-label`

Link to Python class:
:class:`sqlfluff.core.Linter`

Link to function:
:func:`sqlfluff.lint`
```

## Documentation Types

### User-Facing Documentation

**Getting Started** (`gettingstarted.rst`):
- Installation instructions
- Quick start examples
- Basic usage patterns

**Configuration** (`configuration/`):
- Configuration file format
- Available settings
- Dialect-specific config

**Rules Reference** (`reference/rules.rst`):
- Auto-generated from rule metadata
- Rule descriptions, examples, configuration options
- **Updated automatically** via `generate-auto-docs.py`

### Developer Documentation

**Guides** (`guides/`):
- First contribution walkthrough
- Dialect development guide
- Rule development guide
- Architecture overview

**API Reference** (`reference/api.rst`):
- Auto-generated from docstrings
- Python API documentation
- Class and function references

### Production Documentation

**Production** (`production/`):
- CI/CD integration
- Performance tuning
- Deployment best practices

## Auto-Generated Documentation

### Generating Auto-Docs

Some documentation is generated from source code:

```bash
# Generate auto-documentation (rules, dialects, etc.)
python docs/generate-auto-docs.py

# Build docs after generation
cd docs
make html
```

**What gets auto-generated:**
- Rule reference (from rule metadata)
- Dialect list (from available dialects)
- API documentation (from docstrings)

### Rule Documentation

Rules are documented via their metadata:

```python
class Rule_AL01(BaseRule):
    """Implicit aliasing of table not allowed.

    **Anti-pattern**

    Using implicit alias for tables:

    .. code-block:: sql

        SELECT * FROM users u

    **Best practice**

    Use explicit AS keyword:

    .. code-block:: sql

        SELECT * FROM users AS u
    """

    groups = ("all", "aliasing")
    # ... rest of rule
```

Docstring is extracted and added to rule reference docs.

## Documentation Style Guide

### Writing Style

- **Clear and concise**: Use simple language
- **Active voice**: "Run the command" not "The command should be run"
- **Present tense**: "SQLFluff parses SQL" not "SQLFluff will parse SQL"
- **Examples**: Include code examples for every feature
- **User perspective**: Write from user's point of view

### Code Examples

**Always include:**
- Context (what the example demonstrates)
- Complete, runnable code
- Expected output when relevant

**SQL examples:**
```rst
.. code-block:: sql

   -- Anti-pattern: implicit alias
   SELECT * FROM users u;

.. code-block:: sql

   -- Best practice: explicit alias
   SELECT * FROM users AS u;
```

**Python examples:**
```rst
.. code-block:: python

   from sqlfluff.core import Linter

   linter = Linter(dialect="tsql")
   result = linter.lint_string("SELECT * FROM users")
   print(result.violations)
```

**Shell examples:**
```rst
.. code-block:: bash

   # Lint a SQL file
   sqlfluff lint query.sql

   # Fix issues automatically
   sqlfluff fix query.sql
```

### Sections and Headers

Use consistent header hierarchy:

```rst
Page Title (Top Level)
======================

Major Section
-------------

Subsection
~~~~~~~~~~

Sub-subsection
^^^^^^^^^^^^^^
```

### Links and References

**External links:**
```rst
See the `official documentation <https://docs.sqlfluff.com>`_ for details.
```

**Internal cross-references:**
```rst
For configuration options, see :doc:`configuration/index`.

As described in :ref:`dialect-development`, each dialect...
```

**Define reference labels:**
```rst
.. _dialect-development:

Dialect Development
-------------------

This section covers dialect development...
```

## Checking Documentation Quality

### Sphinx Warnings

Sphinx warns about issues during build:

```bash
cd docs
make html

# Look for warnings like:
# WARNING: document isn't included in any toctree
# WARNING: undefined label: some-label
# ERROR: Unknown directive type "cod-block"  (typo!)
```

Fix all warnings before committing documentation changes.

### Link Checking

```bash
cd docs

# Check for broken links
make linkcheck

# Review output for HTTP errors, redirects, broken anchors
```

### Spell Checking

SQLFluff uses `codespell` for spell checking:

```bash
# Run from repository root
codespell docs/source/

# Or via pre-commit
.venv/bin/pre-commit run codespell --all-files
```

## Documentation Workflow

### Adding New Documentation

1. **Create or edit `.rst` file** in `docs/source/`
2. **Add to table of contents** (toctree) in parent `index.rst`:
   ```rst
   .. toctree::
      :maxdepth: 2

      existing_page
      new_page
   ```
3. **Build and review:**
   ```bash
   cd docs
   make clean html
   open build/html/index.html
   ```
4. **Check for warnings** during build
5. **Run link checker:**
   ```bash
   make linkcheck
   ```
6. **Commit both source and auto-generated files** if applicable

### Updating Existing Documentation

1. **Edit `.rst` file**
2. **Rebuild docs:**
   ```bash
   cd docs
   make html
   ```
3. **Review changes** in browser
4. **Check for new warnings**
5. **Commit changes**

### Adding Code Examples

1. **Create example in `examples/`** directory (optional):
   ```python
   # examples/08_new_feature.py
   from sqlfluff.core import Linter

   linter = Linter(dialect="tsql")
   result = linter.lint_string("SELECT * FROM users")
   print(result.violations)
   ```

2. **Reference in documentation:**
   ```rst
   .. literalinclude:: ../../examples/08_new_feature.py
      :language: python
      :linenos:
   ```

3. **Or embed directly:**
   ```rst
   .. code-block:: python

      from sqlfluff.core import Linter
      linter = Linter(dialect="tsql")
   ```

## Common Documentation Tasks

### Document New Rule

1. **Add docstring to rule class** with anti-pattern and best practice
2. **Regenerate docs:**
   ```bash
   python docs/generate-auto-docs.py
   ```
3. **Build and verify:**
   ```bash
   cd docs && make html
   ```

### Document New Dialect

1. **Add dialect overview** to `reference/dialects.rst` or create new file
2. **Include supported features** and known limitations
3. **Provide examples** of dialect-specific syntax
4. **Update auto-generated dialect list:**
   ```bash
   python docs/generate-auto-docs.py
   ```

### Add Tutorial/Guide

1. **Create new `.rst` file** in `docs/source/guides/`
2. **Add to toctree** in `docs/source/guides/index.rst`
3. **Include step-by-step instructions** with examples
4. **Build and test** all commands/code in tutorial

## Sphinx Configuration

Configuration in `docs/source/conf.py`:

**Key settings:**
- `project`: "SQLFluff"
- `extensions`: Sphinx extensions used
- `html_theme`: Documentation theme
- `html_static_path`: Static assets directory

**Custom extensions** in `docs/source/_ext/`:
- Custom directives or roles
- Auto-documentation generators

## Testing Documentation Build in CI

Documentation builds are tested in CI/CD:
- Ensures no Sphinx warnings or errors
- Validates all links
- Checks for spelling errors

**Local pre-check before committing:**
```bash
# Build docs
cd docs && make clean html

# Check links
make linkcheck

# Spell check
cd .. && codespell docs/source/

# Review any warnings/errors
```

---

**See also:**
- Root `AGENTS.md` for general project overview
- `CONTRIBUTING.md` for contribution guidelines
- [Sphinx documentation](https://www.sphinx-doc.org/) for RST syntax reference

#!/usr/bin/env python3
"""Generate Internal API documentation in Markdown format for VitePress.

This script introspects the internal SQLFluff classes and functions used by
plugin and rule authors, parses their Google-style docstrings, and writes
Markdown pages + a VitePress sidebar JSON to reference/internals/.
"""

import inspect
import json
import re
import textwrap
from pathlib import Path
from typing import Any, Callable, get_type_hints

from sqlfluff.core.config import loader as config_loader
from sqlfluff.core.config.fluffconfig import FluffConfig
from sqlfluff.core.rules.base import BaseRule, LintResult
from sqlfluff.core.rules.context import RuleContext
from sqlfluff.core.rules.crawlers import (
    BaseCrawler,
    RootOnlyCrawler,
    SegmentSeekerCrawler,
)
from sqlfluff.core.rules.fix import LintFix
from sqlfluff.utils.functional import raw_file_slice_predicates, segment_predicates
from sqlfluff.utils.functional.raw_file_slices import RawFileSlices
from sqlfluff.utils.functional.segments import Segments
from sqlfluff.utils.reflow import ReflowSequence
from sqlfluff.utils.reflow.elements import ReflowBlock, ReflowPoint

# ── per-page introductory text ────────────────────────────────────────────────

PAGE_INTROS: dict[str, str] = {
    "config": """\
# Configuration & `FluffConfig`

> This section is for plugin and rule authors who use the Python API.
> For everyday configuration options see the [Configuration docs](/configuration/).

Internally, SQLFluff merges all discovered config files into a single
[`FluffConfig`](#fluffconfig) object which is threaded through the linting
pipeline. The `sqlfluff.core.config.loader` module exposes functions to build
the nested dict that `FluffConfig` consumes.

The nested dict mirrors `.sqlfluff` key paths split on `:`. For example:

```ini
[sqlfluff:rules:capitalisation.keywords]
capitalisation_policy = lower
```

becomes:

```python
{"rules": {"capitalisation.keywords": {"capitalisation_policy": "lower"}}}
```

Source:
[`sqlfluff/core/config/`](https://github.com/sqlfluff/sqlfluff/tree/main/src/sqlfluff/core/config)
""",
    "functional": """\
# Functional Traversal API

> This section is for rule authors who need to navigate the parse tree.

The `sqlfluff.utils.functional` submodules provide a higher-level API for
working with parse-tree segments and raw file slices. Rules using these classes
can express traversal and filtering logic more concisely than working with the
raw segment tree directly.

Source:
[`sqlfluff/utils/functional/`](https://github.com/sqlfluff/sqlfluff/tree/main/src/sqlfluff/utils/functional)
""",
    "reflow": """\
# Reflow API

> This section is for rule authors who produce whitespace or layout fixes.

Many SQLFluff rules involve spacing and layout — enforcing a particular
whitespace style or adding/removing code while respecting the layout
configuration. The `sqlfluff.utils.reflow` module provides centralised
utilities so that all layout rules behave consistently.

Rules should use [`ReflowSequence`](#reflowsequence) rather than constructing
[`LintFix`](/reference/internals/rules#lintfix) objects manually; it returns
ready-to-use fix lists and respects the user's layout configuration
automatically.

Source:
[`sqlfluff/utils/reflow/`](https://github.com/sqlfluff/sqlfluff/tree/main/src/sqlfluff/utils/reflow)
""",
    "rules": """\
# Rules Base API

> This section is for contributors writing new built-in rules or plugin rules.

SQLFluff rules are Python classes that subclass [`BaseRule`](#baserule). The
linter crawls the parse tree and calls each rule's `_eval()` method, which
returns zero or more [`LintResult`](#lintresult) objects. Each `LintResult`
may carry [`LintFix`](#lintfix) objects describing how to auto-correct the
violation.

The crawler passed to `BaseRule.crawl_behaviour` controls which segments
`_eval()` is called on — see [`SegmentSeekerCrawler`](#segmentseekerrawler)
and [`RootOnlyCrawler`](#rootonlycrawler).

Source:
[`sqlfluff/core/rules/`](https://github.com/sqlfluff/sqlfluff/tree/main/src/sqlfluff/core/rules)
""",
}

# ── docstring parsing (shared with generate-api-docs.py) ─────────────────────


def clean_rst_markup(text: str) -> str:
    """Remove RST-style markup from text and convert to Markdown equivalents."""
    if not text:
        return text
    # Cross-reference roles
    text = re.sub(r":obj:`([^`]+)`", r"`\1`", text)
    text = re.sub(r":class:`([^`]+)`", r"`\1`", text)
    text = re.sub(r":func:`([^`]+)`", r"`\1`", text)
    text = re.sub(r":meth:`([^`]+)`", r"`\1`", text)
    text = re.sub(r":attr:`([^`]+)`", r"`\1`", text)
    text = re.sub(r":mod:`([^`]+)`", r"`\1`", text)
    text = re.sub(r":py:[a-z]+:`([^`]+)`", r"`\1`", text)
    text = re.sub(r":ref:`([^`]+)`", r"\1", text)
    text = re.sub(r":code:`([^`]+)`", r"`\1`", text)

    # RST code blocks  →  fenced Markdown
    def _code_block(m: re.Match) -> str:
        lang = (m.group(1) or "").strip()
        lang = {
            "py3": "python",
            "py": "python",
            "cfg": "ini",
            "bash": "bash",
            "sql": "sql",
            "text": "",
        }.get(lang, lang)
        # Extract indented body
        body_lines = []
        for line in m.group(2).splitlines():
            body_lines.append(line[4:] if line.startswith("    ") else line)
        return f"```{lang}\n" + "\n".join(body_lines).strip() + "\n```"

    text = re.sub(
        r"\.\.\s+code-block::\s*(\w*)\n\n((?:    .+\n?|\n)+)",
        _code_block,
        text,
    )
    # RST ``..`` directives: note/warning → VitePress containers
    text = re.sub(
        r"\.\.\s+note::\s*\n\n((?:    .+\n?|\n)+)",
        lambda m: "::: info\n" + textwrap.dedent(m.group(1)).strip() + "\n:::\n",
        text,
    )
    text = re.sub(
        r"\.\.\s+warning::\s*\n\n((?:    .+\n?|\n)+)",
        lambda m: "::: warning\n" + textwrap.dedent(m.group(1)).strip() + "\n:::\n",
        text,
    )
    # Leftover bare ``.. something::`` directives — strip them
    text = re.sub(r"\.\.\s+\w+::[^\n]*\n", "", text)
    # RST ``double backtick`` → single backtick
    text = re.sub(r"``([^`]+)``", r"`\1`", text)
    return text


def parse_param_list(text: str) -> list[dict[str, str]]:
    """Parse Google-style parameter list into structured dicts."""
    if not text.strip():
        return []
    params: list[dict[str, str]] = []
    param_pattern = r"^\s*(\w+)\s*(?:\(([^)]+)\))?\s*:\s*(.+)$"
    current: dict[str, str] | None = None
    for line in text.split("\n"):
        m = re.match(param_pattern, line)
        if m:
            if current:
                params.append(current)
            current = {
                "name": m.group(1),
                "type": clean_rst_markup(m.group(2) or ""),
                "description": clean_rst_markup(m.group(3).strip()),
            }
        elif current and line.strip():
            current["description"] += " " + clean_rst_markup(line.strip())
    if current:
        params.append(current)
    return params


def parse_google_docstring(docstring: str) -> dict[str, Any]:
    """Parse a Google-style docstring into keyed sections."""
    if not docstring:
        return {}
    cleaned = inspect.cleandoc(docstring)
    sections: dict[str, Any] = {
        "description": "",
        "args": [],
        "returns": "",
        "raises": [],
        "examples": "",
        "note": "",
    }
    section_pattern = r"^(Args?|Returns?|Raises?|Examples?|Note):\s*$"
    lines = cleaned.split("\n")
    current_section = "description"
    current_content: list[str] = []

    def _flush(section: str, content: list[str]) -> None:
        text = "\n".join(content).strip()
        if section == "description":
            sections["description"] = clean_rst_markup(text)
        elif section in ("args", "raises"):
            sections[section] = parse_param_list(text)
        else:
            sections[section] = clean_rst_markup(text)

    for line in lines:
        m = re.match(section_pattern, line.strip())
        if m:
            _flush(current_section, current_content)
            key = m.group(1).lower().rstrip("s")
            current_section = {
                "arg": "args",
                "return": "returns",
                "raise": "raises",
                "example": "examples",
            }.get(key, key)
            current_content = []
        else:
            current_content.append(line)
    _flush(current_section, current_content)
    return sections


# ── type-hint formatting ──────────────────────────────────────────────────────


def format_type_hint(hint: Any) -> str:
    """Format a type hint for Markdown display."""
    if hint is None or hint is type(None):
        return "None"
    if isinstance(hint, str):
        return hint
    s = str(hint)
    s = s.replace("typing.", "")
    s = s.replace("<class '", "").replace("'>", "")
    s = re.sub(r"sqlfluff\.\w+(?:\.\w+)*\.", "", s)
    return s


# ── introspection helpers ─────────────────────────────────────────────────────


def _param_rows(params: list[dict], doc_args: list[dict]) -> list[dict]:
    """Merge inspect signature params with docstring arg descriptions."""
    doc_map = {p["name"]: p for p in doc_args}
    rows = []
    for p in params:
        name = p["name"]
        if name == "self":
            continue
        doc = doc_map.get(name, {})
        rows.append(
            {
                "name": name,
                "type": p.get("type") or doc.get("type", ""),
                "default": p.get("default", ""),
                "description": doc.get("description", ""),
            }
        )
    return rows


def _sig_params(obj: Any) -> list[dict]:
    """Return a list of {name, type, default} dicts from a callable's signature."""
    try:
        sig = inspect.signature(obj)
        hints = {}
        try:
            hints = get_type_hints(obj)
        except Exception:
            pass
        result = []
        for name, param in sig.parameters.items():
            if name == "self":
                continue
            ptype = (
                format_type_hint(hints[name])
                if name in hints
                else (
                    format_type_hint(param.annotation)
                    if param.annotation is not inspect.Parameter.empty
                    else ""
                )
            )
            default = ""
            if param.default is not inspect.Parameter.empty:
                default = (
                    "None"
                    if param.default is None
                    else (
                        f'"{param.default}"'
                        if isinstance(param.default, str)
                        else str(param.default)
                    )
                )
            result.append({"name": name, "type": ptype, "default": default})
        return result
    except (ValueError, TypeError):
        return []


def _return_type(obj: Any) -> str:
    try:
        hints = get_type_hints(obj)
        if "return" in hints:
            return format_type_hint(hints["return"])
        sig = inspect.signature(obj)
        if sig.return_annotation is not inspect.Signature.empty:
            return format_type_hint(sig.return_annotation)
    except Exception:
        pass
    return ""


# ── markdown rendering ────────────────────────────────────────────────────────


def _params_table(rows: list[dict]) -> list[str]:
    """Render a 4-column parameter table wrapped in a .params-table div.

    The div enables CSS to apply min-widths on wide viewports and a stacked
    definition-list layout on narrow ones, without touching other tables.
    """
    if not rows:
        return []
    lines = [
        "**Parameters:**\n",
        '<div class="params-table">\n',
        "| Parameter | Type | Default | Description |",
        "|:----------|:-----|:--------|:------------|",
    ]
    for r in rows:
        name = f"`{r['name']}`"
        typ = f"`{r['type']}`" if r.get("type") else " "
        default = f"`{r['default']}`" if r.get("default") else " "
        desc = r.get("description", "").replace("\n", " ").strip() or " "
        lines.append(f"| {name} | {typ} | {default} | {desc} |")
    lines.append("\n</div>\n")
    return lines


def render_function(name: str, obj: Callable, heading: str = "###") -> list[str]:
    """Render a single function as Markdown."""
    doc = parse_google_docstring(inspect.getdoc(obj) or "")
    sig_params = _sig_params(obj)
    param_rows = _param_rows(sig_params, doc.get("args", []))
    ret = _return_type(obj)

    # Build signature string
    parts = []
    for p in sig_params:
        parts.append(
            f"    {p['name']}={p['default']}" if p["default"] else f"    {p['name']}"
        )
    sig = f"{name}(\n" + ",\n".join(parts) + "\n)" if parts else f"{name}()"
    if ret:
        sig += f" → {ret}"

    lines: list[str] = [f"{heading} `{name}`\n", f"```python\n{sig}\n```\n"]

    if doc.get("description"):
        lines.append(f"{doc['description']}\n")

    lines.extend(_params_table(param_rows))

    if doc.get("returns") or ret:
        lines.append("**Returns:**\n")
        desc = doc.get("returns") or "See return type."
        lines.append(f"`{ret}` — {desc}\n" if ret else f"{desc}\n")

    if doc.get("raises"):
        lines.append("**Raises:**\n")
        for exc in doc["raises"]:
            lines.append(
                f"- `{exc.get('type', 'Exception')}`: {exc.get('description', '')}"
            )
        lines.append("")

    if doc.get("examples"):
        ex = doc["examples"].strip()
        lines.append("**Example:**\n")
        lines.append(ex if ex.startswith("```") else f"```python\n{ex}\n```\n")

    if doc.get("note"):
        lines.append(f"::: info\n{doc['note']}\n:::\n")

    return lines


def render_class(
    cls: type, heading: str = "##", method_heading: str = "###"
) -> list[str]:
    """Render a class (constructor + public methods) as Markdown."""
    doc = parse_google_docstring(inspect.getdoc(cls) or "")
    lines: list[str] = [f"{heading} `{cls.__name__}`\n"]

    if doc.get("description"):
        lines.append(f"{doc['description']}\n")

    # Constructor params
    init_params = _sig_params(cls.__init__)
    param_rows = _param_rows(init_params, doc.get("args", []))
    lines.extend(_params_table(param_rows))

    if doc.get("note"):
        lines.append(f"::: info\n{doc['note']}\n:::\n")

    # Public methods
    methods = []
    for mname, mobj in inspect.getmembers(cls):
        if mname.startswith("_"):
            continue
        if inspect.isfunction(mobj) or inspect.ismethod(mobj):
            methods.append((mname, mobj))

    if methods:
        lines.append(f"{method_heading} Methods\n")
        for mname, mobj in methods:
            lines.extend(render_function(mname, mobj, heading=method_heading + "#"))

    return lines


# ── page builders ─────────────────────────────────────────────────────────────


def build_config_page() -> str:
    """Build reference/internals/config.md."""
    lines: list[str] = [PAGE_INTROS["config"]]

    lines.append("## Loader functions\n")
    loader_whitelist = [
        ("load_config_string", config_loader.load_config_string),
        ("load_config_file", config_loader.load_config_file),
        ("load_config_resource", config_loader.load_config_resource),
        ("load_config_up_to_path", config_loader.load_config_up_to_path),
    ]
    for fname, fobj in loader_whitelist:
        lines.extend(render_function(fname, fobj, heading="###"))

    lines.extend(render_class(FluffConfig, heading="##", method_heading="###"))
    return "\n".join(lines)


def build_functional_page() -> str:
    """Build reference/internals/functional.md."""
    lines: list[str] = [PAGE_INTROS["functional"]]

    lines.extend(render_class(Segments, heading="##", method_heading="###"))

    lines.append("## `segment_predicates` functions\n")
    lines.append(
        "These predicate functions are passed to `Segments.select()` and similar "
        "methods to filter segments by their properties.\n"
    )
    for fname, fobj in inspect.getmembers(segment_predicates, inspect.isfunction):
        if not fname.startswith("_"):
            lines.extend(render_function(fname, fobj, heading="###"))

    lines.extend(render_class(RawFileSlices, heading="##", method_heading="###"))

    lines.append("## `raw_file_slice_predicates` functions\n")
    lines.append(
        "Predicate functions for use with `RawFileSlices.select()`, mirroring "
        "the role of `segment_predicates` for the raw slice layer.\n"
    )
    for fname, fobj in inspect.getmembers(
        raw_file_slice_predicates, inspect.isfunction
    ):
        if not fname.startswith("_"):
            lines.extend(render_function(fname, fobj, heading="###"))

    return "\n".join(lines)


def build_reflow_page() -> str:
    """Build reference/internals/reflow.md."""
    lines: list[str] = [PAGE_INTROS["reflow"]]
    for cls in [ReflowSequence, ReflowPoint, ReflowBlock]:
        lines.extend(render_class(cls, heading="##", method_heading="###"))
    return "\n".join(lines)


def build_rules_page() -> str:
    """Build reference/internals/rules.md."""
    lines: list[str] = [PAGE_INTROS["rules"]]
    for cls in [
        BaseRule,
        LintResult,
        LintFix,
        RuleContext,
        BaseCrawler,
        SegmentSeekerCrawler,
        RootOnlyCrawler,
    ]:
        lines.extend(render_class(cls, heading="##", method_heading="###"))
    return "\n".join(lines)


def build_index_page() -> str:
    """Build reference/internals/index.md."""
    return """\
---
outline: [2, 3]
---

# Internal API

The modules documented here are primarily useful for people who are:

- Developing **plugins** or **custom rules** that interact with SQLFluff at a
  deeper level.
- **Contributing** to the SQLFluff codebase itself.

As these docs cover less frequently accessed internals, not all modules are
fully documented here. Reading this alongside the docstrings and comments
directly in the
[SQLFluff codebase on GitHub](https://github.com/sqlfluff/sqlfluff/tree/main/src/sqlfluff)
is recommended.

## Modules

| Module | Description |
|--------|-------------|
| [Configuration & FluffConfig](./config) | `FluffConfig` class and config loading functions used by the Python API. |
| [Functional Traversal API](./functional) | Higher-level API for navigating parse trees in rules. |
| [Reflow API](./reflow) | Centralised utilities for whitespace and layout rules. |
| [Rules Base API](./rules) | `BaseRule`, `LintResult`, `LintFix`, `RuleContext`, and crawlers. |
"""


# ── sidebar config ────────────────────────────────────────────────────────────


def build_sidebar() -> dict[str, Any]:
    """Build the VitePress sidebar configuration for the internals section."""
    return {
        "text": "Internal API",
        "collapsed": True,
        "items": [
            {"text": "Overview", "link": "/reference/internals/"},
            {"text": "Configuration", "link": "/reference/internals/config"},
            {"text": "Functional API", "link": "/reference/internals/functional"},
            {"text": "Reflow API", "link": "/reference/internals/reflow"},
            {"text": "Rules Base", "link": "/reference/internals/rules"},
        ],
    }


# ── entry point ───────────────────────────────────────────────────────────────


def main() -> int:
    """Generate all internal API Markdown pages and the sidebar config."""
    script_dir = Path(__file__).parent
    docs_dir = script_dir.parent
    output_dir = docs_dir / "reference" / "internals"
    output_dir.mkdir(parents=True, exist_ok=True)

    pages = {
        "index": build_index_page,
        "config": build_config_page,
        "functional": build_functional_page,
        "reflow": build_reflow_page,
        "rules": build_rules_page,
    }

    print("Generating internal API documentation...")
    for slug, builder in pages.items():
        print(f"  Writing {slug}.md ...")
        content = builder()
        (output_dir / f"{slug}.md").write_text(content, encoding="utf-8")

    sidebar_path = docs_dir / ".vitepress" / "sidebar-internals.json"
    print("  Writing sidebar-internals.json ...")
    sidebar_path.write_text(
        json.dumps(build_sidebar(), indent=2) + "\n", encoding="utf-8"
    )

    print(f"✓ Internal API docs written to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

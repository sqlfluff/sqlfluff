#!/usr/bin/env python3
"""Shared utilities for VitePress documentation generation scripts.

Used by generate-api-docs.py and generate-internals-docs.py.
"""

import inspect
import re
import textwrap
from typing import Any


def clean_rst_markup(text: str) -> str:
    """Remove RST-style markup from text and convert to Markdown equivalents."""
    if not text:
        return text
    # Cross-reference roles → inline code or plain text
    text = re.sub(r":obj:`([^`]+)`", r"`\1`", text)
    text = re.sub(r":class:`([^`]+)`", r"`\1`", text)
    text = re.sub(r":func:`([^`]+)`", r"`\1`", text)
    text = re.sub(r":meth:`([^`]+)`", r"`\1`", text)
    text = re.sub(r":attr:`([^`]+)`", r"`\1`", text)
    text = re.sub(r":mod:`([^`]+)`", r"`\1`", text)
    text = re.sub(r":py:[a-z]+:`([^`]+)`", r"`\1`", text)
    text = re.sub(r":ref:`([^`]+)`", r"\1", text)
    text = re.sub(r":code:`([^`]+)`", r"`\1`", text)

    # RST code blocks → fenced Markdown
    def _code_block(m: re.Match) -> str:  # type: ignore[type-arg]
        lang = (m.group(1) or "").strip()
        lang = {
            "py3": "python",
            "py": "python",
            "cfg": "ini",
            "bash": "bash",
            "sql": "sql",
            "text": "",
        }.get(lang, lang)
        body_lines = []
        for line in m.group(2).splitlines():
            body_lines.append(line[4:] if line.startswith("    ") else line)
        return f"```{lang}\n" + "\n".join(body_lines).strip() + "\n```"

    text = re.sub(
        r"\.\.\s+code-block::\s*(\w*)\n\n((?:    .+\n?|\n)+)",
        _code_block,
        text,
    )
    # RST directives: note/warning → VitePress containers
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
    """Parse a Google-style parameter block into a list of dicts.

    Each dict has keys: name, type, description.
    """
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
    """Parse a Google-style docstring into keyed sections.

    Returns a dict with keys: description, args, returns, raises, examples, note.
    """
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
        elif section == "args":
            sections[section] = parse_param_list(text)
        elif section == "raises":
            # Google-style Raises entries are "ExceptionType: description".
            # parse_param_list puts the exception name in the `name` field;
            # remap it to `type` so renderers can use a consistent key.
            sections[section] = [
                {"type": p["name"], "description": p["description"]}
                for p in parse_param_list(text)
            ]
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


def format_type_hint(hint: Any) -> str:
    """Format a type hint object as a readable string for Markdown display."""
    if hint is None or hint is type(None):
        return "None"
    if isinstance(hint, str):
        return hint
    s = str(hint)
    s = s.replace("typing.", "")
    s = s.replace("<class '", "").replace("'>", "")
    # Strip any sqlfluff module prefix (handles multi-level paths)
    s = re.sub(r"sqlfluff\.\w+(?:\.\w+)*\.", "", s)
    return s


def params_table_rows(params: list[dict]) -> list[str]:
    """Render a 4-column parameter table wrapped in a .params-table div.

    The div lets CSS apply min-widths on wide viewports and a stacked
    definition-list layout on narrow ones without affecting other tables.
    """
    if not params:
        return []
    lines = [
        "**Parameters:**\n",
        '<div class="params-table">\n',
        "| Parameter | Type | Default | Description |",
        "|:----------|:-----|:--------|:------------|",
    ]
    for param in params:
        name = f"`{param['name']}`"
        ptype = f"`{param['type']}`" if param.get("type") else " "
        default = f"`{param['default']}`" if param.get("default") else " "
        # Escape bare pipes in plain-text description to avoid breaking the
        # table structure. Type/default are backtick-wrapped, so their pipes
        # are handled correctly by the parser without escaping.
        desc = (
            param.get("description", "").replace("\n", " ").strip().replace("|", "\\|")
            or " "
        )
        lines.append(f"| {name} | {ptype} | {default} | {desc} |")
    lines.append("\n</div>\n")
    return lines

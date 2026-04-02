#!/usr/bin/env python3
"""Generate rule documentation in Markdown format for VitePress.

This script:
1. Extracts all SQLFluff rules using the plugin system
2. Groups rules by bundle (layout, capitalisation, etc.)
3. Converts RST docstrings to Markdown using pandoc
4. Generates bundle-based markdown files
5. Creates VitePress sidebar configuration
"""

import inspect
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from sqlfluff.core.plugin.host import get_plugin_manager


def rst_to_markdown(rst_text: str) -> str:
    """Convert RST docstring to Markdown.

    Args:
        rst_text: RST-formatted text

    Returns:
        Markdown-formatted text
    """
    if not rst_text:
        return ""

    md = inspect.cleandoc(rst_text)

    # Convert RST admonitions first, before other substitutions that can
    # alter indentation and break block detection.
    md = _convert_rst_admonitions(md)

    # Convert reference-style RST links and strip link definition lines.
    md = _convert_rst_reference_links(md)

    # Convert RST links to markdown links.
    md = re.sub(r"`([^`<]+)\s+<(https?://[^>]+)>`_", r"[\1](\2)", md)
    md = re.sub(r"`([^`<]+)\s+<(https?://[^>]+)>`", r"[\1](\2)", md)

    # Convert rst inline roles/inline literals to markdown code spans.
    # Convert sqlfluff-specific refs before generic :ref: to avoid leaving a
    # stray ':sqlfluff' prefix behind.
    md = re.sub(r":sqlfluff:ref:`([^`]+)`", r"`\1`", md)
    md = re.sub(r":code:`([^`]+)`", r"`\1`", md)
    md = re.sub(r":ref:`([^`]+)`", r"`\1`", md)
    md = re.sub(r"``([^`]+)``", r"`\1`", md)

    # Normalize visible-space symbols to a clearer glyph.
    md = md.replace("•", "◦")

    # Convert rst list-table directives before code-block conversion so they
    # cannot be misinterpreted as loose markdown lists or paragraphs.
    md = _convert_rst_list_tables(md)

    # Convert RST code-block directives to Markdown code fences.
    md = _convert_rst_code_blocks(md)

    # Some sections may still be indented in the raw docstring even though they
    # are markdown structure rather than literal code. Normalize them so later
    # markdown parsing and config-table conversion remain stable.
    md = _normalize_indented_markdown_blocks(md)

    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip()


def _convert_rst_code_blocks(text: str) -> str:
    """Convert rst code-block directives to fenced markdown code blocks."""
    lines = text.split("\n")
    output: list[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]
        match = re.match(r"^\.\.\s+code-block::\s*([\w+-]+)?\s*$", line)
        if not match:
            output.append(line)
            i += 1
            continue

        language = (match.group(1) or "").strip()
        if language == "cfg":
            language = "ini"

        i += 1

        # Consume block lines (blank lines and indented lines).
        # Some generated docstrings can contain later markdown-ish sections
        # which are still indented in the raw text. Stop before those so they
        # don't get swallowed into the fenced code block.
        block_lines: list[str] = []
        while i < len(lines):
            current = lines[i]

            if _should_terminate_rst_code_block(block_lines, current):
                break

            if current == "" or current.startswith((" ", "\t")):
                block_lines.append(current)
                i += 1
                continue
            break

        # Drop rst option lines like ':force:' and preserve only content.
        content_lines: list[str] = []
        for block_line in block_lines:
            if re.match(r"^\s*:[a-zA-Z_][\w-]*:\s*$", block_line):
                continue
            content_lines.append(block_line)

        # Trim leading/trailing blank lines from content.
        while content_lines and not content_lines[0].strip():
            content_lines.pop(0)
        while content_lines and not content_lines[-1].strip():
            content_lines.pop()

        # Dedent based on minimum indentation for non-empty lines.
        min_indent = min(
            (
                len(content_line) - len(content_line.lstrip())
                for content_line in content_lines
                if content_line.strip()
            ),
            default=0,
        )
        dedented_lines = [
            content_line[min_indent:] if content_line.strip() else ""
            for content_line in content_lines
        ]
        # Improve readability of visible-space examples in code samples.
        dedented_lines = [line.replace("•", "◦") for line in dedented_lines]
        code_content = "\n".join(dedented_lines)

        output.append(f"```{language}")
        output.append(code_content)
        output.append("```")

    return "\n".join(output)


def _should_terminate_rst_code_block(block_lines: list[str], current_line: str) -> bool:
    """Return whether an indented line should terminate a converted code block."""
    if not block_lines or not current_line.startswith((" ", "\t")):
        return False

    if block_lines[-1] != "":
        return False

    stripped = current_line.strip()
    if not stripped:
        return False

    return bool(
        re.match(r"^\*\*[^*]+\*\*$", stripped)
        or stripped.startswith("|")
        or stripped.startswith(":::")
        or stripped.startswith(".. ")
        or re.match(r"^#{1,6}\s", stripped)
    )


def _normalize_indented_markdown_blocks(text: str) -> str:
    """Dedent markdown structure lines that should not remain as code blocks."""
    lines = text.split("\n")
    output: list[str] = []
    dedenting = False

    for line in lines:
        stripped = line.strip()

        if dedenting:
            if line.startswith("    "):
                output.append(line[4:])
                continue
            if line == "":
                output.append(line)
                continue
            dedenting = False

        if line.startswith("    ") and _is_markdown_structure_line(stripped):
            output.append(line[4:])
            dedenting = True
            continue

        output.append(line)

    return "\n".join(output)


def _is_markdown_structure_line(stripped_line: str) -> bool:
    """Return whether a stripped line looks like markdown structure."""
    return bool(
        re.match(r"^\*\*[^*]+\*\*$", stripped_line)
        or stripped_line.startswith("|")
        or stripped_line.startswith(":::")
        or stripped_line.startswith(".. ")
        or re.match(r"^[-*]\s+", stripped_line)
        or re.match(r"^#{1,6}\s", stripped_line)
    )


def _convert_rst_admonitions(text: str) -> str:
    """Convert rst note/warning/important directives to VitePress admonitions."""
    lines = text.split("\n")
    output: list[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]
        match = re.match(r"^\.\.\s+(note|warning|important)::\s*$", line, re.IGNORECASE)
        if not match:
            output.append(line)
            i += 1
            continue

        admonition_type = match.group(1).lower()
        i += 1

        # Optional blank line directly after the directive.
        if i < len(lines) and lines[i] == "":
            i += 1

        # Collect indented content lines, allowing blank lines between paragraphs.
        content_lines: list[str] = []
        while i < len(lines):
            current = lines[i]
            if current.startswith((" ", "\t")):
                content_lines.append(current)
                i += 1
                continue

            if current == "":
                next_nonempty = i + 1
                while next_nonempty < len(lines) and lines[next_nonempty] == "":
                    next_nonempty += 1

                if next_nonempty < len(lines) and lines[next_nonempty].startswith(
                    (" ", "\t")
                ):
                    content_lines.append(current)
                    i += 1
                    continue

            break

        # Dedent content while preserving paragraph breaks.
        min_indent = min(
            (
                len(content_line) - len(content_line.lstrip())
                for content_line in content_lines
                if content_line.strip()
            ),
            default=0,
        )
        dedented_lines = [
            content_line[min_indent:] if content_line.strip() else ""
            for content_line in content_lines
        ]

        # Trim outer blank lines but preserve internal paragraph spacing.
        while dedented_lines and not dedented_lines[0].strip():
            dedented_lines.pop(0)
        while dedented_lines and not dedented_lines[-1].strip():
            dedented_lines.pop()

        content_text = "\n".join(dedented_lines)

        if admonition_type == "note":
            output.append("::: tip NOTE")
        elif admonition_type == "warning":
            output.append("::: warning WARNING")
        else:
            output.append("::: tip IMPORTANT")
        output.append(content_text)
        output.append(":::")

    return "\n".join(output)


def _convert_rst_list_tables(text: str) -> str:
    """Convert simple rst list-table directives to markdown tables."""
    lines = text.split("\n")
    output: list[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]
        if not re.match(r"^\.\.\s+list-table::\s*$", line):
            output.append(line)
            i += 1
            continue

        i += 1
        block_lines: list[str] = []
        while i < len(lines):
            current = lines[i]
            if current == "" or current.startswith((" ", "\t")):
                block_lines.append(current)
                i += 1
                continue
            break

        option_lines: list[str] = []
        content_lines: list[str] = []
        for block_line in block_lines:
            if re.match(r"^\s*:[a-zA-Z_][\w-]*:\s*.*$", block_line):
                option_lines.append(block_line)
            else:
                content_lines.append(block_line)

        header_rows = 1
        for option_line in option_lines:
            match = re.match(r"^\s*:header-rows:\s*(\d+)\s*$", option_line)
            if match:
                header_rows = int(match.group(1))
                break

        while content_lines and not content_lines[0].strip():
            content_lines.pop(0)
        while content_lines and not content_lines[-1].strip():
            content_lines.pop()

        min_indent = min(
            (
                len(content_line) - len(content_line.lstrip())
                for content_line in content_lines
                if content_line.strip()
            ),
            default=0,
        )
        dedented_lines = [
            content_line[min_indent:] if content_line.strip() else ""
            for content_line in content_lines
        ]

        rows = _parse_rst_list_table_rows(dedented_lines)
        if not rows:
            output.append(line)
            output.extend(block_lines)
            continue

        header_index = 0 if header_rows > 0 else None
        if header_index is None:
            header = [f"Column {index + 1}" for index in range(len(rows[0]))]
            body_rows = rows
        else:
            header = rows[header_index]
            body_rows = rows[header_index + 1 :]

        column_count = max(len(header), *(len(row) for row in body_rows))
        header = _normalize_table_row(header, column_count)
        body_rows = [_normalize_table_row(row, column_count) for row in body_rows]

        output.append("| " + " | ".join(header) + " |")
        output.append("| " + " | ".join("---" for _ in range(column_count)) + " |")
        for row in body_rows:
            output.append("| " + " | ".join(row) + " |")
        output.append("")

    return "\n".join(output)


def _parse_rst_list_table_rows(lines: list[str]) -> list[list[str]]:
    """Parse dedented rst list-table rows into a row/cell structure."""
    rows: list[list[str]] = []
    current_row: list[list[str]] = []
    current_cell: list[str] | None = None

    for line in lines:
        row_match = re.match(r"^\*\s-\s(.*)$", line)
        if row_match:
            if current_row:
                rows.append([_collapse_table_cell(cell) for cell in current_row])
            current_row = [[row_match.group(1)]]
            current_cell = current_row[-1]
            continue

        cell_match = re.match(r"^\s+-\s(.*)$", line)
        if cell_match and current_row:
            current_row.append([cell_match.group(1)])
            current_cell = current_row[-1]
            continue

        if current_cell is not None:
            current_cell.append(line)

    if current_row:
        rows.append([_collapse_table_cell(cell) for cell in current_row])

    return rows


def _collapse_table_cell(cell_lines: list[str]) -> str:
    """Collapse multiline rst list-table cell content to a single markdown cell."""
    parts: list[str] = []
    for line in cell_lines:
        stripped = line.strip()
        if not stripped:
            continue
        parts.append(stripped)
    return " ".join(parts).replace("|", "\\|")


def _normalize_table_row(row: list[str], column_count: int) -> list[str]:
    """Pad a table row to the expected number of columns."""
    return row + [""] * (column_count - len(row))


def _convert_rst_reference_links(text: str) -> str:
    """Convert rst reference links and remove their definitions.

    Supports both forms:
    - .. _name: https://example.com
    - .. _`Link Name`: https://example.com
    and references:
    - name_
    - `Link Name`_
    """
    link_defs: dict[str, str] = {}

    def collect_definition(match: re.Match[str]) -> str:
        link_name = match.group(1) or match.group(2)
        link_url = match.group(3)
        if link_name:
            link_defs[link_name] = link_url
        return ""

    definition_pattern = r"^\.\.\s+_(?:`([^`]+)`|([^\s:]+)):\s+(\S+)\s*$"
    text = re.sub(definition_pattern, collect_definition, text, flags=re.MULTILINE)

    def replace_backtick_ref(match: re.Match[str]) -> str:
        link_text = match.group(1)
        link_url = link_defs.get(link_text)
        if link_url:
            return f"[{link_text}]({link_url})"
        return link_text

    text = re.sub(r"`([^`]+)`_", replace_backtick_ref, text)

    def replace_plain_ref(match: re.Match[str]) -> str:
        link_text = match.group(1)
        link_url = link_defs.get(link_text)
        if link_url:
            return f"[{link_text}]({link_url})"
        return match.group(0)

    text = re.sub(r"\b([A-Za-z0-9][A-Za-z0-9_.-]*)_\b", replace_plain_ref, text)

    return text


def get_bundle_name(bundle_key: str) -> str:
    """Get display name for a bundle."""
    # Capitalize first letter of bundle name
    return bundle_key.capitalize()


def format_configuration_section(markdown_text: str) -> str:
    """Convert Configuration section from list format to markdown table.

    Also removes duplicate metadata (Name, Aliases, Groups) that appears in docstrings
    since we now show this in a metadata table at the top of each rule.

    Looks for patterns like:
    **Configuration**
    -   `option_name`: Description text. Must be one of `[values]`.

    And converts to a markdown table format.
    """
    # Remove duplicate metadata lines from docstring
    # These appear as **Name**: `value`, **Aliases**: `value`, **Groups**: `value`
    # Handle both single-line and multi-line variations
    markdown_text = re.sub(
        r"\*\*Name\*\*:\s*`[^`]+`\s*\n+", "", markdown_text, flags=re.IGNORECASE
    )
    markdown_text = re.sub(
        r"\*\*Aliases\*\*:\s*`[^`]+(?:`,\s*`[^`]+)*`\s*\n+",
        "",
        markdown_text,
        flags=re.IGNORECASE,
    )
    markdown_text = re.sub(
        r"\*\*Groups\*\*:\s*`[^`]+(?:`,\s*`[^`]+)*`\s*\n+",
        "",
        markdown_text,
        flags=re.IGNORECASE,
    )

    # Remove "This rule is sqlfluff fix compatible" line
    # (redundant with Auto-fixable in table)
    markdown_text = re.sub(
        r"This rule is `sqlfluff fix` compatible\.\s*\n+",
        "",
        markdown_text,
        flags=re.IGNORECASE,
    )

    # Pattern to match Configuration section with bullet points
    config_pattern = r"\*\*Configuration\*\*\s*\n\n((?:[-*]\s+`[^`]+`:[^\n]+\n?)+)"

    def replace_config(match):
        config_text = match.group(1)

        # Parse each configuration option
        # Pattern: -   `option_name`: Description. Must be one of `[values]`.
        option_pattern = r"[-*]\s+`([^`]+)`:\s+([^\n]+)"
        options = re.findall(option_pattern, config_text)

        if not options:
            return match.group(0)  # Return original if can't parse

        # Build markdown table
        table = "**Configuration**\n\n"
        table += "| Option | Description |\n"
        table += "|--------|-------------|\n"

        for option_name, description in options:
            # Clean up description - remove extra spaces
            description = description.strip()
            # Escape pipe characters in description
            description = description.replace("|", "\\|")
            table += f"| `{option_name}` | {description} |\n"

        return table

    return re.sub(config_pattern, replace_config, markdown_text, flags=re.MULTILINE)


def generate_rules_documentation(output_dir: Path) -> dict[str, Any]:
    """Generate rule documentation markdown files.

    Returns:
        Dictionary with sidebar configuration for VitePress
    """
    # Get all rules via plugin system
    pm = get_plugin_manager()
    all_rules = []
    for plugin_rules in pm.hook.get_rules():
        all_rules.extend(plugin_rules)

    print(f"Found {len(all_rules)} rules")

    # Group by bundle (e.g., "layout", "capitalisation")
    rule_bundles = defaultdict(list)
    for rule in all_rules:
        # Extract bundle from rule name (e.g., "layout.spacing" -> "layout")
        bundle_name = rule.name.split(".")[0] if "." in rule.name else "other"
        rule_bundles[bundle_name].append(rule)

    # Sort bundles and rules within each bundle
    sorted_bundles = sorted(rule_bundles.items())

    sidebar_items = []

    # Generate markdown file for each bundle
    for bundle_key, rules in sorted_bundles:
        bundle_display = get_bundle_name(bundle_key)

        # Sort rules by code
        rules.sort(key=lambda r: r.code)

        # Generate markdown content
        md_content = f"# {bundle_display} Rules\n\n"
        md_content += (
            f"This section contains {len(rules)} rule(s) related to {bundle_key}.\n\n"
        )

        # Summary table
        md_content += "## Rule Summary\n\n"
        md_content += "| Code | Name | Aliases | Fix Compatible |\n"
        md_content += "|------|------|---------|----------------|\n"

        for rule in rules:
            aliases = ", ".join(f"`{a}`" for a in rule.aliases) if rule.aliases else "-"
            fix_icon = "✅" if rule.is_fix_compatible else "❌"
            # Create anchor link to rule section below
            md_content += (
                f"| [{rule.code}](#{rule.code.lower()}) | {rule.name} | "
                f"{aliases} | {fix_icon} |\n"
            )

        md_content += "\n---\n\n"

        # Detailed documentation for each rule
        for rule in rules:
            # Extract summary (first line of docstring)
            summary = ""
            if rule.__doc__:
                first_line = rule.__doc__.strip().split("\n")[0]
                summary = first_line.strip()

            md_content += f"## {rule.code}: {rule.name} {{#{rule.code.lower()}}}\n\n"

            if summary:
                md_content += f"{summary}\n\n"

            # Create metadata table
            md_content += "| Property | Value |\n"
            md_content += "|----------|-------|\n"
            md_content += f"| **Name** | `{rule.name}` |\n"

            if rule.aliases:
                aliases_str = ", ".join(f"`{a}`" for a in rule.aliases)
                md_content += f"| **Aliases** | {aliases_str} |\n"

            if rule.groups:
                groups_str = ", ".join(f"`{g}`" for g in rule.groups)
                md_content += f"| **Groups** | {groups_str} |\n"

            auto_fixable = "Yes ✅" if rule.is_fix_compatible else "No ❌"
            md_content += f"| **Auto-fixable** | {auto_fixable} |\n\n"

            # Convert and add rest of docstring (skip first line which is the summary)
            if rule.__doc__:
                # Split docstring into lines and skip the first line (summary)
                lines = rule.__doc__.split("\n")
                # Find where the actual content starts (after summary and blank lines)
                content_start = 1
                while content_start < len(lines) and not lines[content_start].strip():
                    content_start += 1

                # Join remaining lines
                remaining_doc = "\n".join(lines[content_start:])

                if remaining_doc.strip():
                    converted_doc = rst_to_markdown(remaining_doc)

                    # Extract and replace configuration section with a table
                    converted_doc = format_configuration_section(converted_doc)

                    md_content += converted_doc
                    md_content += "\n\n"

            md_content += "---\n\n"

        # Write to file
        output_file = output_dir / f"{bundle_key}.md"
        output_file.write_text(md_content)
        print(f"Generated: {output_file}")

        # Add to sidebar
        sidebar_items.append(
            {"text": bundle_display, "link": f"/reference/rules/{bundle_key}"}
        )

    # Generate index page
    index_content = "# SQLFluff Rules\n\n"
    index_content += f"SQLFluff has **{len(all_rules)} linting rules** "
    index_content += f"organized into {len(rule_bundles)} categories.\n\n"
    index_content += "## Rule Categories\n\n"

    for bundle_key, rules in sorted_bundles:
        bundle_display = get_bundle_name(bundle_key)
        index_content += f"### [{bundle_display}](./{bundle_key})\n\n"
        index_content += f"{len(rules)} rule(s) - "

        # Add brief description based on bundle
        descriptions = {
            "layout": "Spacing, indentation, and line breaks",
            "aliasing": "Table and column aliasing conventions",
            "capitalisation": "Keyword and identifier capitalization",
            "convention": "General SQL coding conventions",
            "ambiguous": "Potentially ambiguous SQL constructs",
            "structure": "SQL statement structure and organization",
            "references": "Column and table reference validation",
            "jinja": "Jinja templating best practices",
            "tsql": "T-SQL specific conventions",
        }
        index_content += descriptions.get(bundle_key, "SQL linting rules")
        index_content += "\n\n"

    (output_dir / "index.md").write_text(index_content)
    print(f"Generated: {output_dir / 'index.md'}")

    # Return sidebar configuration
    sidebar_config = {
        "text": "Rules Reference",
        "collapsed": True,
        "items": [
            {"text": "Overview", "link": "/reference/rules/"},
            *sidebar_items,
        ],
    }

    return sidebar_config


def main():
    """Main entry point."""
    # Determine paths
    script_dir = Path(__file__).parent
    docs_dir = script_dir.parent
    output_dir = docs_dir / "reference" / "rules"

    print("Generating rule documentation...")
    print(f"Output directory: {output_dir}")

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate documentation
    sidebar_config = generate_rules_documentation(output_dir)

    # Write sidebar configuration
    sidebar_file = docs_dir / ".vitepress" / "sidebar-rules.json"
    sidebar_file.write_text(json.dumps(sidebar_config, indent=2))
    print(f"Generated sidebar config: {sidebar_file}")

    print("\n✅ Rule documentation generation complete!")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate dialect documentation in Markdown format for VitePress.

This script:
1. Extracts all SQLFluff dialects using the dialect system
2. Converts RST docstrings to Markdown
3. Generates markdown files for each dialect
4. Creates VitePress sidebar configuration
"""

import inspect
import json
import re
from pathlib import Path
from typing import Any

from sqlfluff.core.dialects import dialect_readout


def rst_to_markdown(rst_text: str) -> str:
    """Convert RST docstring to Markdown.

    Args:
        rst_text: RST-formatted text

    Returns:
        Markdown-formatted text
    """
    if not rst_text:
        return ""

    # Use inspect.cleandoc to properly clean Python docstrings
    # This removes leading indentation while preserving intentional indentation
    md = inspect.cleandoc(rst_text)

    # First, collect RST reference-style link definitions and build a mapping
    # Pattern: .. _`Link Name`: URL
    link_defs = {}

    def collect_link_def(match):
        link_name = match.group(1)
        url = match.group(2)
        link_defs[link_name] = url
        return ""  # Remove the definition line

    md = re.sub(r"\.\.\s+_`([^`]+)`:\s+(\S+)", collect_link_def, md)

    # Convert RST links to Markdown BEFORE converting backticks
    # Pattern: `Link Text <URL>`_ (with or without trailing underscore)
    md = re.sub(r"`([^`<]+)\s+<(https?://[^>]+)>`_", r"[\1](\2)", md)
    md = re.sub(r"`([^`<]+)\s+<(https?://[^>]+)>`", r"[\1](\2)", md)

    # Convert RST reference-style links to Markdown
    # Pattern: `Link Text`_ → [Link Text](URL) using collected definitions
    def replace_ref_link(match):
        link_text = match.group(1)
        if link_text in link_defs:
            return f"[{link_text}]({link_defs[link_text]})"
        else:
            # If no definition found, just return as plain text
            return link_text

    md = re.sub(r"`([^`]+)`_", replace_ref_link, md)

    # Convert RST double-backtick literals to single backticks (Markdown inline code)
    # This must be done AFTER link conversion
    md = re.sub(r"``([^`]+)``", r"`\1`", md)

    # Convert RST code-block directives to Markdown code fences
    # Pattern: .. code-block:: language\n\n   indented code
    pattern = r"\.\.\s+code-block::\s*(\w+)\s*\n\n((?:[ \t]+.+\n?)+)"

    def replace_code_block(match):
        language = match.group(1)
        code = match.group(2)
        # Remove common indentation from code lines
        lines = code.split("\n")
        # Find minimum indentation (excluding empty lines)
        min_indent = min(
            (len(line) - len(line.lstrip()) for line in lines if line.strip()),
            default=0,
        )
        # Remove that indentation from all lines
        dedented_lines = [line[min_indent:] if line.strip() else "" for line in lines]
        code_content = "\n".join(dedented_lines).strip()

        # Convert 'cfg' language to 'ini' for better syntax highlighting
        if language == "cfg":
            language = "ini"

        return f"```{language}\n{code_content}\n```"

    md = re.sub(pattern, replace_code_block, md)

    # Convert RST inline code to Markdown
    md = re.sub(r":code:`([^`]+)`", r"`\1`", md)
    md = re.sub(r":ref:`([^`]+)`", r"`\1`", md)
    md = re.sub(r":sqlfluff:ref:`([^`]+)`", r"`\1`", md)

    # Convert RST substitution references (|text|) to plain text
    # Common ones like |back_quotes| become backticks
    md = re.sub(r"\|back_quotes\|", "backticks", md)
    md = re.sub(r"\|([^|]+)\|", r"\1", md)  # Generic fallback

    # Convert RST note/warning/important directives to VitePress format
    # Pattern: .. note::\n\n   content
    admonition_pattern = r"\.\.\s+(note|warning|important)::\s*\n\n((?:[ \t]+.+\n?)+)"

    def replace_admonition(match):
        admonition_type = match.group(1)
        content = match.group(2)
        # Remove common indentation
        lines = content.split("\n")
        min_indent = min(
            (len(line) - len(line.lstrip()) for line in lines if line.strip()),
            default=0,
        )
        dedented_lines = [line[min_indent:] if line.strip() else "" for line in lines]
        content_text = "\n".join(dedented_lines).strip()

        # Map RST admonition types to VitePress
        vitepress_type = "info"
        if admonition_type == "warning":
            vitepress_type = "warning"
        elif admonition_type == "important":
            vitepress_type = "tip"

        return f":::{vitepress_type}\n{content_text}\n:::"

    md = re.sub(admonition_pattern, replace_admonition, md, flags=re.IGNORECASE)

    # Clean up extra blank lines
    md = re.sub(r"\n{3,}", "\n\n", md)

    return md.strip()


def generate_dialects_documentation(output_dir: Path) -> dict[str, Any]:
    """Generate dialect documentation markdown files.

    Returns:
        Dictionary with sidebar configuration for VitePress
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Generating dialect documentation...")
    print(f"Output directory: {output_dir}")

    # Get all dialects
    dialects = list(dialect_readout())
    print(f"Found {len(dialects)} dialects")

    # Generate index page with summary table
    index_content = "# SQL Dialects\n\n"
    index_content += f"SQLFluff supports {len(dialects)} SQL dialects.\n\n"
    index_content += "## Supported Dialects\n\n"
    index_content += "| Dialect | Label | Inherits From |\n"
    index_content += "|---------|-------|---------------|\n"

    sidebar_items = []

    for dialect in dialects:
        # Add to summary table with link
        inherits = dialect.inherits_from if dialect.inherits_from != "nothing" else "-"
        index_content += (
            f"| [{dialect.name}]({dialect.label}) | `{dialect.label}` | {inherits} |\n"
        )

        # Generate individual dialect page
        md_content = f"# {dialect.name}\n\n"

        # Metadata table
        md_content += "| Property | Value |\n"
        md_content += "|----------|-------|\n"
        md_content += f"| **Label** | `{dialect.label}` |\n"
        md_content += f"| **Inherits From** | {dialect.inherits_from} |\n\n"

        # Convert and add docstring
        if dialect.docstring:
            converted_doc = rst_to_markdown(dialect.docstring)
            md_content += converted_doc
            md_content += "\n\n"

        # Write to file
        output_file = output_dir / f"{dialect.label}.md"
        output_file.write_text(md_content)
        print(f"Generated: {output_file}")

        # Add to sidebar
        sidebar_items.append(
            {"text": dialect.name, "link": f"/reference/dialects/{dialect.label}"}
        )

    # Write index file
    index_file = output_dir / "index.md"
    index_file.write_text(index_content)
    print(f"Generated: {index_file}")

    # Generate sidebar configuration
    sidebar_config = {
        "text": "SQL Dialects",
        "collapsed": True,
        "items": [{"text": "Overview", "link": "/reference/dialects/"}] + sidebar_items,
    }

    sidebar_file = output_dir.parent.parent / ".vitepress" / "sidebar-dialects.json"
    sidebar_file.write_text(json.dumps(sidebar_config, indent=2))

    # add a new line at the end of the file
    with open(sidebar_file, "a") as f:
        f.write("\n")

    print(f"Generated sidebar config: {sidebar_file}")

    print("✅ Dialect documentation generation complete!")
    return sidebar_config


def main():
    """Main entry point."""
    # Get the output directory (docsv/reference/dialects)
    script_dir = Path(__file__).parent
    output_dir = script_dir.parent / "reference" / "dialects"

    generate_dialects_documentation(output_dir)


if __name__ == "__main__":
    main()

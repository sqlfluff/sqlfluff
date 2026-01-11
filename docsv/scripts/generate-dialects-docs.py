#!/usr/bin/env python3
"""Generate dialect documentation in Markdown format for VitePress.

This script:
1. Extracts all SQLFluff dialects using the dialect system
2. Converts RST docstrings to Markdown using pandoc
3. Generates markdown files for each dialect
4. Creates VitePress sidebar configuration
"""

import json
import re
import subprocess
from pathlib import Path
from typing import Any

from sqlfluff.core.dialects import dialect_readout


def rst_to_markdown(rst_text: str) -> str:
    """Convert RST docstring to Markdown using pandoc.

    Args:
        rst_text: RST-formatted text

    Returns:
        Markdown-formatted text
    """
    if not rst_text:
        return ""

    # Remove common leading indentation
    # Python docstrings often have an unindented summary line followed by indented body
    lines = rst_text.split("\n")
    cleaned_lines = []
    for line in lines:
        # Remove up to 4 leading spaces (common Python docstring indentation)
        if line.startswith("    "):
            cleaned_lines.append(line[4:])
        else:
            cleaned_lines.append(line)
    rst_text = "\n".join(cleaned_lines)

    try:
        # Use pandoc to convert RST to Markdown
        result = subprocess.run(
            ["pandoc", "--from", "rst", "--to", "markdown", "--wrap=none"],
            input=rst_text,
            capture_output=True,
            text=True,
            check=True,
        )

        md = result.stdout

        # Post-process the markdown
        # Convert cfg code blocks to ini (handle both with and without space)
        md = re.sub(r"```\s*cfg", "```ini", md)

        # Fix inline code that pandoc might convert
        md = re.sub(r":code:`([^`]+)`", r"`\1`", md)
        md = re.sub(r":ref:`([^`]+)`", r"`\1`", md)
        md = re.sub(r":sqlfluff:ref:`([^`]+)`", r"`\1`", md)

        # Convert RST note/warning/important directives to VitePress format
        pattern = (
            r"::: note\s*\n::: title\s*\n"
            r"(?:Note|Warning|Important)\s*\n:::\s*\n(.*?)\n:::"
        )
        md = re.sub(
            pattern,
            r":::info\n\1\n:::",
            md,
            flags=re.IGNORECASE | re.DOTALL,
        )

        # Fix escaped characters that pandoc adds
        md = re.sub(r'\\"', '"', md)
        md = re.sub(r"\\'", "'", md)
        md = re.sub(r"\\-", "-", md)

        # Clean up extra blank lines
        md = re.sub(r"\n{3,}", "\n\n", md)

        return md.strip()

    except subprocess.CalledProcessError as e:
        print(f"Warning: pandoc conversion failed: {e.stderr}")
        return rst_text
    except FileNotFoundError:
        print("Warning: pandoc not found. Install with: sudo apt install pandoc")
        return rst_text


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
        "/reference/dialects/": [
            {
                "text": "SQL Dialects",
                "items": [{"text": "Overview", "link": "/reference/dialects/"}]
                + sidebar_items,
            }
        ]
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

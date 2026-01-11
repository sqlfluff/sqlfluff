#!/usr/bin/env python3
"""Generate rule documentation in Markdown format for VitePress.

This script:
1. Extracts all SQLFluff rules using the plugin system
2. Groups rules by bundle (layout, capitalisation, etc.)
3. Converts RST docstrings to Markdown using pandoc
4. Generates bundle-based markdown files
5. Creates VitePress sidebar configuration
"""

import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any

from sqlfluff.core.plugin.host import get_plugin_manager


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
    # We need to remove the indentation to prevent pandoc from creating blockquotes
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
        # Pattern: ::: note\n::: title\nNote\n:::\n becomes ::: info
        md = re.sub(
            r"::: note\s*\n::: title\s*\nNote\s*\n:::\s*\n",
            ":::info\n",
            md,
            flags=re.IGNORECASE,
        )
        # Close the info block where we find the next ::: that closes the note
        # This is tricky because the content is between the markers
        # Better approach: match the full note block
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
        print("Falling back to simple conversion...")
        return simple_rst_to_markdown(rst_text)
    except FileNotFoundError:
        print("Warning: pandoc not found. Install with: sudo apt install pandoc")
        print("Falling back to simple conversion...")
        return simple_rst_to_markdown(rst_text)


def simple_rst_to_markdown(rst_text: str) -> str:
    """Simple fallback RST to Markdown converter when pandoc is not available.

    This is a basic converter that handles common patterns but may not be perfect.
    """
    if not rst_text:
        return ""

    md = rst_text

    # Convert code blocks
    md = re.sub(
        r"^\s*\.\.\s+code-block::\s+(\w+)\s*$",
        r"```\1",
        md,
        flags=re.MULTILINE,
    )

    # Convert inline code
    md = re.sub(r":code:`([^`]+)`", r"`\1`", md)
    md = re.sub(r":ref:`([^`]+)`", r"`\1`", md)
    md = re.sub(r":sqlfluff:ref:`([^`]+)`", r"`\1`", md)

    # Clean up
    md = re.sub(r"\n{3,}", "\n\n", md)

    return md.strip()


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
    config_pattern = r"\*\*Configuration\*\*\s*\n\n((?:-\s+`[^`]+`:[^\n]+\n?)+)"

    def replace_config(match):
        config_text = match.group(1)

        # Parse each configuration option
        # Pattern: -   `option_name`: Description. Must be one of `[values]`.
        option_pattern = r"-\s+`([^`]+)`:\s+([^\n]+)"
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
    index_content += "organized into {len(rule_bundles)} categories.\n\n"
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
    sidebar_config = [
        {
            "text": "Rules by Category",
            "items": [
                {"text": "Overview", "link": "/reference/rules/"},
                *sidebar_items,
            ],
        }
    ]

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

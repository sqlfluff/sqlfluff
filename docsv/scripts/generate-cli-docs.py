#!/usr/bin/env python3
"""Generate CLI documentation in Markdown format for VitePress.

This script:
1. Extracts all SQLFluff CLI commands from Click application
2. Introspects command options including inherited ones from decorators
3. Converts epilog examples to Markdown
4. Generates markdown files for each command
5. Creates VitePress sidebar configuration
"""

import inspect
import json
import re
from pathlib import Path
from typing import Any

import click

from sqlfluff.cli.commands import cli


def clean_docstring(text: str) -> str:
    """Clean up docstring formatting by removing excess indentation.

    Args:
        text: Raw docstring text

    Returns:
        Cleaned text with normalized whitespace
    """
    if not text:
        return ""

    # Use inspect.cleandoc to properly clean Python docstrings
    # This removes leading indentation while preserving intentional indentation
    cleaned = inspect.cleandoc(text)

    # Replace single-quoted code snippets with backticks
    # Matches patterns like 'path/to/file.sql', '--option', 'stdin', '-', etc.
    # Pattern: single quote, followed by content (non-quote chars), followed by
    # single quote
    # This will match code-like strings but not contractions like "it's"
    cleaned = re.sub(r"'([^']+)'", r"`\1`", cleaned)

    return cleaned


def rst_code_block_to_markdown(rst_text: str) -> str:
    """Convert RST code-block directive to Markdown code fence.

    Args:
        rst_text: Text potentially containing RST code-block directives

    Returns:
        Markdown-formatted text with code blocks
    """
    if not rst_text:
        return ""

    # Pattern to match: .. code-block:: sh\n\n   code here\n   more code\n
    # RST code blocks have content indented after the directive
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

        return f"```{language}\n{code_content}\n```"

    result = re.sub(pattern, replace_code_block, rst_text)

    # Clean up any remaining newlines
    result = re.sub(r"\n{3,}", "\n\n", result)

    return result.strip()


def format_option_type(param: click.Parameter) -> str:
    """Format the type of a Click parameter for display.

    Args:
        param: Click parameter object

    Returns:
        Human-readable type string
    """
    if isinstance(param.type, click.Choice):
        choices = param.type.choices
        # Limit displayed choices if there are many
        if len(choices) > 5:
            return f"Choice ({len(choices)} options)"
        return f"Choice: {', '.join(choices)}"
    elif isinstance(param.type, click.Path):
        return "Path"
    elif isinstance(param.type, click.types.IntParamType):
        return "Integer"
    elif isinstance(param.type, click.types.FloatParamType):
        return "Float"
    elif isinstance(param.type, click.types.BoolParamType):
        return "Boolean"
    elif hasattr(param, "is_flag") and param.is_flag:
        return "Flag"
    else:
        return "String"


def format_option_default(param: click.Parameter) -> str:
    """Format the default value of a Click parameter for display.

    Args:
        param: Click parameter object

    Returns:
        Formatted default value or empty string
    """
    if param.default is None:
        return ""
    if hasattr(param, "is_flag") and param.is_flag:
        return "false" if not param.default else "true"
    if callable(param.default):
        return "(dynamic)"
    return str(param.default)


def get_option_names(param: click.Parameter) -> str:
    """Get formatted option names (e.g., '-v, --verbose').

    Args:
        param: Click parameter object

    Returns:
        Comma-separated option names
    """
    if isinstance(param, click.Argument):
        return param.name.upper()
    # For options, opts contains all the names like ['-v', '--verbose']
    return ", ".join(f"`{opt}`" for opt in param.opts)


def extract_command_info(cmd_name: str, cmd: click.Command) -> dict[str, Any]:
    """Extract information from a Click command.

    Args:
        cmd_name: Name of the command
        cmd: Click command object

    Returns:
        Dictionary with command information
    """
    info = {
        "name": cmd_name,
        "short_help": clean_docstring(cmd.short_help or cmd.help or ""),
        "help": clean_docstring(cmd.help or ""),
        "epilog": cmd.epilog or "",
        "params": [],
    }

    # Extract all parameters (options and arguments)
    for param in cmd.params:
        param_info = {
            "name": param.name,
            "names": get_option_names(param),
            "type": format_option_type(param),
            "default": format_option_default(param),
            "help": clean_docstring(getattr(param, "help", "") or ""),
            "required": param.required,
            "is_flag": getattr(param, "is_flag", False),
            "is_argument": isinstance(param, click.Argument),
        }
        info["params"].append(param_info)

    return info


def generate_command_markdown(cmd_info: dict[str, Any]) -> str:
    """Generate markdown content for a single command.

    Args:
        cmd_info: Command information dictionary

    Returns:
        Markdown content
    """
    lines = [f"# {cmd_info['name']}\n"]

    # Add description
    if cmd_info["help"]:
        lines.append(f"{cmd_info['help']}\n")

    # Extract arguments and options
    arguments = [p for p in cmd_info["params"] if p["is_argument"]]
    options = [p for p in cmd_info["params"] if not p["is_argument"]]

    # Add usage section
    lines.append("## Usage\n")
    usage = f"sqlfluff {cmd_info['name']}"

    if options:
        usage += " [OPTIONS]"

    for arg in arguments:
        if arg["required"]:
            usage += f" {arg['name']}"
        else:
            usage += f" [{arg['name']}]"

    lines.append(f"```bash\n{usage}\n```\n")

    # Add arguments section if there are any
    if arguments:
        lines.append("## Arguments\n")
        lines.append("| Argument | Description |")
        lines.append("|----------|-------------|")
        for arg in arguments:
            name = f"`{arg['name']}`"
            help_text = arg["help"].replace("\n", " ").strip()
            lines.append(f"| {name} | {help_text} |")
        lines.append("")

    # Add options section
    if options:
        lines.append("## Options\n")
        lines.append("| Option | Type | Default | Description |")
        lines.append("|--------|------|---------|-------------|")
        for opt in options:
            names = opt["names"]
            opt_type = opt["type"]
            default = f"`{opt['default']}`" if opt["default"] else "—"
            help_text = opt["help"].replace("\n", " ").strip()
            lines.append(f"| {names} | {opt_type} | {default} | {help_text} |")
        lines.append("")

    # Add examples section if epilog exists
    if cmd_info["epilog"]:
        epilog_md = rst_code_block_to_markdown(cmd_info["epilog"])
        if epilog_md:
            lines.append("## Examples\n")
            lines.append(epilog_md)
            lines.append("")

    return "\n".join(lines)


def generate_index_markdown(commands: list[dict[str, Any]]) -> str:
    """Generate the index markdown with command summary.

    Args:
        commands: List of command information dictionaries

    Returns:
        Markdown content for index page
    """
    lines = [
        "# CLI Reference\n",
        "SQLFluff provides a comprehensive command-line interface for linting, "
        "fixing, and parsing SQL files.\n",
        "## Available Commands\n",
        "| Command | Description |",
        "|---------|-------------|",
    ]

    for cmd in sorted(commands, key=lambda x: x["name"]):
        name = f"[`{cmd['name']}`](./{cmd['name']})"
        desc = cmd["short_help"].replace("\n", " ").strip()
        lines.append(f"| {name} | {desc} |")

    lines.append("")
    lines.append("## Quick Start\n")
    lines.append("```bash")
    lines.append("# Lint SQL files")
    lines.append("sqlfluff lint path/to/file.sql")
    lines.append("")
    lines.append("# Fix violations automatically")
    lines.append("sqlfluff fix path/to/file.sql")
    lines.append("")
    lines.append("# Check available dialects")
    lines.append("sqlfluff dialects")
    lines.append("```\n")

    return "\n".join(lines)


def generate_sidebar_config(commands: list[dict[str, Any]]) -> dict[str, Any]:
    """Generate VitePress sidebar configuration.

    Args:
        commands: List of command information dictionaries

    Returns:
        Sidebar configuration dictionary
    """
    items = []

    # Add index
    items.append({"text": "Overview", "link": "/reference/cli/"})

    # Add all commands
    for cmd in sorted(commands, key=lambda x: x["name"]):
        items.append({"text": cmd["name"], "link": f"/reference/cli/{cmd['name']}"})

    return {
        "text": "CLI Reference",
        "collapsed": False,
        "items": items,
    }


def main():
    """Generate CLI documentation."""
    # Get script directory and output directory
    script_dir = Path(__file__).parent
    docs_dir = script_dir.parent
    output_dir = docs_dir / "reference" / "cli"

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Generating CLI documentation...")

    # Extract command information
    commands = []
    for cmd_name in sorted(cli.commands.keys()):
        cmd = cli.commands[cmd_name]
        cmd_info = extract_command_info(cmd_name, cmd)
        commands.append(cmd_info)
        print(f"  Processing command: {cmd_name}")

        # Generate markdown for this command
        md_content = generate_command_markdown(cmd_info)

        # Write to file
        output_file = output_dir / f"{cmd_name}.md"
        output_file.write_text(md_content)

    # Generate index page
    print("  Generating index page...")
    index_content = generate_index_markdown(commands)
    index_file = output_dir / "index.md"
    index_file.write_text(index_content)

    # Generate sidebar configuration
    print("  Generating sidebar configuration...")
    sidebar_config = generate_sidebar_config(commands)
    sidebar_file = docs_dir / ".vitepress" / "sidebar-cli.json"
    sidebar_file.write_text(json.dumps(sidebar_config, indent=2))
    # Add newline at end
    with open(sidebar_file, "a") as f:
        f.write("\n")

    print(f"✓ Generated documentation for {len(commands)} commands")
    print(f"✓ Output written to {output_dir}")


if __name__ == "__main__":
    main()

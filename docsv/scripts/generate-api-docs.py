#!/usr/bin/env python3
"""Generate API documentation in Markdown format for VitePress.

This script:
1. Extracts public API functions from sqlfluff.api modules
2. Introspects function signatures and type hints
3. Parses Google-style docstrings
4. Generates markdown files for each module
5. Creates VitePress sidebar configuration
"""

import inspect
import json
import re
from pathlib import Path
from typing import Any, Callable, get_type_hints

from sqlfluff.api import info, simple


def parse_param_list(text: str) -> list[dict[str, str]]:
    """Parse parameter list from Google-style docstring.

    Args:
        text: Text containing parameter descriptions

    Returns:
        List of dicts with keys: name, type, description
    """
    if not text.strip():
        return []

    params = []
    # Pattern: name (type, optional): description
    # or: name (:obj:`type`, optional): description
    # or: name: description
    param_pattern = r"^\s*(\w+)\s*(?:\(([^)]+)\))?\s*:\s*(.+)$"

    lines = text.split("\n")
    current_param = None

    for line in lines:
        # Try to match a parameter definition
        match = re.match(param_pattern, line)
        if match:
            # Save previous parameter if exists
            if current_param:
                params.append(current_param)

            # Start new parameter
            name = match.group(1)
            param_type = match.group(2) or ""
            description = match.group(3).strip()

            # Clean up type annotations like :obj:`str`
            param_type = re.sub(r":obj:`([^`]+)`", r"\1", param_type)

            current_param = {
                "name": name,
                "type": param_type,
                "description": description,
            }
        elif current_param and line.strip():
            # Continuation of previous parameter description
            current_param["description"] += " " + line.strip()

    # Save last parameter
    if current_param:
        params.append(current_param)

    return params


def parse_google_docstring(docstring: str) -> dict[str, Any]:
    """Parse a Google-style docstring into structured sections.

    Args:
        docstring: The raw docstring text

    Returns:
        Dictionary with keys: description, args, returns, raises, examples, note
    """
    if not docstring:
        return {}

    # Clean the docstring
    cleaned = inspect.cleandoc(docstring)

    # Initialize sections
    sections = {
        "description": "",
        "args": [],
        "returns": "",
        "raises": [],
        "examples": "",
        "note": "",
    }

    # Split into sections based on Google-style headers
    # Match "Args:", "Returns:", "Raises:", "Examples:", "Note:", etc.
    section_pattern = r"^(Args?|Returns?|Raises?|Examples?|Note):\s*$"

    lines = cleaned.split("\n")
    current_section = "description"
    current_content = []

    for line in lines:
        # Check if this line is a section header
        match = re.match(section_pattern, line.strip())
        if match:
            # Save previous section content
            if current_section == "description":
                sections["description"] = "\n".join(current_content).strip()
            elif current_section in ("args", "raises"):
                # Parse parameter list
                sections[current_section] = parse_param_list("\n".join(current_content))
            elif current_section in ("returns", "examples", "note"):
                sections[current_section] = "\n".join(current_content).strip()

            # Start new section
            current_section = (
                match.group(1).lower().rstrip("s")
            )  # Normalize to singular
            if current_section == "arg":
                current_section = "args"
            elif current_section == "return":
                current_section = "returns"
            elif current_section == "raise":
                current_section = "raises"
            elif current_section == "example":
                current_section = "examples"
            current_content = []
        else:
            current_content.append(line)

    # Save final section
    if current_section == "description":
        sections["description"] = "\n".join(current_content).strip()
    elif current_section in ("args", "raises"):
        sections[current_section] = parse_param_list("\n".join(current_content))
    elif current_section in ("returns", "examples", "note"):
        sections[current_section] = "\n".join(current_content).strip()

    return sections


def extract_function_info(func: Callable, module_name: str) -> dict[str, Any]:
    """Extract information from a function for documentation.

    Args:
        func: Function object to document
        module_name: Name of the module containing the function

    Returns:
        Dictionary with function information
    """
    # Get signature
    try:
        sig = inspect.signature(func)
    except (ValueError, TypeError):
        sig = None

    # Get type hints
    try:
        hints = get_type_hints(func)
    except Exception:
        hints = {}

    # Parse docstring
    docstring = inspect.getdoc(func) or ""
    parsed_doc = parse_google_docstring(docstring)

    # Build parameter info
    params = []
    if sig:
        for param_name, param in sig.parameters.items():
            # Get type from hints or annotation
            param_type = ""
            if param_name in hints:
                param_type = format_type_hint(hints[param_name])
            elif param.annotation != inspect.Parameter.empty:
                param_type = format_type_hint(param.annotation)

            # Get default value
            default = ""
            if param.default != inspect.Parameter.empty:
                if param.default is None:
                    default = "None"
                elif isinstance(param.default, str):
                    default = f'"{param.default}"'
                else:
                    default = str(param.default)

            # Find description from docstring
            description = ""
            for doc_param in parsed_doc.get("args", []):
                if doc_param["name"] == param_name:
                    description = doc_param["description"]
                    if not param_type and doc_param["type"]:
                        param_type = doc_param["type"]
                    break

            params.append(
                {
                    "name": param_name,
                    "type": param_type,
                    "default": default,
                    "description": description,
                }
            )

    # Get return type
    return_type = ""
    if "return" in hints:
        return_type = format_type_hint(hints["return"])
    elif sig and sig.return_annotation != inspect.Signature.empty:
        return_type = format_type_hint(sig.return_annotation)

    return {
        "name": func.__name__,
        "module": module_name,
        "description": parsed_doc.get("description", ""),
        "params": params,
        "returns": parsed_doc.get("returns", ""),
        "return_type": return_type,
        "raises": parsed_doc.get("raises", []),
        "examples": parsed_doc.get("examples", ""),
        "note": parsed_doc.get("note", ""),
    }


def format_type_hint(hint: Any) -> str:
    """Format a type hint for display.

    Args:
        hint: Type hint object

    Returns:
        Formatted string representation
    """
    if hint is None or hint is type(None):
        return "None"

    # Handle string annotations
    if isinstance(hint, str):
        return hint

    # Get the string representation
    hint_str = str(hint)

    # Clean up common patterns
    hint_str = hint_str.replace("typing.", "")
    hint_str = hint_str.replace("<class '", "").replace("'>", "")
    hint_str = re.sub(r"sqlfluff\.core\.\w+\.", "", hint_str)

    return hint_str


def extract_class_info(cls: type, module_name: str) -> dict[str, Any]:
    """Extract information from a class for documentation.

    Args:
        cls: Class object to document
        module_name: Name of the module containing the class

    Returns:
        Dictionary with class information
    """
    # Parse docstring
    docstring = inspect.getdoc(cls) or ""
    parsed_doc = parse_google_docstring(docstring)

    # Get __init__ signature if it exists
    params = []
    try:
        init_sig = inspect.signature(cls.__init__)
        hints = get_type_hints(cls.__init__)

        for param_name, param in init_sig.parameters.items():
            if param_name == "self":
                continue

            # Get type
            param_type = ""
            if param_name in hints:
                param_type = format_type_hint(hints[param_name])
            elif param.annotation != inspect.Parameter.empty:
                param_type = format_type_hint(param.annotation)

            # Get default
            default = ""
            if param.default != inspect.Parameter.empty:
                if param.default is None:
                    default = "None"
                else:
                    default = str(param.default)

            # Find description
            description = ""
            for doc_param in parsed_doc.get("args", []):
                if doc_param["name"] == param_name:
                    description = doc_param["description"]
                    break

            params.append(
                {
                    "name": param_name,
                    "type": param_type,
                    "default": default,
                    "description": description,
                }
            )
    except (ValueError, TypeError):
        pass

    return {
        "name": cls.__name__,
        "module": module_name,
        "type": "class",
        "description": parsed_doc.get("description", ""),
        "params": params,
        "note": parsed_doc.get("note", ""),
    }


def generate_module_markdown(
    module_name: str, functions: list[dict[str, Any]], classes: list[dict[str, Any]]
) -> str:
    """Generate markdown content for a module.

    Args:
        module_name: Name of the module
        functions: List of function information dicts
        classes: List of class information dicts

    Returns:
        Markdown content
    """
    lines = [f"# {module_name}\n"]

    # Add module description based on module
    if module_name == "simple":
        lines.append(
            "The simple API provides high-level functions for linting, fixing, "
            "and parsing SQL strings.\n"
        )
    elif module_name == "info":
        lines.append(
            "The info API provides functions to list available rules and dialects.\n"
        )

    # Generate classes section
    if classes:
        lines.append("## Classes\n")
        for cls_info in classes:
            lines.append(f"### {cls_info['name']}\n")

            if cls_info["description"]:
                lines.append(f"{cls_info['description']}\n")

            if cls_info["params"]:
                lines.append("**Parameters:**\n")
                lines.append("| Parameter | Type | Default | Description |")
                lines.append("|-----------|------|---------|-------------|")
                for param in cls_info["params"]:
                    name = f"`{param['name']}`"
                    ptype = f"`{param['type']}`" if param["type"] else "—"
                    default = f"`{param['default']}`" if param["default"] else "—"
                    desc = param["description"].replace("\n", " ").strip()
                    lines.append(f"| {name} | {ptype} | {default} | {desc} |")
                lines.append("")

            if cls_info["note"]:
                lines.append(f"**Note:** {cls_info['note']}\n")

    # Generate functions section
    if functions:
        lines.append("## Functions\n")
        for func_info in functions:
            lines.append(f"### {func_info['name']}\n")

            # Signature
            param_parts = []
            for param in func_info["params"]:
                if param["default"]:
                    param_parts.append(f"{param['name']}={param['default']}")
                else:
                    param_parts.append(param["name"])

            signature = f"{func_info['name']}({', '.join(param_parts)})"
            if func_info["return_type"]:
                signature += f" → {func_info['return_type']}"

            lines.append(f"```python\n{signature}\n```\n")

            # Description
            if func_info["description"]:
                lines.append(f"{func_info['description']}\n")

            # Parameters table
            if func_info["params"]:
                lines.append("**Parameters:**\n")
                lines.append("| Parameter | Type | Default | Description |")
                lines.append("|-----------|------|---------|-------------|")
                for param in func_info["params"]:
                    name = f"`{param['name']}`"
                    ptype = f"`{param['type']}`" if param["type"] else "—"
                    default = f"`{param['default']}`" if param["default"] else "—"
                    desc = param["description"].replace("\n", " ").strip()
                    lines.append(f"| {name} | {ptype} | {default} | {desc} |")
                lines.append("")

            # Returns
            if func_info["returns"] or func_info["return_type"]:
                lines.append("**Returns:**\n")
                return_desc = func_info["returns"] or "See return type above"
                if func_info["return_type"]:
                    lines.append(f"`{func_info['return_type']}` — {return_desc}\n")
                else:
                    lines.append(f"{return_desc}\n")

            # Raises
            if func_info["raises"]:
                lines.append("**Raises:**\n")
                for exc in func_info["raises"]:
                    exc_type = exc.get("type", "Exception")
                    exc_desc = exc.get("description", "")
                    lines.append(f"- `{exc_type}`: {exc_desc}")
                lines.append("")

            # Examples
            if func_info["examples"]:
                lines.append("**Examples:**\n")
                # Format examples as code block
                examples = func_info["examples"].strip()
                # If not already in code fence, wrap it
                if not examples.startswith("```"):
                    lines.append(f"```python\n{examples}\n```\n")
                else:
                    lines.append(f"{examples}\n")

            # Note
            if func_info["note"]:
                lines.append(f"**Note:** {func_info['note']}\n")

    return "\n".join(lines)


def generate_index_markdown(modules: list[dict[str, Any]]) -> str:
    """Generate the index markdown with API overview.

    Args:
        modules: List of module information dicts

    Returns:
        Markdown content for index page
    """
    lines = [
        "# Python API Reference\n",
        "SQLFluff provides a Python API for programmatic access to linting, "
        "fixing, and parsing functionality.\n",
        "## Modules\n",
        "| Module | Description |",
        "|--------|-------------|",
    ]

    for mod in modules:
        name = f"[`{mod['name']}`](./{mod['name']})"
        desc = mod["description"]
        lines.append(f"| {name} | {desc} |")

    lines.append("")
    lines.append("## Quick Start\n")
    lines.append("```python")
    lines.append("from sqlfluff.api import lint, fix, parse")
    lines.append("")
    lines.append("# Lint SQL")
    lines.append('violations = lint("SELECT * FROM tbl", dialect="postgres")')
    lines.append("")
    lines.append("# Fix SQL")
    lines.append('fixed_sql = fix("SELECT * FROM tbl", dialect="postgres")')
    lines.append("")
    lines.append("# Parse SQL")
    lines.append('tree = parse("SELECT * FROM tbl", dialect="postgres")')
    lines.append("```\n")

    return "\n".join(lines)


def generate_sidebar_config(modules: list[dict[str, Any]]) -> dict[str, Any]:
    """Generate VitePress sidebar configuration.

    Args:
        modules: List of module information dicts

    Returns:
        Sidebar configuration dictionary
    """
    items = []

    # Add index
    items.append({"text": "Overview", "link": "/reference/api/"})

    # Add all modules
    for mod in sorted(modules, key=lambda x: x["name"]):
        items.append({"text": mod["name"], "link": f"/reference/api/{mod['name']}"})

    return {
        "text": "Python API",
        "collapsed": True,
        "items": items,
    }


def main():
    """Generate API documentation."""
    # Get script directory and output directory
    script_dir = Path(__file__).parent
    docs_dir = script_dir.parent
    output_dir = docs_dir / "reference" / "api"

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Generating API documentation...")

    # Define modules to document
    modules_info = [
        {
            "name": "simple",
            "module": simple,
            "description": "High-level API for linting, fixing, and parsing SQL",
        },
        {
            "name": "info",
            "module": info,
            "description": "Information about available rules and dialects",
        },
    ]

    modules_output = []

    for mod_info in modules_info:
        print(f"  Processing module: {mod_info['name']}")

        # Get all public functions and classes from the module
        functions = []
        classes = []

        for name, obj in inspect.getmembers(mod_info["module"]):
            # Skip private members
            if name.startswith("_"):
                continue

            # Skip imported items (only document items defined in this module)
            if hasattr(obj, "__module__") and not obj.__module__.startswith(
                f"sqlfluff.api.{mod_info['name']}"
            ):
                continue

            if inspect.isfunction(obj):
                func_info = extract_function_info(obj, mod_info["name"])
                functions.append(func_info)
                print(f"    - Function: {name}")
            elif inspect.isclass(obj):
                class_info = extract_class_info(obj, mod_info["name"])
                classes.append(class_info)
                print(f"    - Class: {name}")

        # Generate markdown
        md_content = generate_module_markdown(mod_info["name"], functions, classes)

        # Write to file
        output_file = output_dir / f"{mod_info['name']}.md"
        output_file.write_text(md_content)

        modules_output.append(
            {
                "name": mod_info["name"],
                "description": mod_info["description"],
                "functions": len(functions),
                "classes": len(classes),
            }
        )

    # Generate index page
    print("  Generating index page...")
    index_content = generate_index_markdown(modules_output)
    index_file = output_dir / "index.md"
    index_file.write_text(index_content)

    # Generate sidebar configuration
    print("  Generating sidebar configuration...")
    sidebar_config = generate_sidebar_config(modules_output)
    sidebar_dir = docs_dir / ".vitepress"
    sidebar_dir.mkdir(exist_ok=True)
    sidebar_file = sidebar_dir / "sidebar-api.json"
    sidebar_file.write_text(json.dumps(sidebar_config, indent=2))
    # Add newline at end
    with open(sidebar_file, "a") as f:
        f.write("\n")

    total_functions = sum(m["functions"] for m in modules_output)
    total_classes = sum(m["classes"] for m in modules_output)
    print(
        f"✓ Generated documentation for {len(modules_output)} modules "
        f"({total_functions} functions, {total_classes} classes)"
    )
    print(f"✓ Output written to {output_dir}")


if __name__ == "__main__":
    main()

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
from pathlib import Path
from typing import Any, Callable, get_type_hints

from doc_utils import (
    format_type_hint,
    params_table_rows,
    parse_google_docstring,
)

from sqlfluff.api import info, simple
from sqlfluff.core import Lexer, Linter, Parser


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

    # Extract public methods
    methods = []
    for name, obj in inspect.getmembers(cls):
        # Skip private/magic methods except __init__
        if name.startswith("_"):
            continue

        # Only process methods
        if inspect.ismethod(obj) or inspect.isfunction(obj):
            try:
                method_info = extract_function_info(obj, module_name)
                # Add class context
                method_info["class_name"] = cls.__name__
                methods.append(method_info)
            except Exception:
                # Skip methods that can't be introspected
                pass

    return {
        "name": cls.__name__,
        "module": module_name,
        "type": "class",
        "description": parsed_doc.get("description", ""),
        "params": params,
        "methods": methods,
        "note": parsed_doc.get("note", ""),
    }


def generate_module_markdown(
    name: str,
    module_name: str,
    functions: list[dict[str, Any]],
    classes: list[dict[str, Any]],
) -> str:
    """Generate markdown content for a module.

    Args:
        name: Display name of the module
        module_name: Name of the module
        functions: List of function information dicts
        classes: List of class information dicts

    Returns:
        Markdown content
    """
    lines = [f"# {name}\n"]

    # Add frontmatter for simple and core modules
    if module_name in ("simple", "core"):
        lines.insert(0, "---\noutline: [2, 4]\n---\n")

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
    elif module_name == "core":
        lines.append(
            "The simple API presents only a fraction of the functionality present "
            "within the core SQLFluff library. For more advanced use cases, users can "
            "import the `Linter()` and `FluffConfig()` classes from `sqlfluff.core`. "
            "As of version 0.4.0 this is considered as experimental only as the "
            "internals may change without warning in any future release. If you come "
            "to rely on the internals of SQLFluff, please post an issue on GitHub to "
            "share what you're up to. This will help shape a more reliable, tidy and "
            "well documented public API for use.\n"
        )

    # Generate classes section
    if classes:
        lines.append("# Classes\n")
        for cls_info in classes:
            lines.append(f"## {cls_info['name']}\n")

            if cls_info["description"]:
                lines.append(f"{cls_info['description']}\n")

            if cls_info["params"]:
                lines.extend(params_table_rows(cls_info["params"]))

            # Add methods section
            if cls_info.get("methods"):
                lines.append("### Methods\n")
                for method_info in cls_info["methods"]:
                    lines.append(f"#### `{method_info['name']}`\n")

                    # Signature - format with line breaks for readability
                    param_parts = []
                    for param in method_info["params"]:
                        if param["default"]:
                            param_parts.append(
                                f"    {param['name']}={param['default']}"
                            )
                        else:
                            param_parts.append(f"    {param['name']}")

                    if param_parts:
                        param_str = ",\n".join(param_parts)
                        signature = f"{method_info['name']}(\n{param_str}\n)"
                    else:
                        signature = f"{method_info['name']}()"

                    if method_info["return_type"]:
                        signature += f" → {method_info['return_type']}"

                    lines.append(f"```python\n{signature}\n```\n")

                    # Description
                    if method_info["description"]:
                        lines.append(f"{method_info['description']}\n")

                    # Parameters table
                    if method_info["params"]:
                        lines.extend(params_table_rows(method_info["params"]))

                    # Returns
                    if method_info["returns"] or method_info["return_type"]:
                        lines.append("**Returns:**\n")
                        return_desc = method_info["returns"] or "See return type above"
                        if method_info["return_type"]:
                            lines.append(
                                f"`{method_info['return_type']}` — {return_desc}\n"
                            )
                        else:
                            lines.append(f"{return_desc}\n")

                    # Raises
                    if method_info["raises"]:
                        lines.append("**Raises:**\n")
                        for exc in method_info["raises"]:
                            exc_type = exc.get("type", "Exception")
                            exc_desc = exc.get("description", "")
                            lines.append(f"- `{exc_type}`: {exc_desc}")
                        lines.append("")

                    # Examples
                    if method_info["examples"]:
                        lines.append("**Examples:**\n")
                        examples = method_info["examples"].strip()
                        if not examples.startswith("```"):
                            lines.append(f"```python\n{examples}\n```\n")
                        else:
                            lines.append(f"{examples}\n")

                    # Note
                    if method_info["note"]:
                        lines.append(f"**Note:** {method_info['note']}\n")

            if cls_info["note"]:
                lines.append(f"**Note:** {cls_info['note']}\n")

    # Generate functions section
    if functions:
        lines.append("## Functions\n")
        for func_info in functions:
            lines.append(f"### {func_info['name']}\n")

            # Signature - format with line breaks for readability
            param_parts = []
            for param in func_info["params"]:
                if param["default"]:
                    param_parts.append(f"    {param['name']}={param['default']}")
                else:
                    param_parts.append(f"    {param['name']}")

            if param_parts:
                param_str = ",\n".join(param_parts)
                signature = f"{func_info['name']}(\n{param_str}\n)"
            else:
                signature = f"{func_info['name']}()"

            if func_info["return_type"]:
                signature += f" → {func_info['return_type']}"

            lines.append(f"```python\n{signature}\n```\n")

            # Description
            if func_info["description"]:
                lines.append(f"{func_info['description']}\n")

            # Parameters table
            if func_info["params"]:
                lines.extend(params_table_rows(func_info["params"]))

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
        "SQLFluff exposes a public api for other python applications to use. ",
        "A basic example of this usage is given here, with the documentation ",
        "for each of the methods below.\n",
        "<<< @/../examples/01_basic_api_usage.py\n",
        "## Modules\n",
        "| Module | Description |",
        "|--------|-------------|",
    ]

    for mod in modules:
        name = f"[`{mod['name']}`](./{mod['module_name']})"
        desc = mod["description"]
        lines.append(f"| {name} | {desc} |")

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
    for mod in modules:
        items.append(
            {"text": mod["name"], "link": f"/reference/api/{mod['module_name']}"}
        )

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
            "name": "Simple API",
            "module": simple,
            "module_name": "simple",
            "description": "High-level API for linting, fixing, and parsing SQL",
        },
        {
            "name": "Advanced API",
            "module": None,  # Use whitelist instead
            "module_name": "core",
            "description": "Core classes for parsing and linting",
            "whitelist": {"Linter": Linter, "Lexer": Lexer, "Parser": Parser},
        },
        {
            "name": "Info",
            "module": info,
            "module_name": "info",
            "description": "Information about available rules and dialects",
        },
    ]

    modules_output = []

    for mod_info in modules_info:
        print(f"  Processing module: {mod_info['name']}")

        # Get all public functions and classes from the module
        functions = []
        classes = []

        # If whitelist is provided, only document those members
        if "whitelist" in mod_info:
            for name, obj in mod_info["whitelist"].items():
                if inspect.isfunction(obj):
                    func_info = extract_function_info(obj, mod_info["name"])
                    functions.append(func_info)
                    print(f"    - Function: {name}")
                elif inspect.isclass(obj):
                    class_info = extract_class_info(obj, mod_info["name"])
                    classes.append(class_info)
                    print(f"    - Class: {name}")
        else:
            # Process all public members from the module
            for name, obj in inspect.getmembers(mod_info["module"]):
                # Skip private members
                if name.startswith("_"):
                    continue

                # Skip imported items (only document items defined in this module)
                if hasattr(obj, "__module__") and not obj.__module__.startswith(
                    f"sqlfluff.api.{mod_info['module_name']}"
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
        md_content = generate_module_markdown(
            mod_info["name"], mod_info["module_name"], functions, classes
        )

        # Write to file
        output_file = output_dir / f"{mod_info['module_name']}.md"
        output_file.write_text(md_content, encoding="utf-8")

        modules_output.append(
            {
                "name": mod_info["name"],
                "module_name": mod_info["module_name"],
                "description": mod_info["description"],
                "functions": len(functions),
                "classes": len(classes),
            }
        )

    # Generate index page
    print("  Generating index page...")
    index_content = generate_index_markdown(modules_output)
    index_file = output_dir / "index.md"
    index_file.write_text(index_content, encoding="utf-8")

    # Generate sidebar configuration
    print("  Generating sidebar configuration...")
    sidebar_config = generate_sidebar_config(modules_output)
    sidebar_dir = docs_dir / ".vitepress"
    sidebar_dir.mkdir(exist_ok=True)
    sidebar_file = sidebar_dir / "sidebar-api.json"
    sidebar_file.write_text(json.dumps(sidebar_config, indent=2), encoding="utf-8")
    # Add newline at end
    with open(sidebar_file, "a", encoding="utf-8") as f:
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

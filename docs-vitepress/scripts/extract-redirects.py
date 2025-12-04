#!/usr/bin/env python3
"""Extract redirects from Sphinx conf.py and convert to VitePress format.

This script:
1. Parses docs/source/conf.py to extract rediraffe_redirects
2. Converts Sphinx HTML paths to VitePress markdown paths
3. Generates TypeScript rewrites config for VitePress
4. Outputs both inline TypeScript and JSON format
"""

import json
from pathlib import Path


def extract_sphinx_redirects(conf_path: Path) -> dict[str, str]:
    """Extract redirects from Sphinx conf.py file.

    Args:
        conf_path: Path to conf.py file

    Returns:
        Dictionary of {old_path: new_path}
    """
    print(f"Reading redirects from: {conf_path}")

    # Change to the conf.py directory so relative imports work
    import os

    original_dir = os.getcwd()
    os.chdir(conf_path.parent)

    try:
        # Execute the conf.py file to get the redirects variable
        namespace = {}
        with open(conf_path) as f:
            exec(f.read(), namespace)

        redirects = namespace.get("redirects", {})

        if not redirects:
            print("WARNING: No redirects found in conf.py")
            return {}

        print(f"Found {len(redirects)} redirects")
        return redirects
    finally:
        os.chdir(original_dir)


def convert_redirect_to_vitepress(old_path: str, new_path: str) -> tuple[str, str]:
    """Convert Sphinx redirect to VitePress format.

    Args:
        old_path: Sphinx old path (may end with .html)
        new_path: Sphinx new path (may end with .html, may have ../.. prefix)

    Returns:
        Tuple of (vitepress_old, vitepress_new)
    """
    # Remove .html extension
    old = old_path.replace(".html", "")
    new = new_path.replace(".html", "")

    # Remove leading ../ from new path (Sphinx relative paths)
    while new.startswith("../"):
        new = new[3:]

    # Convert to markdown path
    if not new.endswith(".md") and not new.endswith("/"):
        new = new + ".md"

    return old, new


def generate_vitepress_rewrites(redirects: dict[str, str]) -> dict[str, str]:
    """Generate VitePress rewrites configuration.

    Args:
        redirects: Sphinx redirects dictionary

    Returns:
        VitePress rewrites dictionary
    """
    rewrites = {}

    for old_path, new_path in redirects.items():
        old, new = convert_redirect_to_vitepress(old_path, new_path)

        # Skip anchor-only redirects (VitePress handles these differently)
        if "#" in new_path and new_path.count("/") < 2:
            print(f"  Skipping anchor redirect: {old} -> {new}")
            continue

        rewrites[old] = new

    return rewrites


def generate_typescript_config(rewrites: dict[str, str]) -> str:
    """Generate TypeScript code for VitePress config.

    Args:
        rewrites: VitePress rewrites dictionary

    Returns:
        TypeScript code string
    """
    ts = "  // Auto-generated redirects from Sphinx conf.py\n"
    ts += "  rewrites: {\n"

    for old, new in sorted(rewrites.items()):
        # Escape single quotes in paths
        old_escaped = old.replace("'", "\\'")
        new_escaped = new.replace("'", "\\'")
        ts += f"    '{old_escaped}': '{new_escaped}',\n"

    ts += "  },\n"

    return ts


def main():
    """Main entry point."""
    script_dir = Path(__file__).parent
    docs_vitepress = script_dir.parent
    docs_sphinx = docs_vitepress.parent / "docs"

    # Find conf.py
    conf_path = docs_sphinx / "source" / "conf.py"
    if not conf_path.exists():
        print(f"ERROR: Could not find {conf_path}")
        return 1

    # Extract redirects from Sphinx
    sphinx_redirects = extract_sphinx_redirects(conf_path)

    if not sphinx_redirects:
        print("No redirects found, nothing to do")
        return 0

    # Convert to VitePress format
    vitepress_rewrites = generate_vitepress_rewrites(sphinx_redirects)

    print(f"\nConverted {len(vitepress_rewrites)} redirects to VitePress format")

    # Output JSON file
    json_output = docs_vitepress / ".vitepress" / "redirects.json"
    with open(json_output, "w") as f:
        json.dump(vitepress_rewrites, f, indent=2)
    print(f"✅ Generated JSON: {json_output}")

    # add a new line at the end of the file
    with open(json_output, "a") as f:
        f.write("\n")

    # Print summary
    print("\n" + "=" * 60)
    print("REDIRECT SUMMARY")
    print("=" * 60)

    # Group by type
    perma_redirects = {
        k: v for k, v in vitepress_rewrites.items() if k.startswith("perma/")
    }
    rule_redirects = {k: v for k, v in vitepress_rewrites.items() if "/rule/" in k}
    other_redirects = {
        k: v
        for k, v in vitepress_rewrites.items()
        if not k.startswith("perma/") and "/rule/" not in k
    }

    print(f"Perma redirects: {len(perma_redirects)}")
    print(f"Rule redirects: {len(rule_redirects)}")
    print(f"Other redirects: {len(other_redirects)}")
    print(f"Total: {len(vitepress_rewrites)}")

    # Show sample redirects
    print("\nSample redirects:")
    for i, (old, new) in enumerate(sorted(vitepress_rewrites.items())[:5]):
        print(f"  {old} -> {new}")

    print("\n✅ Redirect extraction complete!")
    print("\nTo use in VitePress config.ts:")
    print(
        "  1. Import: import redirects from './redirects.json' assert { type: 'json' }"
    )
    print("  2. Add to config: rewrites: redirects")

    return 0


if __name__ == "__main__":
    exit(main())

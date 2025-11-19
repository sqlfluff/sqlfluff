#!/usr/bin/env python3
"""Master script to generate all VitePress documentation.

This script orchestrates the entire documentation generation process:
1. Rule documentation (generate-rules-docs.py)
2. API documentation (pydoc-markdown)
3. Redirect extraction (extract-redirects.py)
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> int:
    """Run a command and report status.

    Args:
        cmd: Command and arguments as list
        description: Human-readable description

    Returns:
        Exit code (0 = success)
    """
    print("\n" + "=" * 60)
    print(f"▶ {description}")
    print("=" * 60)
    print(f"Command: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(cmd, check=True)
        print(f"✅ {description} completed successfully")
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return e.returncode
    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        print("   Make sure the required tools are installed")
        return 1


def main():
    """Main entry point."""
    script_dir = Path(__file__).parent
    docs_dir = script_dir.parent

    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "VitePress Documentation Build" + " " * 14 + "║")
    print("╚" + "=" * 58 + "╝")

    # Step 1: Generate rule documentation
    rules_script = script_dir / "generate-rules-docs.py"
    exit_code = run_command(
        [sys.executable, str(rules_script)], "Generating rule documentation"
    )
    if exit_code != 0:
        print("\n❌ Build failed at rule documentation generation")
        return exit_code

    # Step 2: Generate API documentation with pydoc-markdown
    pydoc_config = docs_dir / "pydoc-markdown.yml"
    api_output_dir = docs_dir / "reference" / "api"

    # Check if pydoc-markdown is available
    try:
        subprocess.run(["pydoc-markdown", "--version"], check=True, capture_output=True)

        exit_code = run_command(
            [
                "pydoc-markdown",
                "--config",
                str(pydoc_config),
                "--render-toc",
                ">",
                str(api_output_dir / "simple.md"),
            ],
            "Generating API documentation",
        )

        if exit_code != 0:
            print("⚠️  API documentation generation had issues, continuing...")

    except FileNotFoundError:
        print("\n⚠️  pydoc-markdown not found, skipping API docs generation")
        print("   Install with: pip install pydoc-markdown")
        print("   Continuing with other steps...\n")

    # Step 3: Extract redirects from Sphinx conf.py
    redirects_script = script_dir / "extract-redirects.py"
    exit_code = run_command(
        [sys.executable, str(redirects_script)],
        "Extracting redirects from Sphinx config",
    )
    if exit_code != 0:
        print("⚠️  Redirect extraction had issues, continuing...")

    # Summary
    print("\n" + "╔" + "=" * 58 + "╗")
    print("║" + " " * 20 + "Build Summary" + " " * 25 + "║")
    print("╚" + "=" * 58 + "╝")

    print("\n✅ Documentation generation complete!")
    print("\nGenerated files:")
    print(f"  - Rule documentation: {docs_dir / 'reference' / 'rules'}")
    print(f"  - API documentation: {docs_dir / 'reference' / 'api'}")
    print(f"  - Redirects config: {docs_dir / '.vitepress' / 'redirects.json'}")
    print(f"  - Sidebar config: {docs_dir / '.vitepress' / 'sidebar-rules.json'}")

    print("\n📝 Next steps:")
    print("  1. Install Node dependencies: cd docs-vitepress && pnpm install")
    print("  2. Start dev server: pnpm run docs:dev")
    print("  3. Build for production: pnpm run docs:build")

    return 0


if __name__ == "__main__":
    exit(main())

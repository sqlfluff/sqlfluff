#!/usr/bin/env python3
"""Master script to generate all VitePress documentation.

This script orchestrates the entire documentation generation process:
1. Rule documentation (generate-rules-docs.py)
2. Dialect documentation (generate-dialects-docs.py)
3. CLI documentation (generate-cli-docs.py)
4. API documentation (generate-api-docs.py)
5. Redirect extraction (extract-redirects.py)
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

    # Step 2: Generate dialect documentation
    dialects_script = script_dir / "generate-dialects-docs.py"
    exit_code = run_command(
        [sys.executable, str(dialects_script)], "Generating dialect documentation"
    )
    if exit_code != 0:
        print("\n❌ Build failed at dialect documentation generation")
        return exit_code

    # Step 3: Generate CLI documentation
    cli_script = script_dir / "generate-cli-docs.py"
    exit_code = run_command(
        [sys.executable, str(cli_script)], "Generating CLI documentation"
    )
    if exit_code != 0:
        print("\n❌ Build failed at CLI documentation generation")
        return exit_code

    # Step 4: Generate API documentation
    api_script = script_dir / "generate-api-docs.py"
    exit_code = run_command(
        [sys.executable, str(api_script)], "Generating API documentation"
    )
    if exit_code != 0:
        print("\n❌ Build failed at API documentation generation")
        return exit_code

    # Step 5: Extract redirects from Sphinx conf.py
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
    print(f"  - Dialect documentation: {docs_dir / 'reference' / 'dialects'}")
    print(f"  - CLI documentation: {docs_dir / 'reference' / 'cli'}")
    print(f"  - API documentation: {docs_dir / 'reference' / 'api'}")
    print(f"  - Redirects config: {docs_dir / '.vitepress' / 'redirects.json'}")
    print(
        f"  - Sidebar config (rules): {docs_dir / '.vitepress' / 'sidebar-rules.json'}"
    )
    # Break into two lines for readability: label on one line, path on the next
    print("  - Sidebar config (dialects):")
    print(f"    {docs_dir / '.vitepress' / 'sidebar-dialects.json'}")
    print(f"  - Sidebar config (CLI): {docs_dir / '.vitepress' / 'sidebar-cli.json'}")
    print(f"  - Sidebar config (API): {docs_dir / '.vitepress' / 'sidebar-api.json'}")

    return 0


if __name__ == "__main__":
    exit(main())

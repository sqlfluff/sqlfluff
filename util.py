#!/usr/bin/env python

"""Utility strings for use during deployment.

NB: This is not part of the core sqlfluff code.
"""


# This contains various utility scripts

import os
import re
import shutil
import time

import click
from fastcore.net import HTTPError
from ghapi.all import GhApi


@click.group()
def cli():
    """Launch the utility cli."""
    pass


@cli.command()
@click.option("--path", default=".test-reports")
def clean_tests(path):
    """Clear up the tests directory.

    NB: Using scripts allows platform independence
    Makes a new one afterward
    """
    try:
        shutil.rmtree(path)
        click.echo(f"Removed {path!r}...")
    # OSError is for python 27
    # in py36 its FileNotFoundError (but that inherits from IOError, which exists in
    # py27)
    except OSError:
        click.echo(f"Directory {path!r} does not exist. Skipping...")

    os.mkdir(path)
    click.echo(f"Created {path!r}")


@cli.command()
@click.argument("new_version_num")
def release(new_version_num):
    """Change version number in the cfg files.

    NOTE: For fine grained personal access tokens, this requires
    _write_ access to the "contents" scope. For dome reason, if you
    only grant the _read_ access, you can't see any *draft* PRs
    which are necessary for this script to run.
    """
    api = GhApi(
        owner=os.environ["GITHUB_REPOSITORY_OWNER"],
        repo="sqlfluff",
        token=os.environ["GITHUB_TOKEN"],
    )
    try:
        releases = api.repos.list_releases(per_page=100)
    except HTTPError as err:
        raise click.UsageError(
            "HTTP Error from GitHub API. Check your credentials.\n"
            "(i.e. GITHUB_REPOSITORY_OWNER & GITHUB_TOKEN)\n"
            f"{err}"
        )

    latest_draft_release = None
    for rel in releases:
        if rel["draft"]:
            latest_draft_release = rel
            break

    if not latest_draft_release:
        raise click.UsageError(
            "No draft release found on GitHub.\n"
            "This could be because the GitHub action which generates it is broken, "
            "but is more likely due to using an API token which only has read-only "
            "access to the `sqlfluff/sqlfluff` repository. This script requires an "
            "API token with `read and write` access to the `contents` scope in "
            "order to be able to view draft releases."
        )

    # Pre-releases are identifiable because they contain letters.
    # https://peps.python.org/pep-0440/
    is_pre_release = any(char.isalpha() for char in new_version_num)
    click.echo(
        f"Preparing for release {new_version_num}. (Pre-release: {is_pre_release})"
    )

    # Linkify the PRs and authors
    draft_body_parts = latest_draft_release["body"].split("\n")
    potential_new_contributors = []
    for i, p in enumerate(draft_body_parts):
        draft_body_parts[i] = re.sub(
            r"\(#([0-9]*)\) @([^ ]*)$",
            r"[#\1](https://github.com/sqlfluff/sqlfluff/pull/\1) [@\2](https://github.com/\2)",  # noqa E501
            p,
        )
        new_contrib_string = re.sub(
            r".*\(#([0-9]*)\) @([^ ]*)$",
            r"* [@\2](https://github.com/\2) made their first contribution in [#\1](https://github.com/sqlfluff/sqlfluff/pull/\1)",  # noqa E501
            p,
        )
        if new_contrib_string.startswith("* "):
            new_contrib_name = re.sub(r"\* \[(.*?)\].*", r"\1", new_contrib_string)
            potential_new_contributors.append(
                {"name": new_contrib_name, "line": new_contrib_string}
            )
    whats_changed_text = "\n".join(draft_body_parts)

    # Find the first commit for each contributor in this release
    potential_new_contributors.reverse()
    seen_contributors = set()
    deduped_potential_new_contributors = []
    for c in potential_new_contributors:
        if c["name"] not in seen_contributors:
            seen_contributors.add(c["name"])
            deduped_potential_new_contributors.append(c)

    click.echo("Updating CHANGELOG.md...")
    input_changelog = open("CHANGELOG.md", encoding="utf8").readlines()
    write_changelog = open("CHANGELOG.md", "w", encoding="utf8")
    for i, line in enumerate(input_changelog):
        write_changelog.write(line)
        if "DO NOT DELETE THIS LINE" in line:
            existing_entry_start = i + 2
            new_heading = f"## [{new_version_num}] - {time.strftime('%Y-%m-%d')}\n"
            # If the release is already in the changelog, update it
            if f"## [{new_version_num}]" in input_changelog[existing_entry_start]:
                click.echo(f"...found existing entry for {new_version_num}")
                # Update the existing heading with the new date.
                input_changelog[existing_entry_start] = new_heading

                # Delete the existing What’s Changed and New Contributors sections
                remaining_changelog = input_changelog[existing_entry_start:]
                existing_whats_changed_start = (
                    next(
                        j
                        for j, line in enumerate(remaining_changelog)
                        if line.startswith("## What’s Changed")
                    )
                    + existing_entry_start
                )
                existing_new_contributors_start = (
                    next(
                        j
                        for j, line in enumerate(remaining_changelog)
                        if line.startswith("## New Contributors")
                    )
                    + existing_entry_start
                )
                existing_new_contributors_length = (
                    next(
                        j
                        for j, line in enumerate(
                            input_changelog[existing_new_contributors_start:]
                        )
                        if line.startswith("## [")
                    )
                    - 1
                )

                del input_changelog[
                    existing_whats_changed_start : existing_new_contributors_start
                    + existing_new_contributors_length
                ]

                # Now that we've cleared the previous sections, we will accurately
                # find if contributors have been previously mentioned in the changelog
                new_contributor_lines = []
                input_changelog_str = "".join(
                    input_changelog[existing_whats_changed_start:]
                )
                for c in deduped_potential_new_contributors:
                    if c["name"] not in input_changelog_str:
                        new_contributor_lines.append(c["line"])
                input_changelog[existing_whats_changed_start] = (
                    whats_changed_text
                    + "\n\n## New Contributors\n"
                    + "\n".join(new_contributor_lines)
                    + "\n\n"
                )

            else:
                click.echo(f"...creating new entry for {new_version_num}")
                write_changelog.write(f"\n{new_heading}\n## Highlights\n\n")
                write_changelog.write(whats_changed_text)
                write_changelog.write("\n## New Contributors\n\n")
                # Ensure contributor names don't appear in input_changelog list
                new_contributor_lines = []
                input_changelog_str = "".join(input_changelog)
                for c in deduped_potential_new_contributors:
                    if c["name"] not in input_changelog_str:
                        new_contributor_lines.append(c["line"])
                write_changelog.write("\n".join(new_contributor_lines))
                write_changelog.write("\n")

    write_changelog.close()

    click.echo("Updating plugins/sqlfluff-templater-dbt/setup.cfg")
    for filename in ["plugins/sqlfluff-templater-dbt/setup.cfg"]:
        input_file = open(filename, "r").readlines()
        # Regardless of platform, write newlines as \n
        write_file = open(filename, "w", newline="\n")
        for line in input_file:
            if line.startswith("version"):
                line = f"version = {new_version_num}\n"
            elif line.startswith("    sqlfluff=="):
                line = f"    sqlfluff=={new_version_num}\n"
            write_file.write(line)
        write_file.close()

    keys = ["version"]
    if not is_pre_release:
        # Only update stable_version if it's not a pre-release.
        keys.append("stable_version")

    click.echo("Updating pyproject.toml")
    for filename in ["pyproject.toml"]:
        input_file = open(filename, "r").readlines()
        # Regardless of platform, write newlines as \n
        write_file = open(filename, "w", newline="\n")
        for line in input_file:
            for key in keys:
                if line.startswith(key):
                    # For pyproject.toml we quote the version identifier.
                    line = f'{key} = "{new_version_num}"\n'
                    break
            write_file.write(line)
        write_file.close()

    if not is_pre_release:
        click.echo("Updating gettingstarted.rst")
        for filename in ["docs/source/gettingstarted.rst"]:
            input_file = open(filename, "r").readlines()
            # Regardless of platform, write newlines as \n
            write_file = open(filename, "w", newline="\n")
            change_next_line = False
            for line in input_file:
                if change_next_line:
                    line = f"    {new_version_num}\n"
                    change_next_line = False
                elif line.startswith("    $ sqlfluff version"):
                    change_next_line = True
                write_file.write(line)
            write_file.close()

    click.echo("DONE")


if __name__ == "__main__":
    cli()

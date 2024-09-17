"""Utility to generate yml files for all the parsing examples."""

import fnmatch
import multiprocessing
import os
import re
import sys
import time
from collections import defaultdict
from typing import Callable, Dict, List, Optional, Tuple, TypeVar

import click
import yaml
from conftest import (
    ParseExample,
    compute_parse_tree_hash,
    get_parse_fixtures,
    parse_example_file,
)

from sqlfluff.core.errors import SQLParseError

S = TypeVar("S", bound="ParseExample")


def distribute_work(work_items: List[S], work_fn: Callable[[S], None]) -> None:
    """Distribute work keep track of progress."""
    # Build up a dict of sets, where the key is the dialect and the set
    # contains all the expected cases. As cases return we'll check them
    # off.
    success_map = {}

    expected_cases = defaultdict(set)
    for case in work_items:
        expected_cases[case.dialect].add(case)

    errors = []

    with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
        for example, result in pool.imap_unordered(work_fn, work_items):
            if result is not None:
                errors.append(result)
                success_map[example] = False
            else:
                success_map[example] = True

            expected_cases[example.dialect].remove(example)
            # Check to see whether a dialect is complete
            if not expected_cases[example.dialect]:
                # It's done. Report success rate.
                local_success_map = {
                    k: v for k, v in success_map.items() if k.dialect == example.dialect
                }
                if all(local_success_map.values()):
                    print(f"{example.dialect!r} complete.\t\tAll Success ✅")
                else:
                    fail_files = [
                        k.sqlfile for k, v in local_success_map.items() if not v
                    ]
                    print(
                        f"{example.dialect!r} complete.\t\t{len(fail_files)} fails. ⚠️"
                    )
                    for fname in fail_files:
                        print(f"  - {fname!r}")

    if errors:
        print(errors)
        print("FAILED TO GENERATE ALL CASES")
        sys.exit(1)


def _create_file_path(example: ParseExample, ext: str = ".yml") -> str:
    dialect, sqlfile = example
    root, _ = os.path.splitext(sqlfile)
    path = os.path.join("test", "fixtures", "dialects", dialect, root + ext)
    return path


def _is_matching_new_criteria(example: ParseExample):
    """Is the Yaml doesn't exist or is older than the SQL."""
    yaml_path = _create_file_path(example)
    if not os.path.exists(yaml_path):
        return True

    sql_path = os.path.join(
        "test",
        "fixtures",
        "dialects",
        example.dialect,
        example.sqlfile,
    )
    return os.path.getmtime(yaml_path) < os.path.getmtime(sql_path)


def generate_one_parse_fixture(
    example: ParseExample,
) -> Tuple[ParseExample, Optional[SQLParseError]]:
    """Parse example SQL file, write parse tree to YAML file."""
    dialect, sqlfile = example
    sql_path = _create_file_path(example, ".sql")

    try:
        tree = parse_example_file(dialect, sqlfile)
    except Exception as err:
        # Catch parsing errors, and wrap the file path only it.
        return example, SQLParseError(f"Fatal parsing error: {sql_path}: {err}")

    # Check we don't have any base types or unparsable sections
    types = tree.type_set()
    if "base" in types:
        return example, SQLParseError(f"Unnamed base section when parsing: {sql_path}")
    if "unparsable" in types:
        return example, SQLParseError(f"Could not parse: {sql_path}")

    _hash = compute_parse_tree_hash(tree)
    # Remove the .sql file extension
    path = _create_file_path(example)
    with open(path, "w", newline="\n") as f:
        r: Optional[Dict[str, Optional[str]]] = None

        if not tree:
            f.write("")
            return example, None

        records = tree.as_record(code_only=True, show_raw=True)
        assert records, "TypeGuard"
        r = dict([("_hash", _hash), *list(records.items())])
        print(
            "# YML test files are auto-generated from SQL files and should not be "
            "edited by",
            '# hand. To help enforce this, the "hash" field in the file must match '
            "a hash",
            "# computed by SQLFluff when running the tests. Please run",
            "# `python test/generate_parse_fixture_yml.py`  to generate them after "
            "adding or",
            "# altering SQL files.",
            file=f,
            sep="\n",
        )
        yaml.dump(
            data=r,
            stream=f,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )
        return example, None


def gather_file_list(
    dialect: Optional[str] = None,
    glob_match_pattern: Optional[str] = None,
    new_only: bool = False,
) -> List[ParseExample]:
    """Gather the list of files to generate fixtures for. Apply filters as required."""
    parse_success_examples, _ = get_parse_fixtures()
    if new_only:
        parse_success_examples = [
            example
            for example in parse_success_examples
            if _is_matching_new_criteria(example)
        ]

    if dialect:
        dialect = dialect.lower()
        parse_success_examples = [
            example for example in parse_success_examples if example[0] == dialect
        ]
        if len(parse_success_examples) == 0:
            raise ValueError(f'Unknown Dialect "{dialect}"')

    if not glob_match_pattern:
        return parse_success_examples

    regex = re.compile(fnmatch.translate(glob_match_pattern))
    return [
        example
        for example in parse_success_examples
        if regex.match(example[1]) is not None
    ]


@click.command()
@click.option(
    "--filter", "-f", default=None, help="A glob filter to apply to file names."
)
@click.option("--dialect", "-d", default=None, help="Filter to a given dialect.")
@click.option(
    "--new-only",
    "new_only",
    is_flag=True,
    default=False,
    help="Only create missing fixtures.",
)
def generate_parse_fixtures(
    filter: Optional[str], dialect: Optional[str], new_only: bool
):
    """Generate fixture or a subset based on dialect or filename glob match."""
    filter_str = filter or "*"
    dialect_str = dialect or "all"
    print("Match Pattern Received:")
    print(f"\tfilter={filter_str} dialect={dialect_str} new-only={new_only}")
    parse_success_examples = gather_file_list(dialect, filter, new_only)
    print(f"Found {len(parse_success_examples)} file(s) to generate")
    t0 = time.monotonic()
    try:
        distribute_work(parse_success_examples, generate_one_parse_fixture)
    except SQLParseError as err:
        # If one fails, exit early and cleanly.
        print(f"PARSING FAILED: {err}")
        sys.exit(1)
    dt = time.monotonic() - t0
    print(f"Built {len(parse_success_examples)} fixtures in {dt:.2f}s.")


def main():
    """Find all example SQL files, parse and create YAML files."""
    generate_parse_fixtures()


if __name__ == "__main__":
    main()

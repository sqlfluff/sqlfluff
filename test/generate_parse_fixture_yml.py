"""Utility to generate yml files for all the parsing examples."""
import multiprocessing
import os
import fnmatch
import re
import click
from typing import Callable, Dict, List, Optional, TypeVar


import yaml

from conftest import (
    compute_parse_tree_hash,
    get_parse_fixtures,
    parse_example_file,
    ParseExample,
)
from sqlfluff.core.errors import SQLParseError


S = TypeVar("S")


def distribute_work(work_items: List[S], work_fn: Callable[[S], None]) -> None:
    """Distribute work and ignore results."""
    with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
        for _ in pool.imap_unordered(work_fn, work_items):
            pass


def _create_yaml_path(example: ParseExample) -> str:
    dialect, sqlfile = example
    root, _ = os.path.splitext(sqlfile)
    path = os.path.join("test", "fixtures", "dialects", dialect, root + ".yml")
    return path


def _is_matching_new_criteria(example: ParseExample):
    """Is the Yaml doesn't exist or is older than the SQL."""
    yaml_path = _create_yaml_path(example)
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


def generate_one_parse_fixture(example: ParseExample) -> None:
    """Parse example SQL file, write parse tree to YAML file."""
    dialect, sqlfile = example
    tree = parse_example_file(dialect, sqlfile)
    _hash = compute_parse_tree_hash(tree)
    # Remove the .sql file extension
    path = _create_yaml_path(example)
    with open(path, "w", newline="\n") as f:
        r: Optional[Dict[str, Optional[str]]] = None

        if not tree:
            f.write("")
            return

        # Check we don't have any base types or unparsable sections
        types = tree.type_set()
        if "base" in types:
            raise SQLParseError(f"Unnamed base section when parsing: {f.name}")
        if "unparsable" in types:
            for unparsable in tree.iter_unparsables():
                print("Found unparsable segment...")
                print(unparsable.stringify())
            raise SQLParseError(f"Could not parse: {f.name}")

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
        yaml.dump(r, f, default_flow_style=False, sort_keys=False)
        return


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
    distribute_work(parse_success_examples, generate_one_parse_fixture)
    print(f"Fixture built: {len(parse_success_examples)}")


def main():
    """Find all example SQL files, parse and create YAML files."""
    generate_parse_fixtures()


if __name__ == "__main__":
    main()

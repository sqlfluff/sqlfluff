"""Utility to generate yml files for all the parsing examples."""
import multiprocessing
import os

import yaml

from conftest import compute_parse_tree_hash, get_parse_fixtures, parse_example_file


def generate_parse_fixture(example):
    """Parse example SQL file, write parse tree to YAML file."""
    dialect, sqlfile = example
    tree = parse_example_file(dialect, sqlfile)
    _hash = compute_parse_tree_hash(tree)
    # Remove the .sql file extension
    root = sqlfile[:-4]
    path = os.path.join("test", "fixtures", "dialects", dialect, root + ".yml")
    with open(path, "w", newline="\n") as f:
        r = None
        if tree:
            r = dict(
                [("_hash", _hash)]
                + list(tree.as_record(code_only=True, show_raw=True).items())
            )
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
        else:
            f.write("")


def main():
    """Find all example SQL files, parse and create YAML files."""
    parse_success_examples, _ = get_parse_fixtures()
    with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
        for _ in pool.imap_unordered(generate_parse_fixture, parse_success_examples):
            pass


if __name__ == "__main__":
    main()

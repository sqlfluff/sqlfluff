"""Utility to generate yml files for all the parsing examples."""
import os

import oyaml as yaml

from conftest import compute_parse_tree_hash, parse_example_file
from dialects.parse_fixtures import get_parse_fixtures


def generate_parse_fixture(dialect, sqlfile):
    """Parse example SQL file, write parse tree to YAML file."""
    tree = parse_example_file(dialect, sqlfile)
    _hash = compute_parse_tree_hash(tree)
    # Remove the .sql file extension
    root = sqlfile[:-4]
    path = os.path.join("test", "fixtures", "parser", dialect, root + ".yml")
    with open(path, "w", newline="\n") as f:
        r = None
        if tree:
            r = dict(
                [("_hash", _hash)]
                + list(tree.as_record(code_only=True, show_raw=True).items())
            )
            yaml.dump(r, f, default_flow_style=False)
        else:
            f.write("")


def main():
    """Find all example SQL files, parse and create YAML files."""
    parse_success_examples, _ = get_parse_fixtures()
    for example in parse_success_examples:
        dialect, sqlfile = example
        generate_parse_fixture(dialect, sqlfile)


if __name__ == "__main__":
    main()

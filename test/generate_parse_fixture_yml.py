"""Utility to generate yml files for all the parsing examples."""
import os

import oyaml as yaml

from sqlfluff.cli.commands import quoted_presenter

from conftest import compute_parse_tree_hash, parse_example_file
from dialects.parse_fixtures import get_parse_fixtures

yaml.add_representer(str, quoted_presenter)

def generate_parse_fixture(dialect, sqlfile):
    tree = parse_example_file(dialect, sqlfile)
    _hash = compute_parse_tree_hash(tree)
    # Remove the .sql file extension
    root = sqlfile[:-4]
    path = os.path.join("test", "fixtures", "parser", dialect, root + ".yml")
    with open(path, "w", newline="\n") as f:
        r = None
        if tree:
            r = dict(
                [('_hash', _hash)] + list(
                    tree.as_record(code_only=True, show_raw=True).items())
            )
            yaml.dump(r, f, default_flow_style=False)
        else:
            f.write("")


def main():
    parse_success_examples, _ = get_parse_fixtures()
    for example in parse_success_examples:
        dialect, sqlfile = example
        generate_parse_fixture(dialect, sqlfile)


if __name__ == '__main__':
    main()

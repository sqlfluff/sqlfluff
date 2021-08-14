"""Utility to generate yml files for all the parsing examples."""
import hashlib
import io
import os

import oyaml as yaml

from sqlfluff.core.parser import Parser, Lexer
from sqlfluff.core import FluffConfig
from sqlfluff.cli.commands import quoted_presenter

from conftest import compute_parse_tree_hash
from dialects.parse_fixtures import get_parse_fixtures, load_file

yaml.add_representer(str, quoted_presenter)

def main():
    parse_success_examples, _ = get_parse_fixtures()

    for example in parse_success_examples:
        dialect, sqlfile = example
        config = FluffConfig(overrides=dict(dialect=dialect))
        # Load the SQL
        raw = load_file(dialect, sqlfile)
        # Lex and parse the file
        tokens, _ = Lexer(config=config).lex(raw)
        tree = Parser(config=config).parse(tokens)
        # Remove the .sql file extension
        root = sqlfile[:-4]
        path = os.path.join("test", "fixtures", "parser", dialect, root + ".yml")
        with open(path, "w", newline="\n") as f:
            r = None
            if tree:
                r = dict(
                    [('_hash', compute_parse_tree_hash(tree))] + list(tree.as_record(code_only=True, show_raw=True).items())
                )
                yaml.dump(r, f, default_flow_style=False)
            else:
                f.write("")

if __name__ == '__main__':
    main()

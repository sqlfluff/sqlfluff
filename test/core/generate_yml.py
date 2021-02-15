"""Utility to generate yml files for all the parsing examples."""
import os

import oyaml as yaml

from sqlfluff.core.parser import Parser, Lexer
from sqlfluff.core import FluffConfig

from dialects.dialects_test import parse_structure_examples, load_file


def quoted_presenter(dumper, data):
    """Re-presenter which always double quotes string values needing escapes."""
    if "\n" in data or "\t" in data or "'" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')
    else:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="")


yaml.add_representer(str, quoted_presenter)

for example in parse_structure_examples:
    dialect, sqlfile, _, _ = example
    config = FluffConfig(overrides=dict(dialect=dialect))
    # Load the SQL
    raw = load_file(dialect, sqlfile)
    # Lex and parse the file
    tokens, _ = Lexer(config=config).lex(raw)
    tree = Parser(config=config).parse(tokens)
    d = None
    if tree:
        d = tree.as_record(code_only=True, show_raw=True)
    root = sqlfile[:-4]
    y = os.path.join("test", "fixtures", "parser", dialect, root + ".yml")
    with open(y, "w") as f:
        yaml.dump(d, f)

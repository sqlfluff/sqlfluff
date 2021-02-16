"""Automated tests for all dialects.

Any files in the /tests/fixtures/parser directoy will be picked up
and automatically tested against the appropriate dialect.
"""

import pytest
import os

from sqlfluff.core.parser import Parser, Lexer
from sqlfluff.core import FluffConfig


# Construct the tests from the filepath
parse_success_examples = []
parse_structure_examples = []

# Generate the filenames for each dialect from the parser test directory
for d in os.listdir(os.path.join("test", "fixtures", "parser")):
    # Ignore documentation
    if d.endswith(".md"):
        continue
    # assume that d is now the name of a dialect
    dirlist = os.listdir(os.path.join("test", "fixtures", "parser", d))
    for f in dirlist:
        has_yml = False
        if f.endswith(".sql"):
            root = f[:-4]
            # only look for sql files
            parse_success_examples.append((d, f))
            # Look for the code_only version of the structure
            y = root + ".yml"
            if y in dirlist:
                parse_structure_examples.append((d, f, True, y))
                has_yml = True
            # Look for the non-code included version of the structure
            y = root + "_nc.yml"
            if y in dirlist:
                parse_structure_examples.append((d, f, False, y))
                has_yml = True
            if not has_yml:
                raise (
                    Exception(
                        f"Missing .yml file for {os.path.join(d, f)}. Run the test/core/generate_parse_fixture_yml.py script!"
                    )
                )


def make_dialect_path(dialect, fname):
    """Work out how to find paths given a dialect and a file name."""
    return os.path.join("test", "fixtures", "parser", dialect, fname)


def load_file(dialect, fname):
    """Load a file."""
    with open(make_dialect_path(dialect, fname)) as f:
        raw = f.read()
    return raw


@pytest.mark.parametrize("dialect,file", parse_success_examples)
def test__dialect__base_file_parse(dialect, file):
    """For given test examples, check successful parsing."""
    raw = load_file(dialect, file)
    # Load the right dialect
    config = FluffConfig(overrides=dict(dialect=dialect))
    tokens, lex_vs = Lexer(config=config).lex(raw)
    # From just the initial parse, check we're all there
    assert "".join(token.raw for token in tokens) == raw
    # Check we don't have lexing issues
    assert not lex_vs

    # Do the parse WITHOUT lots of logging
    # The logs get too long here to be useful. We should use
    # specific segment tests if we want to debug logs.
    if raw:
        parsed = Parser(config=config).parse(tokens)
        print("Post-parse structure: {0}".format(parsed.to_tuple(show_raw=True)))
        print("Post-parse structure: {0}".format(parsed.stringify()))
        # Check we're all there.
        assert parsed.raw == raw
        # Check that there's nothing unparsable
        typs = parsed.type_set()
        assert "unparsable" not in typs


@pytest.mark.parametrize("dialect,sqlfile,code_only,yamlfile", parse_structure_examples)
def test__dialect__base_parse_struct(
    dialect, sqlfile, code_only, yamlfile, yaml_loader
):
    """For given test examples, check parsed structure against yaml."""
    # Load the right dialect
    config = FluffConfig(overrides=dict(dialect=dialect))
    # Load the SQL
    raw = load_file(dialect, sqlfile)
    # Lex and parse the file
    tokens, _ = Lexer(config=config).lex(raw)
    parsed = Parser(config=config).parse(tokens)
    # Load the YAML
    res = yaml_loader(make_dialect_path(dialect, yamlfile))
    if parsed:
        assert parsed.to_tuple(code_only=code_only, show_raw=True) == res
    else:
        assert parsed == res

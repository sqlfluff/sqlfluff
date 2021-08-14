"""Automated tests for all dialects.

Any files in the /tests/fixtures/parser directoy will be picked up
and automatically tested against the appropriate dialect.
"""

import pytest

from sqlfluff.core.parser import Parser, Lexer
from sqlfluff.core import FluffConfig

from .parse_fixtures import get_parse_fixtures, load_file, make_dialect_path

parse_success_examples, parse_structure_examples = get_parse_fixtures(
    fail_on_missing_yml=True
)


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
        print(f"Post-parse structure: {parsed.to_tuple(show_raw=True)}")
        print(f"Post-parse structure: {parsed.stringify()}")
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
    _hash, res = yaml_loader(make_dialect_path(dialect, yamlfile))
    if parsed:
        assert parsed.to_tuple(code_only=code_only, show_raw=True) == res
    else:
        assert parsed == res

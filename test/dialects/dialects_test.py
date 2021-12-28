"""Automated tests for all dialects.

Any files in the test/fixtures/dialects/ directory will be picked up
and automatically tested against the appropriate dialect.
"""

import pytest

from sqlfluff.core.parser import Parser, Lexer
from sqlfluff.core import FluffConfig

from ..conftest import (
    compute_parse_tree_hash,
    parse_example_file,
    load_file,
    make_dialect_path,
    get_parse_fixtures,
)

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
    parsed = parse_example_file(dialect, sqlfile)
    actual_hash = compute_parse_tree_hash(parsed)
    # Load the YAML
    expected_hash, res = yaml_loader(make_dialect_path(dialect, yamlfile))
    if parsed:
        # Verify the current parse tree matches the historic parse tree.
        parsed_tree = parsed.to_tuple(code_only=code_only, show_raw=True)
        # The prased tree consists of a tuple of "File:", followed by the
        # statements. So only compare when there is at least one statement.
        if parsed_tree[1] or res[1]:
            assert parsed_tree == res
        # Verify the current hash matches the historic hash. The main purpose of
        # this check is to force contributors to use the generator script to
        # to create these files. New contributors have sometimes been unaware of
        # this tool and have attempted to craft the YAML files manually. This
        # can lead to slight differences, confusion, and errors.
        assert expected_hash == actual_hash, (
            "Parse tree hash does not match. Please run "
            "'python test/generate_parse_fixture_yml.py' to create YAML files "
            "in test/fixtures/dialects."
        )
    else:
        assert parsed == res

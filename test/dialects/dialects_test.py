"""Automated tests for all dialects.

Any files in the test/fixtures/dialects/ directory will be picked up
and automatically tested against the appropriate dialect.
"""

from functools import cache
from typing import Any, Dict, Optional
import pytest

from sqlfluff.core.parser import Parser, Lexer
from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.parser.segments.base import BaseSegment

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

@cache
def lex_and_parse(config_overrides: Dict[str, Any], raw:str) -> Optional[BaseSegment]:
    """Performs a Lex and Parse, and caches result for further steps."""
    print("LINTING!")
    # Load the right dialect
    config = FluffConfig(overrides=config_overrides)
    tokens, lex_vs = Lexer(config=config).lex(raw)
    # From just the initial parse, check we're all there
    assert "".join(token.raw for token in tokens) == raw
    # Check we don't have lexing issues
    assert not lex_vs

    # Do the parse WITHOUT lots of logging
    # The logs get too long here to be useful. We should use
    # specific segment tests if we want to debug logs.
    if not raw:
        return None

    return Parser(config=config).parse(tokens)


@pytest.mark.parametrize("dialect,file", parse_success_examples)
def test__dialect__base_file_parse(dialect, file):
    """For given test examples, check successful parsing."""
    config_overides = dict(dialect=dialect)
    raw = load_file(config_overides, file)
    # Use the helper function to avoid parsing twice
    parsed = lex_and_parse(dialect, raw)
    if not parsed:
        return

    print(f"Post-parse structure: {parsed.to_tuple(show_raw=True)}")
    print(f"Post-parse structure: {parsed.stringify()}")
    # Check we're all there.
    assert parsed.raw == raw
    # Check that there's nothing unparsable
    typs = parsed.type_set()
    assert "unparsable" not in typs


@pytest.mark.parametrize("dialect,file", parse_success_examples)
def test__dialect__base_broad_fix(dialect, file, raise_critical_errors_after_fix):
    """For given test examples, check successful parsing."""
    raw = load_file(dialect, file)
    config_overides = dict(dialect=dialect)
    # Lean on the cached result of the above test if possible
    parsed = lex_and_parse(config_overides, raw)
    if not parsed:
        return

    # Due to "raise_critical_errors_after_fix" fixure "fix",
    # will now throw.
    config = FluffConfig(overrides=config_overides)
    Linter(config=config).fix(parsed)


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

"""Automated tests for all dialects.

Any files in the test/fixtures/dialects/ directory will be picked up
and automatically tested against the appropriate dialect.
"""
from typing import Any, Dict, Optional
import pytest

from sqlfluff.core.parser import Parser, Lexer
from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.parser.segments.base import BaseSegment

from ..conftest import (
    compute_parse_tree_hash,
    load_file,
    make_dialect_path,
    parse_example_file,
    get_parse_fixtures,
)

parse_success_examples, parse_structure_examples = get_parse_fixtures(
    fail_on_missing_yml=True
)


def lex_and_parse(config_overrides: Dict[str, Any], raw: str) -> Optional[BaseSegment]:
    """Performs a Lex and Parse, with cachable inputs within fixture."""
    # Load the right dialect
    config = FluffConfig(overrides=config_overrides)
    tokens, lex_vs = Lexer(config=config).lex(raw)
    # From just the initial parse, check we're all there
    assert "".join(token.raw for token in tokens) == raw
    # Check we don't have lexing issues
    assert not lex_vs
    # TODO: Handle extremely verbose logging
    # temp - use negative grep: | grep -v "INFO\|DEBUG\|\[L\|#\|Initial\|^$"
    # better maybe - https://docs.pytest.org/en/6.2.x/logging.html#caplog-fixture

    if not raw:
        return None

    return Parser(config=config).parse(tokens)


@pytest.mark.integration_test
@pytest.mark.parametrize("dialect,file", parse_success_examples)
def test__dialect__base_broad_fix(dialect, file, raise_critical_errors_after_fix):
    """Run a full fix with all rules, in search of critical errors."""
    raw = load_file(dialect, file)
    config_overides = dict(dialect=dialect)
    # Lean on the cached result of the above test if possible
    parsed: Optional[BaseSegment] = lex_and_parse(config_overides, raw)
    if not parsed:
        return

    config = FluffConfig(overrides=config_overides)
    # Due to "raise_critical_errors_after_fix" fixure "fix",
    # will now throw.
    Linter(config=config).lint_string(raw, fix=True)


@pytest.mark.parametrize("dialect,sqlfile,code_only,yamlfile", parse_structure_examples)
def test__dialect__base_parse_struct(
    dialect,
    sqlfile,
    code_only,
    yamlfile,
    yaml_loader,
):
    """For given test examples, check parsed structure against yaml."""
    parsed: Optional[BaseSegment] = parse_example_file(dialect, sqlfile)
    actual_hash = compute_parse_tree_hash(parsed)
    # Load the YAML
    expected_hash, res = yaml_loader(make_dialect_path(dialect, yamlfile))
    if not parsed:
        assert parsed == res
        return

    # Verify the current parse tree matches the historic parse tree.
    parsed_tree = parsed.to_tuple(code_only=code_only, show_raw=True)
    # The parsed tree consists of a tuple of "File:", followed by the
    # statements. So only compare when there is at least one statement.
    if parsed_tree[1] or res[1]:
        assert parsed_tree == res
    # Verify the current hash matches the historic hash. The main purpose of
    # this check is to force contributors to use the generator script to
    # create these files. New contributors have sometimes been unaware of
    # this tool and have attempted to craft the YAML files manually. This
    # can lead to slight differences, confusion, and errors.
    assert expected_hash == actual_hash, (
        "Parse tree hash does not match. Please run "
        "'python test/generate_parse_fixture_yml.py' to create YAML files "
        "in test/fixtures/dialects."
    )

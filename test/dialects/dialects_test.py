"""Automated tests for all dialects.

Any files in the test/fixtures/dialects/ directory will be picked up
and automatically tested against the appropriate dialect.
"""

from typing import Any, Dict, Optional

import pytest

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.linter import ParsedString, RenderedFile
from sqlfluff.core.parser.segments.base import BaseSegment
from sqlfluff.core.templaters import TemplatedFile

from ..conftest import (
    compute_parse_tree_hash,
    get_parse_fixtures,
    load_file,
    make_dialect_path,
    parse_example_file,
)

parse_success_examples, parse_structure_examples = get_parse_fixtures(
    fail_on_missing_yml=True
)


def lex_and_parse(config_overrides: Dict[str, Any], raw: str) -> Optional[ParsedString]:
    """Performs a Lex and Parse, with cacheable inputs within fixture."""
    # Load the right dialect
    config = FluffConfig(overrides=config_overrides)
    # Construct rendered file (to skip the templater)
    templated_file = TemplatedFile.from_string(raw)
    rendered_file = RenderedFile(
        [templated_file],
        [],
        config,
        {},
        templated_file.fname,
        "utf8",
        raw,
    )
    # Parse (which includes lexing)
    linter = Linter(config=config)
    parsed_file = linter.parse_rendered(rendered_file)
    if not raw:  # Empty file case
        # We're just checking there aren't exceptions in this case.
        return None
    # Check we managed to parse
    assert parsed_file.parsed_variants
    root_variant = parsed_file.root_variant()
    assert root_variant
    assert root_variant.tree
    # From just the initial parse, check we're all there
    assert "".join(token.raw for token in root_variant.tree.raw_segments) == raw
    # Check we don't have lexing or parsing issues
    assert not parsed_file.violations()
    return parsed_file


@pytest.mark.integration
@pytest.mark.parse_suite
@pytest.mark.parametrize("dialect,file", parse_success_examples)
def test__dialect__base_file_parse(dialect, file):
    """For given test examples, check successful parsing."""
    raw = load_file(dialect, file)
    config_overrides = dict(dialect=dialect)
    # Use the helper function to avoid parsing twice
    parsed: Optional[ParsedString] = lex_and_parse(config_overrides, raw)
    if not parsed:  # Empty file case
        return
    tree = parsed.root_variant().tree
    print(f"Post-parse structure: {tree.to_tuple(show_raw=True)}")
    print(f"Post-parse structure: {tree.stringify()}")
    # Check we're all there.
    assert tree.raw == raw
    # Check that there's nothing unparsable
    types = tree.type_set()
    assert "unparsable" not in types
    # When testing the validity of fixes we re-parse sections of the file.
    # To ensure this is safe - here we re-parse the unfixed file to ensure
    # it's still valid even in the case that no fixes have been applied.
    assert tree.validate_segment_with_reparse(parsed.config.get("dialect_obj"))


@pytest.mark.integration
@pytest.mark.fix_suite
@pytest.mark.parametrize("dialect,file", parse_success_examples)
def test__dialect__base_broad_fix(
    dialect, file, raise_critical_errors_after_fix, caplog
):
    """Run a full fix with all rules, in search of critical errors.

    NOTE: This suite does all of the same things as the above test
    suite (the `parse_suite`), but also runs fix. In CI, we run
    the above tests _with_ coverage tracking, but these we run
    _without_.

    The purpose of this test is as a more stretching run through
    a wide range of test sql examples, and the full range of rules
    to find any potential critical errors raised by any interactions
    between different dialects and rules.

    We also do not use DEBUG logging here because it gets _very_
    noisy.
    """
    raw = load_file(dialect, file)
    config_overrides = dict(dialect=dialect)

    parsed: Optional[ParsedString] = lex_and_parse(config_overrides, raw)
    if not parsed:  # Empty file case
        return
    tree = parsed.root_variant().tree
    print(tree.stringify())

    config = FluffConfig(overrides=config_overrides)
    linter = Linter(config=config)
    rule_pack = linter.get_rulepack()
    # Due to "raise_critical_errors_after_fix" fixture "fix",
    # will now throw.
    linter.lint_parsed(
        parsed,
        rule_pack,
        fix=True,
    )


@pytest.mark.integration
@pytest.mark.parse_suite
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

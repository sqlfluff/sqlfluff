"""Automated tests for all dialects.

Any files in the /tests/fixtures/parser directoy will be picked up
and automatically tested against the appropriate dialect.
"""

import pytest
import os

from sqlfluff.parser import FileSegment, RootParseContext
from sqlfluff.config import FluffConfig


# Construct the tests from the filepath
parse_success_examples = []
parse_structure_examples = []

# Generate the filenames for each dialect from the parser test directory
for d in os.listdir(os.path.join('test', 'fixtures', 'parser')):
    # Ignore documentation
    if d.endswith('.md'):
        continue
    # assume that d is now the name of a dialect
    dirlist = os.listdir(os.path.join('test', 'fixtures', 'parser', d))
    for f in dirlist:
        if f.endswith('.sql'):
            root = f[:-4]
            # only look for sql files
            parse_success_examples.append((d, f))
            # Look for the code_only version of the structure
            y = root + '.yml'
            if y in dirlist:
                parse_structure_examples.append((d, f, True, y))
            # Look for the non-code included version of the structure
            y = root + '_nc.yml'
            if y in dirlist:
                parse_structure_examples.append((d, f, False, y))


def make_dialect_path(dialect, fname):
    """Work out how to find paths given a dialect and a file name."""
    return os.path.join('test', 'fixtures', 'parser', dialect, fname)


def load_file(dialect, fname):
    """Load a file."""
    with open(make_dialect_path(dialect, fname)) as f:
        raw = f.read()
    return raw


@pytest.mark.parametrize(
    "dialect,file",
    parse_success_examples
)
def test__dialect__base_file_parse(dialect, file):
    """For given test examples, check successful parsing."""
    raw = load_file(dialect, file)
    # Load the right dialect
    config = FluffConfig(overrides=dict(dialect=dialect))
    fs, lex_vs = FileSegment.from_raw(raw, config=config)
    # From just the initial parse, check we're all there
    assert fs.raw == raw
    # Check we don't have lexing issues
    assert not lex_vs

    # Do the parse WITHOUT lots of logging
    # The logs get too long here to be useful. We should use
    # specfic segment tests if we want to debug logs.
    # with caplog.at_level(logging.DEBUG):
    print("Pre-parse structure: {0}".format(fs.to_tuple(show_raw=True)))
    print("Pre-parse structure: {0}".format(fs.stringify()))
    with RootParseContext.from_config(config) as ctx:  # Optional: set recurse=1 to limit recursion
        parsed = fs.parse(parse_context=ctx)
    print("Post-parse structure: {0}".format(fs.to_tuple(show_raw=True)))
    print("Post-parse structure: {0}".format(fs.stringify()))
    # Check we're all there.
    assert parsed.raw == raw
    # Check that there's nothing un parsable
    typs = parsed.type_set()
    assert 'unparsable' not in typs


@pytest.mark.parametrize(
    "dialect,sqlfile,code_only,yamlfile",
    parse_structure_examples
)
def test__dialect__base_parse_struct(dialect, sqlfile, code_only, yamlfile, yaml_loader):
    """For given test examples, check parsed structure against yaml."""
    # Load the right dialect
    config = FluffConfig(overrides=dict(dialect=dialect))
    # Load the SQL
    raw = load_file(dialect, sqlfile)
    fs, _ = FileSegment.from_raw(raw, config=config)
    # Load the YAML
    res = yaml_loader(make_dialect_path(dialect, yamlfile))
    with RootParseContext.from_config(config) as ctx:
        parsed = fs.parse(parse_context=ctx)
    assert parsed.to_tuple(code_only=code_only, show_raw=True) == res

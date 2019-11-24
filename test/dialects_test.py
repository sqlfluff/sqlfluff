"""Automated tests for all dialects.

Any files in the /tests/fixtures/parser directoy will be picked up
and automatically tested against the appropriate dialect.
"""

import pytest
import logging
import os

from sqlfluff.parser.segments_base import ParseContext
from sqlfluff.parser.segments_file import FileSegment
from sqlfluff.dialects import dialect_selector


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
            y = root + '.yml'
            if y in dirlist:
                parse_structure_examples.append((d, f, y))


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
def test__dialect__base_file_parse(dialect, file, caplog):
    """For given test examples, check successful parsing."""
    raw = load_file(dialect, file)
    fs = FileSegment.from_raw(raw)
    # From just the initial parse, check we're all there
    assert fs.raw == raw
    # Load the right dialect
    dia = dialect_selector(dialect)
    context = ParseContext(dialect=dia)
    # Do the parse with lots of logging
    with caplog.at_level(logging.DEBUG):
        logging.debug("Pre-parse structure: {0}".format(fs.to_tuple(show_raw=True)))
        logging.debug("Pre-parse structure: {0}".format(fs.stringify()))
        parsed = fs.parse(parse_context=context)  # Optional: set recurse=1 to limit recursion
        logging.debug("Post-parse structure: {0}".format(fs.to_tuple(show_raw=True)))
        logging.debug("Post-parse structure: {0}".format(fs.stringify()))
    # Check we're all there.
    assert parsed.raw == raw
    # Check that there's nothing un parsable
    typs = parsed.type_set()
    assert 'unparsable' not in typs


@pytest.mark.parametrize(
    "dialect,sqlfile,yamlfile",
    parse_structure_examples
)
def test__dialect__base_parse_struct(dialect, sqlfile, yamlfile, caplog, yaml_loader):
    """For given test examples, check parsed structure against yaml."""
    # Load the right dialect
    dia = dialect_selector(dialect)
    context = ParseContext(dialect=dia)
    # Load the SQL
    raw = load_file(dialect, sqlfile)
    fs = FileSegment.from_raw(raw)
    # Load the YAML
    res = yaml_loader(make_dialect_path(dialect, yamlfile))
    with caplog.at_level(logging.DEBUG):
        parsed = fs.parse(parse_context=context)
    assert parsed.to_tuple(code_only=True, show_raw=True) == res

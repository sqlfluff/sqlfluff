"""
Automated tests for all dialects.

Any files in the /tests/fixtures/parser directoy will be picked up
and automatically tested against the appropriate dialect.
"""

import pytest
import logging
import os
import oyaml

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


def load_file(dialect, fname):
    with open(os.path.join('test', 'fixtures', 'parser', dialect, fname)) as f:
        raw = f.read()
    return raw


def process_struct(obj):
    if isinstance(obj, dict):
        return tuple(
            [(k, process_struct(obj[k])) for k in obj]
        )
    elif isinstance(obj, list):
        # We'll assume that it's a list of dicts
        if isinstance(obj[0], dict):
            buff = [process_struct(elem) for elem in obj]
            if any([len(elem) > 1 for elem in buff]):
                raise ValueError("Not sure how to deal with multi key dict: {0!r}".format(buff))
            return tuple(
                [elem[0] for elem in buff]
            )
        else:
            raise TypeError(
                "Did not expect a list of {0}: {1!r}".format(
                    type(obj[0]), obj[0]))
    elif isinstance(obj, str):
        return obj
    elif isinstance(obj, int):
        return str(obj)
    else:
        raise TypeError("Not sure how to deal with type {0}: {1!r}".format(
            type(obj), obj))


def load_struct(dialect, fname):
    raw = load_file(dialect, fname)
    obj = oyaml.safe_load(raw)
    # Unwrap one layer of tuple
    return process_struct(obj)[0]


@pytest.mark.parametrize(
    "dialect,file",
    parse_success_examples
)
def test__dialect__ansi__base_file_parse(dialect, file, caplog):
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
def test__dialect__ansi__base_parse_struct(dialect, sqlfile, yamlfile, caplog):
    """ Some simple statements to check full parsing structure """
    # Load the right dialect
    dia = dialect_selector(dialect)
    context = ParseContext(dialect=dia)
    # Load the SQL
    raw = load_file(dialect, sqlfile)
    fs = FileSegment.from_raw(raw)
    # Load the YAML
    res = load_struct(dialect, yamlfile)
    with caplog.at_level(logging.DEBUG):
        parsed = fs.parse(parse_context=context)
    assert parsed.to_tuple(code_only=True, show_raw=True) == res

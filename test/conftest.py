"""Common Test Fixtures."""

import hashlib
import io
import os
from typing import List, NamedTuple, Tuple

import pytest
import yaml

from sqlfluff.cli.commands import quoted_presenter
from sqlfluff.core import FluffConfig
from sqlfluff.core.linter import Linter
from sqlfluff.core.parser import Lexer, Parser
from sqlfluff.core.parser.markers import PositionMarker
from sqlfluff.core.parser.segments import (
    BaseSegment,
    CodeSegment,
    CommentSegment,
    Dedent,
    Indent,
    NewlineSegment,
    SymbolSegment,
    WhitespaceSegment,
)
from sqlfluff.core.rules import BaseRule
from sqlfluff.core.templaters import TemplatedFile

# When writing YAML files, double quotes string values needing escapes.
yaml.add_representer(str, quoted_presenter)


class ParseExample(NamedTuple):
    """A tuple representing an example SQL file to parse."""

    dialect: str
    sqlfile: str


def get_parse_fixtures(
    fail_on_missing_yml=False,
) -> Tuple[List[ParseExample], List[Tuple[str, str, bool, str]]]:
    """Search for all parsing fixtures."""
    parse_success_examples = []
    parse_structure_examples = []
    # Generate the filenames for each dialect from the parser test directory
    for d in os.listdir(os.path.join("test", "fixtures", "dialects")):
        # Ignore documentation
        if d.endswith(".md"):
            continue
        # assume that d is now the name of a dialect
        dirlist = os.listdir(os.path.join("test", "fixtures", "dialects", d))
        for f in dirlist:
            has_yml = False
            if f.endswith(".sql"):
                root = f[:-4]
                # only look for sql files
                parse_success_examples.append(ParseExample(d, f))
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
                if not has_yml and fail_on_missing_yml:
                    raise (
                        Exception(
                            f"Missing .yml file for {os.path.join(d, f)}. Run the "
                            "test/generate_parse_fixture_yml.py script!"
                        )
                    )
    return parse_success_examples, parse_structure_examples


def make_dialect_path(dialect, fname):
    """Work out how to find paths given a dialect and a file name."""
    return os.path.join("test", "fixtures", "dialects", dialect, fname)


def load_file(dialect, fname):
    """Load a file."""
    with open(make_dialect_path(dialect, fname), encoding="utf8") as f:
        raw = f.read()
    return raw


def process_struct(obj):
    """Process a nested dict or dict-like into a check tuple."""
    if isinstance(obj, dict):
        return tuple((k, process_struct(obj[k])) for k in obj)
    elif isinstance(obj, list):
        # If empty list, return empty tuple
        if not len(obj):
            return tuple()
        # We'll assume that it's a list of dicts
        if isinstance(obj[0], dict):
            buff = [process_struct(elem) for elem in obj]
            if any(len(elem) > 1 for elem in buff):
                raise ValueError(f"Not sure how to deal with multi key dict: {buff!r}")
            return tuple(elem[0] for elem in buff)
        else:
            raise TypeError(f"Did not expect a list of {type(obj[0])}: {obj[0]!r}")
    elif isinstance(obj, (str, int, float)):
        return str(obj)
    elif obj is None:
        return None
    else:
        raise TypeError(f"Not sure how to deal with type {type(obj)}: {obj!r}")


def parse_example_file(dialect: str, sqlfile: str):
    """Parse example SQL file, return parse tree."""
    config = FluffConfig(overrides=dict(dialect=dialect))
    # Load the SQL
    raw = load_file(dialect, sqlfile)
    # Lex and parse the file
    tokens, _ = Lexer(config=config).lex(raw)
    tree = Parser(config=config).parse(tokens, fname=dialect + "/" + sqlfile)
    return tree


def compute_parse_tree_hash(tree):
    """Given a parse tree, compute a consistent hash value for it."""
    if tree:
        r = tree.as_record(code_only=True, show_raw=True)
        if r:
            r_io = io.StringIO()
            yaml.dump(r, r_io, sort_keys=False, allow_unicode=True)
            result = hashlib.blake2s(r_io.getvalue().encode("utf-8")).hexdigest()
            return result
    return None


def load_yaml(fpath):
    """Load a yaml structure and process it into a tuple."""
    # Load raw file
    with open(fpath, encoding="utf8") as f:
        raw = f.read()
    # Parse the yaml
    obj = yaml.safe_load(raw)
    # Return the parsed and structured object
    _hash = None
    if obj:
        _hash = obj.pop("_hash", None)
    processed = process_struct(obj)
    if processed:
        return _hash, process_struct(obj)[0]
    else:
        return None, None


@pytest.fixture()
def yaml_loader():
    """Return a yaml loading function."""
    # Return a function
    return load_yaml


def _generate_test_segments_func(elems):
    """Roughly generate test segments.

    This function isn't totally robust, but good enough
    for testing. Use with caution.
    """
    buff = []
    raw_file = "".join(elems)
    templated_file = TemplatedFile.from_string(raw_file)
    idx = 0

    for elem in elems:
        if elem == "<indent>":
            buff.append(
                Indent(pos_marker=PositionMarker.from_point(idx, idx, templated_file))
            )
            continue
        elif elem == "<dedent>":
            buff.append(
                Dedent(pos_marker=PositionMarker.from_point(idx, idx, templated_file))
            )
            continue

        seg_kwargs = {}

        if set(elem) <= {" ", "\t"}:
            SegClass = WhitespaceSegment
        elif set(elem) <= {"\n"}:
            SegClass = NewlineSegment
        elif elem == "(":
            SegClass = SymbolSegment
            seg_kwargs = {"instance_types": ("start_bracket",)}
        elif elem == ")":
            SegClass = SymbolSegment
            seg_kwargs = {"instance_types": ("end_bracket",)}
        elif elem == "[":
            SegClass = SymbolSegment
            seg_kwargs = {"instance_types": ("start_square_bracket",)}
        elif elem == "]":
            SegClass = SymbolSegment
            seg_kwargs = {"instance_types": ("end_square_bracket",)}
        elif elem.startswith("--"):
            SegClass = CommentSegment
            seg_kwargs = {"instance_types": ("inline_comment",)}
        elif elem.startswith('"'):
            SegClass = CodeSegment
            seg_kwargs = {"instance_types": ("double_quote",)}
        elif elem.startswith("'"):
            SegClass = CodeSegment
            seg_kwargs = {"instance_types": ("single_quote",)}
        else:
            SegClass = CodeSegment

        # Set a none position marker which we'll realign at the end.
        buff.append(
            SegClass(
                raw=elem,
                pos_marker=PositionMarker(
                    slice(idx, idx + len(elem)),
                    slice(idx, idx + len(elem)),
                    templated_file,
                ),
                **seg_kwargs,
            )
        )
        idx += len(elem)

    return tuple(buff)


@pytest.fixture(scope="module")
def generate_test_segments():
    """Roughly generate test segments.

    This is a factory function so that it works as a fixture,
    but when actually used, this will return the inner function
    which is what you actually need.
    """
    return _generate_test_segments_func


@pytest.fixture
def raise_critical_errors_after_fix(monkeypatch):
    """Raises errors that break the Fix process.

    These errors are otherwise swallowed to allow the lint messages to reach
    the end user.
    """

    @staticmethod
    def _log_critical_errors(error: Exception):
        raise error

    monkeypatch.setattr(BaseRule, "_log_critical_errors", _log_critical_errors)


@pytest.fixture(autouse=True)
def fail_on_parse_error_after_fix(monkeypatch):
    """Cause tests to fail if a lint fix introduces a parse error.

    In production, we have a couple of functions that, upon detecting a bug in
    a lint rule, just log a warning. To catch bugs in new or modified rules, we
    want to be more strict during dev and CI/CD testing. Here, we patch in
    different functions which raise runtime errors, causing tests to fail if
    this happens.
    """

    @staticmethod
    def raise_error_apply_fixes_check_issue(message, *args):  # pragma: no cover
        raise ValueError(message % args)

    @staticmethod
    def raise_error_conflicting_fixes_same_anchor(message: str):  # pragma: no cover
        raise ValueError(message)

    monkeypatch.setattr(
        BaseSegment, "_log_apply_fixes_check_issue", raise_error_apply_fixes_check_issue
    )

    monkeypatch.setattr(
        Linter,
        "_report_conflicting_fixes_same_anchor",
        raise_error_conflicting_fixes_same_anchor,
    )


@pytest.fixture(autouse=True)
def test_verbosity_level(request):
    """Report the verbosity level for a given pytest run.

    For example:

    $ pytest -vv
    Has a verbosity level of 2

    While:

    $ pytest
    Has a verbosity level of 0
    """
    return request.config.getoption("verbose")

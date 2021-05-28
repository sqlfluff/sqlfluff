"""Common Test Fixtures."""

import pytest
import oyaml

from sqlfluff.core.parser.markers import PositionMarker
from sqlfluff.core.parser.segments import (
    Indent,
    Dedent,
    WhitespaceSegment,
    NewlineSegment,
    SymbolSegment,
    CommentSegment,
    CodeSegment,
)
from sqlfluff.core.templaters import TemplatedFile


def process_struct(obj):
    """Process a nested dict or dict-like into a check tuple."""
    if isinstance(obj, dict):
        return tuple((k, process_struct(obj[k])) for k in obj)
    elif isinstance(obj, list):
        # We'll assume that it's a list of dicts
        if isinstance(obj[0], dict):
            buff = [process_struct(elem) for elem in obj]
            if any(len(elem) > 1 for elem in buff):
                raise ValueError(
                    "Not sure how to deal with multi key dict: {0!r}".format(buff)
                )
            return tuple(elem[0] for elem in buff)
        else:
            raise TypeError(
                "Did not expect a list of {0}: {1!r}".format(type(obj[0]), obj[0])
            )
    elif isinstance(obj, (str, int, float)):
        return str(obj)
    elif obj is None:
        return None
    else:
        raise TypeError(
            "Not sure how to deal with type {0}: {1!r}".format(type(obj), obj)
        )


def load_yaml(fpath):
    """Load a yaml structure and process it into a tuple."""
    # Load raw file
    with open(fpath) as f:
        raw = f.read()
    # Parse the yaml
    obj = oyaml.safe_load(raw)
    # Return the parsed and structured object
    processed = process_struct(obj)
    if processed:
        return process_struct(obj)[0]
    else:
        return None


@pytest.fixture()
def yaml_loader():
    """Return a yaml loading function."""
    # Return a function
    return load_yaml


@pytest.fixture(scope="module")
def generate_test_segments():
    """Roughly generate test segments.

    This is a factory function so that it works as a fixture,
    but when actually used, this will return the inner function
    which is what you actually need.
    """

    def generate_test_segments_func(elems):
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
                    Indent(
                        pos_marker=PositionMarker.from_point(idx, idx, templated_file)
                    )
                )
                continue
            elif elem == "<dedent>":
                buff.append(
                    Dedent(
                        pos_marker=PositionMarker.from_point(idx, idx, templated_file)
                    )
                )
                continue

            seg_kwargs = {}

            if set(elem) <= {" ", "\t"}:
                SegClass = WhitespaceSegment
            elif set(elem) <= {"\n"}:
                SegClass = NewlineSegment
            elif elem == "(":
                SegClass = SymbolSegment
                seg_kwargs = {"name": "bracket_open"}
            elif elem == ")":
                SegClass = SymbolSegment
                seg_kwargs = {"name": "bracket_close"}
            elif elem.startswith("--"):
                SegClass = CommentSegment
                seg_kwargs = {"name": "inline_comment"}
            elif elem.startswith('"'):
                SegClass = CodeSegment
                seg_kwargs = {"name": "double_quote"}
            elif elem.startswith("'"):
                SegClass = CodeSegment
                seg_kwargs = {"name": "single_quote"}
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
                    **seg_kwargs
                )
            )
            idx += len(elem)

        return tuple(buff)

    # Return the function
    return generate_test_segments_func

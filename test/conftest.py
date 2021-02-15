"""Common Test Fixtures."""

import pytest
import oyaml

from sqlfluff.core.parser.markers import FilePositionMarker
from sqlfluff.core.parser.segments import RawSegment


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
    if process_struct(obj):
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
        raw_buff = ""
        for elem in elems:
            if set(elem) <= {" ", "\t"}:
                cls = RawSegment.make(" ", name="whitespace", type="whitespace")
            elif set(elem) <= {"\n"}:
                cls = RawSegment.make("\n", name="newline", type="newline")
            elif elem == "(":
                cls = RawSegment.make("(", name="bracket_open", _is_code=True)
            elif elem == ")":
                cls = RawSegment.make(")", name="bracket_close", _is_code=True)
            elif elem.startswith("--"):
                cls = RawSegment.make("--", name="inline_comment")
            elif elem.startswith('"'):
                cls = RawSegment.make('"', name="double_quote", _is_code=True)
            elif elem.startswith("'"):
                cls = RawSegment.make("'", name="single_quote", _is_code=True)
            else:
                cls = RawSegment.make("", _is_code=True)

            buff.append(cls(elem, FilePositionMarker().advance_by(raw_buff)))
            raw_buff += elem
        return tuple(buff)  # Make sure we return a tuple

    # Return the function
    return generate_test_segments_func

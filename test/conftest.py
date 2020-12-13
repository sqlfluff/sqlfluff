"""Common Test Fixtures."""

import pytest
import oyaml
import sys
import os

# append the helpers to the test path
# to support having a "testing" library
sys.path.append(os.path.join(os.path.dirname(__file__), "helpers"))


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
        raise TypeError(
            "Found a null value in dict. This is probably a misconfiguration."
        )
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
    return process_struct(obj)[0]


@pytest.fixture()
def yaml_loader():
    """Return a yaml loading function."""
    # Return a function
    return load_yaml

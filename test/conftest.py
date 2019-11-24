"""Common Test Fixtures."""

import pytest
import oyaml
import six


def process_struct(obj):
    """Process a nested dict or dict-like into a check tuple."""
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
    elif isinstance(obj, six.string_types) or isinstance(obj, six.integer_types) or isinstance(obj, float):
        return six.u(str(obj))
    else:
        raise TypeError("Not sure how to deal with type {0}: {1!r}".format(
            type(obj), obj))


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

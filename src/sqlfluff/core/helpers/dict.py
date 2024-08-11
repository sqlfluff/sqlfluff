"""Dict helpers, mostly used in config routines."""

from typing import Any, Dict, List, Optional


def nested_combine(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Combine an iterable of dictionaries.

    Each dictionary is combined into a result dictionary. For
    each key in the first dictionary, it will be overwritten
    by any same-named key in any later dictionaries in the
    iterable. If the element at that key is a dictionary, rather
    than just overwriting we use the same function to combine
    those dictionaries.

    Args:
        *dicts: An iterable of dictionaries to be combined.

    Returns:
        `dict`: A combined dictionary from the input dictionaries.

    A simple example:
    >>> nested_combine({"a": {"b": "c"}}, {"a": {"d": "e"}})
    {'a': {'b': 'c', 'd': 'e'}}

    Keys overwrite left to right:
    >>> nested_combine({"a": {"b": "c"}}, {"a": {"b": "e"}})
    {'a': {'b': 'e'}}
    """
    r: Dict[str, Any] = {}
    for d in dicts:
        for k in d:
            if k in r and isinstance(r[k], dict):
                if isinstance(d[k], dict):
                    r[k] = nested_combine(r[k], d[k])
                else:  # pragma: no cover
                    raise ValueError(
                        "Key {!r} is a dict in one config but not another! PANIC: "
                        "{!r}".format(k, d[k])
                    )
            else:
                r[k] = d[k]
    return r


def dict_diff(
    left: Dict[str, Any], right: Dict[str, Any], ignore: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Work out the difference between two dictionaries.

    Returns a dictionary which represents elements in the `left`
    dictionary which aren't in the `right` or are different to
    those in the `right`. If the element is a dictionary, we
    recursively look for differences in those dictionaries,
    likewise only returning the differing elements.

    NOTE: If an element is in the `right` but not in the `left`
    at all (i.e. an element has been *removed*) then it will
    not show up in the comparison.

    Args:
        left (:obj:`dict`): The object containing the *new* elements
            which will be compared against the other.
        right (:obj:`dict`): The object to compare against.
        ignore (:obj:`list` of `str`, optional): Keys to ignore.

    Returns:
        `dict`: A dictionary representing the difference.

    Basic functionality shown, especially returning the left as:
    >>> dict_diff({"a": "b", "c": "d"}, {"a": "b", "c": "e"})
    {'c': 'd'}

    Ignoring works on a key basis:
    >>> dict_diff({"a": "b"}, {"a": "c"})
    {'a': 'b'}
    >>> dict_diff({"a": "b"}, {"a": "c"}, ["a"])
    {}
    """
    buff: Dict[str, Any] = {}
    for k in left:
        if ignore and k in ignore:
            continue
        # Is the key there at all?
        if k not in right:
            buff[k] = left[k]
        # Is the content the same?
        elif left[k] == right[k]:
            continue
        # If it's not the same but both are dicts, then compare
        elif isinstance(left[k], dict) and isinstance(right[k], dict):
            diff = dict_diff(left[k], right[k], ignore=ignore)
            # Only include the difference if non-null.
            if diff:
                buff[k] = diff
        # It's just different
        else:
            buff[k] = left[k]
    return buff

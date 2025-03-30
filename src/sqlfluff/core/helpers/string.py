"""String Helpers for the parser module."""

from collections.abc import Iterator
from typing import Union


def curtail_string(s: str, length: int = 20) -> str:
    """Trim a string nicely to length."""
    if len(s) > length:
        return s[:length] + "..."
    else:
        return s


def findall(substr: str, in_str: str) -> Iterator[int]:
    """Yields all the positions sbstr within in_str.

    https://stackoverflow.com/questions/4664850/how-to-find-all-occurrences-of-a-substring
    """
    # Return nothing if one of the inputs is trivial
    if not substr or not in_str:
        return
    idx = in_str.find(substr)
    while idx != -1:
        yield idx
        idx = in_str.find(substr, idx + 1)


def split_colon_separated_string(in_str: str) -> tuple[tuple[str, ...], str]:
    r"""Converts a colon separated string.

    The final value in the string is handled separately the other others.
    >>> split_colon_separated_string("a:b")
    (('a',), 'b')
    >>> split_colon_separated_string("a:b:c")
    (('a', 'b'), 'c')
    >>> split_colon_separated_string("a:b:c:d")
    (('a', 'b', 'c'), 'd')
    >>> split_colon_separated_string("a")
    ((), 'a')

    NOTE: This also includes some heuristics for legit values containing colon.
    >>> split_colon_separated_string("foo:bar:C:\\Users")
    (('foo', 'bar'), 'C:\\Users')
    >>> split_colon_separated_string('foo:bar:{"k":"v"}')
    (('foo', 'bar'), '{"k":"v"}')
    >>> split_colon_separated_string('foo:bar:[{"k":"v"}]')
    (('foo', 'bar'), '[{"k":"v"}]')
    """
    config_path: list[str] = []
    leftover = in_str
    while ":" in leftover:
        element, _, value = leftover.partition(":")
        element = element.strip()
        value = value.strip()
        config_path.append(element)
        leftover = value
        if not should_split_on_colon(value):
            break

    # last part - actual value
    config_path.append(leftover)
    return tuple(config_path[:-1]), config_path[-1]


def should_split_on_colon(value: str) -> bool:
    """Heuristic for legit values containing comma."""
    if len(value) >= 2 and value[1] == ":" and value[2] == "\\":
        # Likely a Windows path
        return False
    if len(value) >= 2 and (value[0] == "[" and value[-1] == "]"):
        # Likely a JSON array
        return False
    if len(value) >= 2 and (value[0] == "{" and value[-1] == "}"):
        # Likely a JSON object
        return False

    return True


def split_comma_separated_string(raw: Union[str, list[str]]) -> list[str]:
    """Converts comma separated string to List, stripping whitespace."""
    if isinstance(raw, str):
        return [s.strip() for s in raw.split(",") if s.strip()]
    assert isinstance(raw, list)
    return raw


def get_trailing_whitespace_from_string(in_str: str) -> str:
    r"""Returns the trailing whitespace from a string.

    Designed to work with source strings of placeholders.

    >>> get_trailing_whitespace_from_string("")
    ''
    >>> get_trailing_whitespace_from_string("foo")
    ''
    >>> get_trailing_whitespace_from_string("   ")
    '   '
    >>> get_trailing_whitespace_from_string("  foo ")
    ' '
    >>> get_trailing_whitespace_from_string("foo\n")
    '\n'
    >>> get_trailing_whitespace_from_string("bar  \t  \n  \r ")
    '  \t  \n  \r '
    """
    whitespace_chars = " \t\r\n"
    if not in_str or in_str[-1] not in whitespace_chars:
        return ""  # No whitespace
    for i in range(1, len(in_str)):
        if in_str[-(i + 1)] not in whitespace_chars:
            # NOTE: The partial whitespace case is included as
            # future-proofing. In testing it appears it is never
            # required, and so only covered in the doctests above.
            # doctest coverage isn't included in the overall coverage
            # check and so the line below is excluded.
            return in_str[-i:]  # pragma: no cover
    else:
        return in_str  # All whitespace

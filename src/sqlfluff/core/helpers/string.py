"""String Helpers for the parser module."""

from typing import Iterator, List, Tuple, Union


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


def split_colon_separated_string(in_str: str) -> Tuple[Tuple[str, ...], str]:
    """Converts a colon separated string.

    NOTE: This also includes some provisions for values which may be
    Windows paths containing colons and NOT stripping those.
    """
    config_path: List[str] = []
    for element in in_str.split(":"):
        # If the next element begins with a backslash, and the previous
        # one had length == 1,  then this is probably a windows path.
        # In which case, rejoin them together.
        element = element.strip()
        if (
            element
            and element[0] == "\\"
            and config_path[-1]
            and len(config_path[-1]) == 1
        ):
            config_path[-1] = config_path[-1] + ":" + element
        else:
            # Otherwise just add it to the path.
            config_path.append(element)

    return tuple(config_path[:-1]), config_path[-1]


def split_comma_separated_string(raw: Union[str, List[str]]) -> List[str]:
    """Converts comma separated string to List, stripping whitespace."""
    if isinstance(raw, str):
        return [s.strip() for s in raw.split(",") if s.strip()]
    assert isinstance(raw, list)
    return raw

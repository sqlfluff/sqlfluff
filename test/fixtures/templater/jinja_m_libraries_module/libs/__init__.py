"""Module used to test __init__.py within the jinja template."""


def root_equals(col: str, val: str) -> str:
    """Return a string that has col = val."""
    return f"{col} = {val}"

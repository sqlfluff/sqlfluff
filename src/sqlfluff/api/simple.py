"""The simple public API methods."""

from ..core import Linter, FluffConfig


def lint(sql, dialect="ansi", fname="passed string"):
    """Lint a sql string or file.

    Args:
        sql (:obj:`str` or file-like object): The sql to be linted
            either as a string or a subclass of :obj:`TextIOBase`.
        dialect (:obj:`str`, optional): A reference to the dialect of the sql
            to be linted. Defaults to `ansi`.
        fname (:obj:`str`, optional): The name of the file to be assigned in
            the results object.
    """
    # Make sure that whatever we're passed is an appropriate object.
    if not isinstance(sql, str):
        try:
            sql = sql.read()
        except AttributeError:
            raise TypeError("Value passed as sql is not a string or a readable object.")

    # TODO: This pattern seems to repeat a lot, maybe we should have a sensible default?
    config = FluffConfig(overrides=dict(dialect=dialect))
    linter = Linter(config=config)

    # Use the linter
    result = linter.lint_string_wrapped(sql, fname=fname)
    result_records = result.as_records()
    # Return just the violations for this file
    return result_records[0]["violations"]

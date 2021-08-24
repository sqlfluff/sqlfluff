"""The simple public API methods."""

from sqlfluff.core import Linter


class APIParsingError(ValueError):
    """An exception which holds a set of violations."""

    def __init__(self, violations, **kwargs):
        self.violations = violations
        self.msg = f"Found {len(violations)} issues while parsing string."
        for viol in violations:
            self.msg += f"\n{viol!s}"
        super().__init__(self.msg, **kwargs)


def _unify_str_or_file(sql):
    """Unify string and files in the same format."""
    if not isinstance(sql, str):
        try:
            sql = sql.read()
        except AttributeError:  # pragma: no cover
            raise TypeError("Value passed as sql is not a string or a readable object.")
    return sql


def lint(sql, dialect="ansi", rules=None):
    """Lint a sql string or file.

    Args:
        sql (:obj:`str` or file-like object): The sql to be linted
            either as a string or a subclass of :obj:`TextIOBase`.
        dialect (:obj:`str`, optional): A reference to the dialect of the sql
            to be linted. Defaults to `ansi`.
        rules (:obj:`str` or iterable of :obj:`str`, optional): A subset of rule
            reference to lint for.

    Returns:
        :obj:`list` of :obj:`dict` for each violation found.
    """
    sql = _unify_str_or_file(sql)
    linter = Linter(dialect=dialect, rules=rules)

    result = linter.lint_string_wrapped(sql)
    result_records = result.as_records()
    # Return just the violations for this file
    return [] if not result_records else result_records[0]["violations"]


def fix(sql, dialect="ansi", rules=None):
    """Fix a sql string or file.

    Args:
        sql (:obj:`str` or file-like object): The sql to be linted
            either as a string or a subclass of :obj:`TextIOBase`.
        dialect (:obj:`str`, optional): A reference to the dialect of the sql
            to be linted. Defaults to `ansi`.
        rules (:obj:`str` or iterable of :obj:`str`, optional): A subset of rule
            reference to lint for.

    Returns:
        :obj:`str` for the fixed sql if possible.
    """
    sql = _unify_str_or_file(sql)
    linter = Linter(dialect=dialect, rules=rules)

    result = linter.lint_string_wrapped(sql, fix=True)
    fixed_string = result.paths[0].files[0].fix_string()[0]
    return fixed_string


def parse(sql, dialect="ansi"):
    """Parse a sql string or file.

    Args:
        sql (:obj:`str` or file-like object): The sql to be linted
            either as a string or a subclass of :obj:`TextIOBase`.
        dialect (:obj:`str`, optional): A reference to the dialect of the sql
            to be linted. Defaults to `ansi`.

    Returns:
        :obj:`ParsedString` containing the parsed structure.
    """
    sql = _unify_str_or_file(sql)
    linter = Linter(dialect=dialect)
    parsed = linter.parse_string(sql)
    # If we encounter any parsing errors, raise them in a combined issue.
    if parsed.violations:
        raise APIParsingError(parsed.violations)
    return parsed

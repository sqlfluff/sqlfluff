"""The simple public API methods."""

from typing import Any, Dict, List, Optional
from sqlfluff.core import Linter
from sqlfluff.core import SQLBaseError
from sqlfluff.core.linter import ParsedString


class APIParsingError(ValueError):
    """An exception which holds a set of violations."""

    def __init__(self, violations: List[SQLBaseError], *args: Any):
        self.violations = violations
        self.msg = f"Found {len(violations)} issues while parsing string."
        for viol in violations:
            self.msg += f"\n{viol!s}"
        super().__init__(self.msg, *args)


def lint(
    sql: str,
    dialect: str = "ansi",
    rules: Optional[List[str]] = None,
    exclude_rules: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Lint a sql string or file.

    Args:
        sql (:obj:`str`): The sql to be linted
            either as a string or a subclass of :obj:`TextIOBase`.
        dialect (:obj:`str`, optional): A reference to the dialect of the sql
            to be linted. Defaults to `ansi`.
        rules (:obj:list of :obj:`str`, optional): A subset of rule
            references to lint for.
        exclude_rules (:obj:list of :obj:`str`, optional): A subset of rule
            references to avoid linting for.

    Returns:
        :obj:`list` of :obj:`dict` for each violation found.
    """
    linter = Linter(dialect=dialect, rules=rules, exclude_rules=exclude_rules)

    result = linter.lint_string_wrapped(sql)
    result_records = result.as_records()
    # Return just the violations for this file
    return [] if not result_records else result_records[0]["violations"]


def fix(
    sql: str,
    dialect: str = "ansi",
    rules: Optional[List[str]] = None,
    exclude_rules: Optional[List[str]] = None,
) -> str:
    """Fix a sql string or file.

    Args:
        sql (:obj:`str`): The sql to be linted
            either as a string or a subclass of :obj:`TextIOBase`.
        dialect (:obj:`str`, optional): A reference to the dialect of the sql
            to be linted. Defaults to `ansi`.
        rules (:obj:list of :obj:`str`, optional): A subset of rule
            references to lint for.
        exclude_rules (:obj:list of :obj:`str`, optional): A subset of rule
            references to avoid linting for.

    Returns:
        :obj:`str` for the fixed sql if possible.
    """
    linter = Linter(dialect=dialect, rules=rules, exclude_rules=exclude_rules)

    result = linter.lint_string_wrapped(sql, fix=True)
    fixed_string = result.paths[0].files[0].fix_string()[0]
    return fixed_string


def parse(sql: str, dialect: str = "ansi") -> ParsedString:
    """Parse a sql string or file.

    Args:
        sql (:obj:`str`): The sql to be linted
            either as a string or a subclass of :obj:`TextIOBase`.
        dialect (:obj:`str`, optional): A reference to the dialect of the sql
            to be linted. Defaults to `ansi`.

    Returns:
        :obj:`ParsedString` containing the parsed structure.
    """
    linter = Linter(dialect=dialect)
    parsed = linter.parse_string(sql)
    # If we encounter any parsing errors, raise them in a combined issue.
    if parsed.violations:
        raise APIParsingError(parsed.violations)
    return parsed

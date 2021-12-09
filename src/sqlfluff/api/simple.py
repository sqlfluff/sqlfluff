"""The simple public API methods."""

from typing import Any, Dict, List, Optional
from sqlfluff.core import (
    dialect_selector,
    FluffConfig,
    Linter,
    SQLBaseError,
    SQLFluffUserError,
)
from sqlfluff.core.linter import ParsedString


def get_simple_config(
    dialect: str = "ansi",
    rules: Optional[List[str]] = None,
    exclude_rules: Optional[List[str]] = None,
    extra_config_path: Optional[str] = None,
    ignore_local_config: bool = False,
) -> FluffConfig:
    """Get a config object from simple API arguments."""
    # Check the requested dialect exists and is valid.
    try:
        dialect_selector(dialect)
    except SQLFluffUserError as err:
        raise SQLFluffUserError(f"Error loading dialect '{dialect}': {str(err)}")
    except KeyError:
        raise SQLFluffUserError(f"Error: Unknown dialect '{dialect}'")

    # Create overrides for simple API arguments.
    overrides = {
        "dialect": dialect,
        "rules": ",".join(rules) if rules is not None else None,
        "exclude_rules": ",".join(exclude_rules) if exclude_rules is not None else None,
    }

    # Instantiate a config object.
    try:
        return FluffConfig.from_root(
            extra_config_path=extra_config_path,
            ignore_local_config=ignore_local_config,
            overrides=overrides,
        )
    except SQLFluffUserError as err:  # pragma: no cover
        raise SQLFluffUserError(f"Error loading config: {str(err)}")


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
    extra_config_path: Optional[str] = None,
    ignore_local_config: bool = False,
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
    cfg = get_simple_config(
        dialect=dialect,
        rules=rules,
        exclude_rules=exclude_rules,
        extra_config_path=extra_config_path,
        ignore_local_config=ignore_local_config,
    )
    linter = Linter(config=cfg)

    result = linter.lint_string_wrapped(sql)
    result_records = result.as_records()
    # Return just the violations for this file
    return [] if not result_records else result_records[0]["violations"]


def fix(
    sql: str,
    dialect: str = "ansi",
    rules: Optional[List[str]] = None,
    exclude_rules: Optional[List[str]] = None,
    extra_config_path: Optional[str] = None,
    ignore_local_config: bool = False,
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
    cfg = get_simple_config(
        dialect=dialect,
        rules=rules,
        exclude_rules=exclude_rules,
        extra_config_path=extra_config_path,
        ignore_local_config=ignore_local_config,
    )
    linter = Linter(config=cfg)

    result = linter.lint_string_wrapped(sql, fix=True)
    fixed_string = result.paths[0].files[0].fix_string()[0]
    return fixed_string


def parse(
    sql: str,
    dialect: str = "ansi",
    extra_config_path: Optional[str] = None,
    ignore_local_config: bool = False,
) -> ParsedString:
    """Parse a sql string or file.

    Args:
        sql (:obj:`str`): The sql to be linted
            either as a string or a subclass of :obj:`TextIOBase`.
        dialect (:obj:`str`, optional): A reference to the dialect of the sql
            to be linted. Defaults to `ansi`.

    Returns:
        :obj:`ParsedString` containing the parsed structure.
    """
    cfg = get_simple_config(
        dialect=dialect,
        extra_config_path=extra_config_path,
        ignore_local_config=ignore_local_config,
    )
    linter = Linter(config=cfg)

    parsed = linter.parse_string(sql)
    # If we encounter any parsing errors, raise them in a combined issue.
    if parsed.violations:
        raise APIParsingError(parsed.violations)
    return parsed

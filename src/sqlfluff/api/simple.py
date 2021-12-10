"""The simple public API methods."""

from typing import Any, Dict, List, Optional
from sqlfluff.core import (
    dialect_selector,
    FluffConfig,
    Linter,
    SQLBaseError,
    SQLFluffUserError,
)


def get_simple_config(
    dialect: str = "ansi",
    rules: Optional[List[str]] = None,
    exclude_rules: Optional[List[str]] = None,
    config_path: Optional[str] = None,
) -> FluffConfig:
    """Get a config object from simple API arguments."""
    # Check the requested dialect exists and is valid.
    try:
        dialect_selector(dialect)
    except SQLFluffUserError as err:  # pragma: no cover
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
            extra_config_path=config_path,
            ignore_local_config=True,
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
    config_path: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Lint a SQL string.

    Args:
        sql (:obj:`str`): The SQL to be linted.
        dialect (:obj:`str`, optional): A reference to the dialect of the SQL
            to be linted. Defaults to `ansi`.
        rules (:obj:`Optional[List[str]`, optional): A list of rule
            references to lint for. Defaults to None.
        exclude_rules (:obj:`Optional[List[str]`, optional): A list of rule
            references to avoid linting for. Defaults to None.
        config_path (:obj:`Optional[str]`, optional): A path to a .sqlfluff config.
            Defaults to None.

    Returns:
        :obj:`List[Dict[str, Any]]` for each violation found.
    """
    cfg = get_simple_config(
        dialect=dialect,
        rules=rules,
        exclude_rules=exclude_rules,
        config_path=config_path,
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
    config_path: Optional[str] = None,
) -> str:
    """Fix a SQL string.

    Args:
        sql (:obj:`str`): The SQL to be fixed.
        dialect (:obj:`str`, optional): A reference to the dialect of the SQL
            to be fixed. Defaults to `ansi`.
        rules (:obj:`Optional[List[str]`, optional): A subset of rule
            references to fix for. Defaults to None.
        exclude_rules (:obj:`Optional[List[str]`, optional): A subset of rule
            references to avoid fixing for. Defaults to None.
        config_path (:obj:`Optional[str]`, optional): A path to a .sqlfluff config.
            Defaults to None.

    Returns:
        :obj:`str` for the fixed SQL if possible.
    """
    cfg = get_simple_config(
        dialect=dialect,
        rules=rules,
        exclude_rules=exclude_rules,
        config_path=config_path,
    )
    linter = Linter(config=cfg)

    result = linter.lint_string_wrapped(sql, fix=True)
    fixed_string = result.paths[0].files[0].fix_string()[0]
    return fixed_string


def parse(
    sql: str,
    dialect: str = "ansi",
    config_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Parse a SQL string.

    Args:
        sql (:obj:`str`): The SQL to be parsed.
        dialect (:obj:`str`, optional): A reference to the dialect of the SQL
            to be parsed. Defaults to `ansi`.
        config_path (:obj:`Optional[str]`, optional): A path to a .sqlfluff config.
            Defaults to None.

    Returns:
        :obj:`Dict[str, Any]` JSON containing the parsed structure.
    """
    cfg = get_simple_config(
        dialect=dialect,
        config_path=config_path,
    )
    linter = Linter(config=cfg)

    parsed = linter.parse_string(sql)
    # If we encounter any parsing errors, raise them in a combined issue.
    if parsed.violations:
        raise APIParsingError(parsed.violations)
    # Return a JSON representation of the parse tree.
    if parsed.tree is None:  # pragma: no cover
        return {}
    return parsed.tree.as_record(show_raw=True)

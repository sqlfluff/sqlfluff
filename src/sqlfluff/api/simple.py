"""The simple public API methods."""

from typing import Any, Optional

from sqlfluff.core import (
    FluffConfig,
    Linter,
    SQLBaseError,
    SQLFluffUserError,
    dialect_selector,
)
from sqlfluff.core.types import ConfigMappingType


def get_simple_config(
    dialect: Optional[str] = None,
    rules: Optional[list[str]] = None,
    exclude_rules: Optional[list[str]] = None,
    config_path: Optional[str] = None,
) -> FluffConfig:
    """Get a config object from simple API arguments."""
    # Create overrides for simple API arguments.
    overrides: ConfigMappingType = {}
    if dialect is not None:
        # Check the requested dialect exists and is valid.
        try:
            dialect_selector(dialect)
        except SQLFluffUserError as err:  # pragma: no cover
            raise SQLFluffUserError(f"Error loading dialect '{dialect}': {str(err)}")
        except KeyError:
            raise SQLFluffUserError(f"Error: Unknown dialect '{dialect}'")

        overrides["dialect"] = dialect
    if rules is not None:
        overrides["rules"] = ",".join(rules)
    if exclude_rules is not None:
        overrides["exclude_rules"] = ",".join(exclude_rules)

    # Instantiate a config object.
    try:
        config = FluffConfig.from_root(
            extra_config_path=config_path,
            ignore_local_config=True,
            overrides=overrides,
            require_dialect=False,
        )

        # If no dialect was specified, set it to ansi. This allows for the legacy
        # behavior of the simple API to be maintained, where the dialect is not
        # required to be specified, but defaults to ansi.
        if not config.get("dialect"):
            overrides["dialect"] = "ansi"
            config = FluffConfig.from_root(
                extra_config_path=config_path,
                ignore_local_config=True,
                overrides=overrides,
            )
        return config
    except SQLFluffUserError as err:  # pragma: no cover
        raise SQLFluffUserError(f"Error loading config: {str(err)}")


class APIParsingError(ValueError):
    """An exception which holds a set of violations."""

    def __init__(self, violations: list[SQLBaseError], *args: Any):
        self.violations = violations
        msg = f"Found {len(violations)} issues while parsing string."
        for viol in violations:
            msg += f"\n{viol!s}"
        super().__init__(msg, *args)


def lint(
    sql: str,
    dialect: Optional[str] = None,
    rules: Optional[list[str]] = None,
    exclude_rules: Optional[list[str]] = None,
    config: Optional[FluffConfig] = None,
    config_path: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Lint a SQL string.

    Args:
        sql (:obj:`str`): The SQL to be linted.
        dialect (:obj:`Optional[str]`, optional): A reference to the dialect of the SQL
            to be linted. Defaults to `ansi`.
        rules (:obj:`Optional[list[str]`, optional): A list of rule
            references to lint for. Defaults to None.
        exclude_rules (:obj:`Optional[list[str]`, optional): A list of rule
            references to avoid linting for. Defaults to None.
        config (:obj:`Optional[FluffConfig]`, optional): A configuration object
            to use for the operation. Defaults to None.
        config_path (:obj:`Optional[str]`, optional): A path to a .sqlfluff config,
            which is only used if a `config` is not already provided.
            Defaults to None.

    Returns:
        :obj:`list[dict[str, Any]]` for each violation found.
    """
    cfg = config or get_simple_config(
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
    dialect: Optional[str] = None,
    rules: Optional[list[str]] = None,
    exclude_rules: Optional[list[str]] = None,
    config: Optional[FluffConfig] = None,
    config_path: Optional[str] = None,
    fix_even_unparsable: Optional[bool] = None,
) -> str:
    """Fix a SQL string.

    Args:
        sql (:obj:`str`): The SQL to be fixed.
        dialect (:obj:`Optional[str]`, optional): A reference to the dialect of the SQL
            to be fixed. Defaults to `ansi`.
        rules (:obj:`Optional[list[str]`, optional): A subset of rule
            references to fix for. Defaults to None.
        exclude_rules (:obj:`Optional[list[str]`, optional): A subset of rule
            references to avoid fixing for. Defaults to None.
        config (:obj:`Optional[FluffConfig]`, optional): A configuration object
            to use for the operation. Defaults to None.
        config_path (:obj:`Optional[str]`, optional): A path to a .sqlfluff config,
            which is only used if a `config` is not already provided.
            Defaults to None.
        fix_even_unparsable (:obj:`bool`, optional): Optional override for the
            corresponding SQLFluff configuration value.

    Returns:
        :obj:`str` for the fixed SQL if possible.
    """
    cfg = config or get_simple_config(
        dialect=dialect,
        rules=rules,
        exclude_rules=exclude_rules,
        config_path=config_path,
    )
    linter = Linter(config=cfg)

    result = linter.lint_string_wrapped(sql, fix=True)
    if fix_even_unparsable is None:
        fix_even_unparsable = cfg.get("fix_even_unparsable")
    should_fix = True
    if not fix_even_unparsable:
        # If fix_even_unparsable wasn't set, check for templating or parse
        # errors and suppress fixing if there were any.
        _, num_filtered_errors = result.count_tmp_prs_errors()
        if num_filtered_errors > 0:
            should_fix = False
    if should_fix:
        sql = result.paths[0].files[0].fix_string()[0]
    return sql


def parse(
    sql: str,
    dialect: Optional[str] = None,
    config: Optional[FluffConfig] = None,
    config_path: Optional[str] = None,
) -> dict[str, Any]:
    """Parse a SQL string.

    Args:
        sql (:obj:`str`): The SQL to be parsed.
        dialect (:obj:`Optional[str]`, optional): A reference to the dialect of the SQL
            to be parsed. Defaults to `ansi`.
        config (:obj:`Optional[FluffConfig]`, optional): A configuration object
            to use for the operation. Defaults to None.
        config_path (:obj:`Optional[str]`, optional): A path to a .sqlfluff config,
            which is only used if a `config` is not already provided.
            Defaults to None.

    Returns:
        :obj:`Dict[str, Any]` JSON containing the parsed structure.

    Note:
        In the case of multiple potential variants from the raw source file
        only the first variant is returned by the simple API. For access to
        the other variants, use the underlying main API directly.
    """
    cfg = config or get_simple_config(
        dialect=dialect,
        config_path=config_path,
    )
    linter = Linter(config=cfg)

    parsed = linter.parse_string(sql)
    # If we encounter any parsing errors, raise them in a combined issue.
    violations = parsed.violations
    if violations:
        raise APIParsingError(violations)
    # Return a JSON representation of the parse tree.
    # NOTE: For the simple API - only a single variant is returned.
    root_variant = parsed.root_variant()
    assert root_variant, "Files parsed without violations must have a valid variant"
    assert root_variant.tree, "Files parsed without violations must have a valid tree"
    record = root_variant.tree.as_record(show_raw=True)
    assert record
    return record

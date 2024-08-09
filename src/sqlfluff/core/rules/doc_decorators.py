"""A collection of decorators to modify rule docstrings for Sphinx.

NOTE: All of these decorators are deprecated from SQLFluff 2.0.0 onwards.

They are still included to allow a transition period, but the functionality
is now packaged in the BaseRule class via the RuleMetaclass.
"""

from typing import TYPE_CHECKING, Any, Type

from sqlfluff.core.rules.base import rules_logger  # noqa

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.rules.base import BaseRule


def document_fix_compatible(cls: Type["BaseRule"]) -> Type["BaseRule"]:
    """Mark the rule as fixable in the documentation."""
    rules_logger.warning(
        f"{cls.__name__} uses the @document_fix_compatible decorator "
        "which is deprecated in SQLFluff 2.0.0. Remove the decorator "
        "to resolve this warning."
    )
    return cls


def document_groups(cls: Type["BaseRule"]) -> Type["BaseRule"]:
    """Mark the rule as fixable in the documentation."""
    rules_logger.warning(
        f"{cls.__name__} uses the @document_groups decorator "
        "which is deprecated in SQLFluff 2.0.0. Remove the decorator "
        "to resolve this warning."
    )
    return cls


def document_configuration(cls: Type["BaseRule"], **kwargs: Any) -> Type["BaseRule"]:
    """Add a 'Configuration' section to a Rule docstring."""
    rules_logger.warning(
        f"{cls.__name__} uses the @document_configuration decorator "
        "which is deprecated in SQLFluff 2.0.0. Remove the decorator "
        "to resolve this warning."
    )
    return cls

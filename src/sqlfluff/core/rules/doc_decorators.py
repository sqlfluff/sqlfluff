"""A collection of decorators to modify rule docstrings for Sphinx."""

from sqlfluff.core.rules.config_info import get_config_info
from sqlfluff.core.rules.base import rules_logger  # noqa
import re


FIX_COMPATIBLE = "    This rule is ``sqlfluff fix`` compatible."


def document_fix_compatible(cls):
    """Mark the rule as fixable in the documentation."""
    # Match `**Anti-pattern**`, `.. note::` and `**Configuration**`,
    # then insert fix_compatible before the first occurrences.
    # We match `**Configuration**` here to make it work in all order of doc decorators
    pattern = re.compile(
        "(\\s{4}\\*\\*Anti-pattern\\*\\*|\\s{4}\\.\\. note::|"
        "\\s{4}\\*\\*Configuration\\*\\*)",
        flags=re.MULTILINE,
    )
    cls.__doc__ = pattern.sub(f"\n\n{FIX_COMPATIBLE}\n\n\\1", cls.__doc__, count=1)
    return cls


def is_fix_compatible(cls) -> bool:  # pragma: no cover TODO?
    """Return whether the rule is documented as fixable."""
    return FIX_COMPATIBLE in cls.__doc__


def document_configuration(cls, ruleset="std"):
    """Add a 'Configuration' section to a Rule docstring.

    Utilize the the metadata in config_info to dynamically
    document the configuration options for a given rule.

    This is a little hacky, but it allows us to propagate configuration
    options in the docs, from a single source of truth.
    """
    if ruleset == "std":
        config_info = get_config_info()
    else:  # pragma: no cover
        raise (
            NotImplementedError(
                "Add another config info dict for the new ruleset here!"
            )
        )

    config_doc = "\n    **Configuration**\n"
    try:
        for keyword in sorted(cls.config_keywords):
            try:
                info_dict = config_info[keyword]
            except KeyError:  # pragma: no cover
                raise KeyError(
                    "Config value {!r} for rule {} is not configured in "
                    "`config_info`.".format(keyword, cls.__name__)
                )
            config_doc += "\n    * ``{}``: {}".format(keyword, info_dict["definition"])
            if (
                config_doc[-1] != "."
                and config_doc[-1] != "?"
                and config_doc[-1] != "\n"
            ):
                config_doc += "."
            if "validation" in info_dict:
                config_doc += " Must be one of ``{}``.".format(info_dict["validation"])
    except AttributeError:
        rules_logger.info(f"No config_keywords defined for {cls.__name__}")
        return cls
    # Add final blank line
    config_doc += "\n"

    if "**Anti-pattern**" in cls.__doc__:
        # Match `**Anti-pattern**`, then insert configuration before
        # the first occurrences
        pattern = re.compile("(\\s{4}\\*\\*Anti-pattern\\*\\*)", flags=re.MULTILINE)
        cls.__doc__ = pattern.sub(f"\n{config_doc}\n\\1", cls.__doc__, count=1)
    else:
        # Match last `\n` or `.`, then append configuration
        pattern = re.compile("(\\.|\\n)$", flags=re.MULTILINE)
        cls.__doc__ = pattern.sub(f"\\1\n{config_doc}\n", cls.__doc__, count=1)
    return cls


def is_configurable(cls) -> bool:
    """Return whether the rule is documented as fixable."""
    return "**Configuration**" in cls.__doc__

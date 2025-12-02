"""The capitalisation plugin bundle."""

from sqlfluff.core.plugin import hookimpl
from sqlfluff.core.rules import BaseRule, ConfigInfo


@hookimpl
def get_configs_info() -> dict[str, ConfigInfo]:
    """Get additional rule config validations and descriptions."""
    return {
        "capitalisation_policy": {
            "validation": ["consistent", "upper", "lower", "capitalise"],
            "definition": "The capitalisation policy to enforce.",
        },
        "extended_capitalisation_policy": {
            "validation": [
                "consistent",
                "upper",
                "lower",
                "pascal",
                "capitalise",
                "snake",
                "camel",
            ],
            "definition": (
                "The capitalisation policy to enforce, extended with PascalCase, "
                "snake_case, and camelCase. "
                "This is separate from ``capitalisation_policy`` as it should not be "
                "applied to keywords."
                "Camel, Pascal, and Snake will never be inferred when the policy is "
                "set to consistent. This is because snake can cause destructive "
                "changes to the identifier, and unlinted code is too easily mistaken "
                "for camel and pascal. If, when set to consistent, no consistent "
                "case is found, it will default to upper."
            ),
        },
    }


@hookimpl
def get_rules() -> list[type[BaseRule]]:
    """Get plugin rules.

    NOTE: Rules are imported only on fetch to manage import times
    when rules aren't used.
    """
    from sqlfluff.rules.capitalisation.CP01 import Rule_CP01
    from sqlfluff.rules.capitalisation.CP02 import Rule_CP02
    from sqlfluff.rules.capitalisation.CP03 import Rule_CP03
    from sqlfluff.rules.capitalisation.CP04 import Rule_CP04
    from sqlfluff.rules.capitalisation.CP05 import Rule_CP05

    return [Rule_CP01, Rule_CP02, Rule_CP03, Rule_CP04, Rule_CP05]

"""This is an example of providing config overrides."""

from sqlfluff.core import Lexer, Parser, Linter, FluffConfig

sql = "SELECT 1"


config = FluffConfig(
    overrides={
        "dialect": "snowflake",
        # NOTE: We explicitly set the string "none" here rather
        # than a None literal so that it overrides any config
        # set by any config files in the path.
        "templater": {"library_path": "none"}
    }
)

linted_file = Linter(config=config).lint_string(sql)

assert linted_file.get_violations() == []

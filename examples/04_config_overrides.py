"""This is an example of providing config overrides."""

from sqlfluff.core import FluffConfig, Linter

sql = "SELECT 1\n"


config = FluffConfig(
    overrides={
        "dialect": "snowflake",
        # NOTE: We explicitly set the string "none" here rather
        # than a None literal so that it overrides any config
        # set by any config files in the path.
        "library_path": "none",
    }
)

linted_file = Linter(config=config).lint_string(sql)

assert linted_file.get_violations() == []

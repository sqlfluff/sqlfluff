"""An example to show a few ways of configuring the API."""

import sqlfluff
from sqlfluff.core import FluffConfig, Linter

# #######################################
# The simple API can be configured in three ways.

# 1. Limited keyword arguments
sqlfluff.fix("SELECT  1", dialect="bigquery")

# 2. Providing the path to a config file
sqlfluff.fix("SELECT  1", config_path="test/fixtures/.sqlfluff")

# 3. Providing a preconfigured FluffConfig object.
# NOTE: This is the way of configuring SQLFluff which will give the most control.

# 3a. FluffConfig objects can be created directly from a dictionary of values.
config = FluffConfig(configs={"core": {"dialect": "bigquery"}})
# 3b. FluffConfig objects can be created from a config file in a string.
config = FluffConfig.from_string("[sqlfluff]\ndialect=bigquery\n")
# 3c. FluffConfig objects can be created from a config file in multiple strings
#     to simulate the effect of multiple nested config strings.
config = FluffConfig.from_strings(
    # NOTE: Given these two strings, the resulting dialect would be "mysql"
    # as the later files take precedence.
    "[sqlfluff]\ndialect=bigquery\n",
    "[sqlfluff]\ndialect=mysql\n",
)
# 3d. FluffConfig objects can be created from a path containing a config file.
config = FluffConfig.from_path("test/fixtures/")
# 3e. FluffConfig objects can be from keyword arguments
config = FluffConfig.from_kwargs(dialect="bigquery", rules=["LT01"])

# The FluffConfig is then provided via a config argument.
sqlfluff.fix("SELECT  1", config=config)


# #######################################
# The core API is always configured using a FluffConfig object.

# When instantiating a Linter (or Parser), a FluffConfig must be provided
# on instantiation. See above for details on how to create a FluffConfig.
linter = Linter(config=config)

# The provided config will then be used in any operations.

lint_result = linter.lint_string("SELECT  1", fix=True)
fixed_string = lint_result.fix_string()
# NOTE: The "True" element shows that fixing was a success.
assert fixed_string == ("SELECT 1", True)

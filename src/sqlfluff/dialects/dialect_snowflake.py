"""The Snowflake dialect.

Inherits from Postgres.

Based on https://docs.snowflake.com/en/sql-reference-commands.html
"""

from .dialect_postgres import postgres_dialect

snowflake_dialect = postgres_dialect.copy_as('snowflake')

# Semi Structured Access
# https://docs.snowflake.com/en/user-guide/semistructured-considerations.html

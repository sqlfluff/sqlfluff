"""The PostgreSQL dialect."""

from .dialect_ansi import ansi_dialect

# At the moment this is just a placeholder. Unique syntax to be added later.
postgres_dialect = ansi_dialect.copy_as('postgres')

"""The MariaDB dialect.

MariaDB is a fork of MySQL, so the dialect is very similar.
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.dialects import dialect_ansi as ansi
from sqlfluff.dialects import dialect_mysql as mysql
from sqlfluff.dialects.dialect_mariadb_keywords import (
    mariadb_reserved_keywords,
    mariadb_unreserved_keywords,
)

mysql_dialect = load_raw_dialect("mysql")
ansi_dialect = load_raw_dialect("ansi")
mariadb_dialect = mysql_dialect.copy_as("mariadb")

# Set Keywords
# Do not clear inherited unreserved ansi keywords. Too many are needed to parse well.
# Just add MariaDB unreserved keywords.
mariadb_dialect.update_keywords_set_from_multiline_string(
    "unreserved_keywords", mariadb_unreserved_keywords
)

mariadb_dialect.sets("reserved_keywords").clear()
mariadb_dialect.update_keywords_set_from_multiline_string(
    "reserved_keywords", mariadb_reserved_keywords
)

"""The Databricks Dialect.

Functionally, it is quite similar to SparkSQL,
however it's much less strict on keywords.
It also has some extensions.
"""

from sqlfluff.core.dialects import load_raw_dialect

from sqlfluff.dialects.dialect_databricks_keywords import RESERVED_KEYWORDS

sparksql_dialect = load_raw_dialect("sparksql")
databricks_dialect = sparksql_dialect.copy_as("databricks")

databricks_dialect.sets("unreserved_keywords").update(
    sparksql_dialect.sets("reserved_keywords")
)
databricks_dialect.sets("unreserved_keywords").difference_update(RESERVED_KEYWORDS)
databricks_dialect.sets("reserved_keywords").clear()
databricks_dialect.sets("reserved_keywords").update(RESERVED_KEYWORDS)

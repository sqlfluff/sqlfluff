"""A List of Databricks keywords.

This is an alias for the `sparksql` dialect keywords.
Databricks is a managed data platform built on Apache Spark
and uses the Spark SQL syntax.

Please make changes directly to the `sparksql` dialect.
"""
from sqlfluff.dialects.dialect_sparksql_keywords import (
    RESERVED_KEYWORDS as SPARKSQL_RESERVED_KEYWORDS,
    UNRESERVED_KEYWORDS as SPARKSQL_UNRESERVED_KEYWORDS,
)

RESERVED_KEYWORDS = SPARKSQL_RESERVED_KEYWORDS

UNRESERVED_KEYWORDS = SPARKSQL_UNRESERVED_KEYWORDS

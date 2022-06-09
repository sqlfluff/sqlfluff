"""The Databricks dialect.

This is an alias for the `sparksql` dialect.
Databricks is a managed data platform built on Apache Spark
and uses the Spark SQL syntax.

Please make changes directly to the `sparksql` dialect.

https://databricks.com/
"""
from sqlfluff.core.dialects import load_raw_dialect

databricks_dialect = load_raw_dialect("sparksql").copy_as("databricks")

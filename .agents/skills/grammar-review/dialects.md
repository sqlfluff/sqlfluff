# Dialect reference: vendor docs

Prefer the doc URL in the segment's own docstring. Otherwise start from the root below and
search within it, using the docs version the dialect targets.

| Dialect | Docs root |
|---|---|
| ansi | No vendor. Cross-check against postgres + <https://modern-sql.com>; ANSI should only hold what most dialects share |
| athena | <https://docs.aws.amazon.com/athena/latest/ug/ddl-sql-reference.html> (DDL is Hive-flavoured, DML is Trino) |
| bigquery | <https://cloud.google.com/bigquery/docs/reference/standard-sql/> |
| clickhouse | <https://clickhouse.com/docs/sql-reference> |
| databricks | <https://docs.databricks.com/en/sql/language-manual/index.html> |
| db2 | <https://www.ibm.com/docs/en/db2/11.5> (search "SQL statements") |
| doris | <https://doris.apache.org/docs/dev/sql-manual/sql-statements/> |
| duckdb | <https://duckdb.org/docs/sql/introduction> |
| exasol | <https://docs.exasol.com/db/latest/> (search "SQL reference") |
| flink | <https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/table/sql/overview/> |
| greenplum | <https://techdocs.broadcom.com> (search "Greenplum SQL commands"); falls back to postgres |
| hive | <https://cwiki.apache.org/confluence/display/Hive/LanguageManual> |
| impala | <https://impala.apache.org/docs/build/html/topics/impala_langref.html> |
| mariadb | <https://mariadb.com/kb/en/sql-statements/> |
| materialize | <https://materialize.com/docs/sql/> |
| mysql | <https://dev.mysql.com/doc/refman/8.4/en/sql-statements.html> |
| oracle | <https://docs.oracle.com/en/database/oracle/oracle-database/23/sqlrf/>; PL/SQL (`IF`, `LOOP`, blocks): <https://docs.oracle.com/en/database/oracle/oracle-database/23/lnpls/> |
| postgres | <https://www.postgresql.org/docs/current/sql-commands.html> |
| redshift | <https://docs.aws.amazon.com/redshift/latest/dg/c_SQL_commands.html> |
| snowflake | <https://docs.snowflake.com/en/sql-reference-commands> (a huge index: go straight to `/en/sql-reference/sql/<command>`, e.g. `create-table`) |
| soql | <https://developer.salesforce.com/docs/atlas.en-us.soql_sosl.meta/soql_sosl/> |
| sparksql | <https://spark.apache.org/docs/latest/sql-ref.html> |
| sqlite | <https://www.sqlite.org/lang.html> (railroad diagrams, so very precise) |
| starrocks | <https://docs.starrocks.io/docs/sql-reference/sql-statements/> |
| teradata | <https://docs.teradata.com> (search "SQL Data Definition Language") |
| trino | <https://trino.io/docs/current/sql.html> |
| tsql | <https://learn.microsoft.com/en-us/sql/t-sql/statements/statements> |
| vertica | <https://docs.vertica.com/latest/en/sql-reference/statements/> |

Vendor reserved-word lists, for checking reserved vs. unreserved placement:
postgres `sql-keywords-appendix.html`, mysql `keywords.html`, tsql
`reserved-keywords-transact-sql`, snowflake `reserved-keywords`, bigquery
`lexical#reserved_keywords`, oracle `Oracle-SQL-Reserved-Words`, sqlite `lang_keywords.html`.

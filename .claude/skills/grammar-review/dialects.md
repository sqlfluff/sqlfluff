# Dialect reference: vendor docs and runnable databases

Prefer the doc URL in the segment's own docstring. Fall back to the root below and
search within it. "Image ✓" means `docker manifest inspect` found it (checked
2026-11-13); "run ✓" means the exec line was actually run. Anything else is a
best guess: verify on first use and update this file.

## Docs roots

| Dialect | Docs root |
|---|---|
| ansi | No vendor. Cross-check against postgres + <https://modern-sql.com>; ANSI should only hold what most dialects share |
| athena | <https://docs.aws.amazon.com/athena/latest/ug/ddl-sql-reference.html> (DDL is Hive-flavoured, DML is Trino) |
| bigquery | <https://cloud.google.com/bigquery/docs/reference/standard-sql/> |
| clickhouse | <https://clickhouse.com/docs/sql-reference> |
| databricks | <https://docs.databricks.com/en/sql/language-manual/index.html> |
| db2 | <https://www.ibm.com/docs/en/db2/11.5> (search "SQL statements") |
| doris | <https://doris.apache.org/docs/sql-manual/> |
| duckdb | <https://duckdb.org/docs/sql/introduction> |
| exasol | <https://docs.exasol.com/db/latest/> (search "SQL reference") |
| flink | <https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/table/sql/overview/> |
| greenplum | <https://techdocs.broadcom.com> (search "Greenplum SQL commands"); falls back to postgres |
| hive | <https://cwiki.apache.org/confluence/display/Hive/LanguageManual> |
| impala | <https://impala.apache.org/docs/build/html/topics/impala_langref.html> |
| mariadb | <https://mariadb.com/kb/en/sql-statements/> |
| materialize | <https://materialize.com/docs/sql/> |
| mysql | <https://dev.mysql.com/doc/refman/8.4/en/sql-statements.html> |
| oracle | <https://docs.oracle.com/en/database/oracle/oracle-database/23/sqlrf/> |
| postgres | <https://www.postgresql.org/docs/current/sql-commands.html> |
| redshift | <https://docs.aws.amazon.com/redshift/latest/dg/c_SQL_commands.html> |
| snowflake | <https://docs.snowflake.com/en/sql-reference-commands> |
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

## Runnable databases

The container name is always `sqlfluff-review-<dialect>`. Run `docker ps -a --filter name=sqlfluff-review-` first.
Reuse a container only after checking its image matches the row below; otherwise start a fresh one. Passwords are throwaway values. Publish no ports
unless the client has to run on the host, and then bind to `127.0.0.1` only.

**Statement runner.** `./sql_run.py ENGINE FIXTURE [SETUP...]` (from this folder) covers db2, postgres,
sqlite and duckdb. It gives each statement a fresh schema and a PASS/SYNTAX/SEMANTIC/UNKNOWN verdict.
`./sql_run.py selftest` checks it without Docker. To add an engine, add one entry to its `ENGINES` table.
It splits on `;` outside quotes, comments and `$$` bodies, so postgres/duckdb dollar-quoted functions and sqlite
triggers stay whole. Unquoted compound `BEGIN … END` blocks (PL/SQL, T-SQL, Db2 compound SQL) get cut at inner
semicolons: run those through the engine's own command below instead.

**The table commands are whole-file checks.** They run the fixture as one batch against one
mutable database, so an early statement can change what later ones see. Treat them as best-effort, not
per-statement verdicts.

**Syntax error vs. semantic error.** The fixture SQL refers to tables that don't exist.
An error like "relation does not exist", "invalid object name" or "unknown table"
means the **parser accepted** the statement. Only syntax errors count against
the grammar.

### Tier 1: small and quick (seconds to ~1 min)

| Dialect | Start | Run file `$F` | Syntax-error signature | Status |
|---|---|---|---|---|
| sqlite | none (host `sqlite3`, currently 3.45) | `(cd <scratchpad> && sqlite3 -safe :memory: < "$(realpath $F)")`. Always `-safe`: fixture dot-commands (`.shell`) would otherwise run on your machine. It also blocks `ATTACH` | `syntax error` or `incomplete input`. sqlite prefixes *every* error with "Parse error", even "table already exists" | run ✓ (host binary; may lag upstream) |
| duckdb | none | `docker run --rm -i duckdb/duckdb:latest < $F` | `Parser Error:`. `Catalog Error` = parsed OK | image ✓ run ✓ |
| clickhouse | none: **parse-only**, no server | `docker run --rm -i --entrypoint clickhouse-format clickhouse/clickhouse-server:latest --multiquery < $F` | `Syntax error` | image ✓ |
| postgres | `docker run -d --name sqlfluff-review-postgres -e POSTGRES_PASSWORD=review postgres:17` | `docker exec -i sqlfluff-review-postgres psql -U postgres < $F` | `syntax error at or near` (42601) | image ✓ |
| mysql | `docker run -d --name sqlfluff-review-mysql -e MYSQL_ROOT_PASSWORD=review -e MYSQL_DATABASE=review mysql:8.4` | `docker exec -i sqlfluff-review-mysql mysql -uroot -preview review --force < $F` | `ERROR 1064` | image ✓ |
| mariadb | `docker run -d --name sqlfluff-review-mariadb -e MARIADB_ROOT_PASSWORD=review -e MARIADB_DATABASE=review mariadb:11.4` | `docker exec -i sqlfluff-review-mariadb mariadb -uroot -preview review --force < $F` | `ERROR 1064` | image ✓ |
| materialize | `docker run -d --name sqlfluff-review-materialize -p 127.0.0.1:6875:6875 materialize/materialized:latest` | `psql -h 127.0.0.1 -p 6875 -U materialize < $F` (host psql) | `syntax error` | image ✓ |
| trino (+ athena DML) | `docker run -d --name sqlfluff-review-trino trinodb/trino:latest` (~30s to ready) | `docker cp $F sqlfluff-review-trino:/tmp/t.sql && docker exec sqlfluff-review-trino trino --file /tmp/t.sql --ignore-errors` | `mismatched input` / `SYNTAX_ERROR` | image ✓ |

### Tier 2: heavier (1–10 min startup, GBs). Say so when offering.

| Dialect | Start | Run file `$F` | Syntax-error signature | Status |
|---|---|---|---|---|
| tsql | `docker run -d --name sqlfluff-review-tsql -e ACCEPT_EULA=Y -e MSSQL_SA_PASSWORD='Review_Passw0rd!' mcr.microsoft.com/mssql/server:2022-latest` (accepts the Developer-edition EULA, so tell the user) | `docker cp $F sqlfluff-review-tsql:/tmp/t.sql && docker exec sqlfluff-review-tsql /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa -P 'Review_Passw0rd!' -i /tmp/t.sql`. Prepend `SET PARSEONLY ON;\nGO\n` for a parse-only run. Statements need `GO` separators where batches matter | `Msg 102` / `Msg 156` `Incorrect syntax near` | image ✓ |
| oracle | `docker run -d --name sqlfluff-review-oracle -e ORACLE_PASSWORD=review gvenzl/oracle-free:23-slim-faststart` | `docker exec -i sqlfluff-review-oracle sqlplus -s system/review@localhost/FREEPDB1 < $F`. Add `SET SQLBLANKLINES ON` and end PL/SQL blocks with `/` | `ORA-00900`, `-00907`, `-00911`, `-00921`, `-00922`, `-00933`, `-00936`, `PLS-00103`. `SP2-0734` = SQL*Plus doesn't accept it as a top-level command (e.g. a bare PL/SQL `IF`). Note `ORA-00904`/`-00942` are semantic (= parsed OK) | image ✓ run ✓ (2026-11-14, PR 9115: scratch `CREATE USER`, wrap PL/SQL probes in `DECLARE…BEGIN…END;` + `/`, `DROP USER … CASCADE` after). The user may already have an Oracle container: ask to reuse it (password from its `ORACLE_PASSWORD` env) |
| sparksql (+ databricks, partial) | none (one-shot, ~20s JVM start) | `docker run --rm -i -v "$(realpath "$F")":/t.sql:ro apache/spark:3.5.3 /opt/spark/bin/spark-sql -f /t.sql`. Use a 4.x tag for newer syntax | `PARSE_SYNTAX_ERROR` / `ParseException`. `AnalysisException` = parsed OK | image ✓. Databricks-only syntax (Delta, Unity Catalog, `IDENTIFIER()`…) will fail here: docs only |
| hive (+ athena DDL) | `docker run -d --name sqlfluff-review-hive -e SERVICE_NAME=hiveserver2 apache/hive:4.0.0` | `docker cp $F sqlfluff-review-hive:/tmp/t.sql && docker exec sqlfluff-review-hive beeline -u jdbc:hive2://localhost:10000/ -f /tmp/t.sql` | `ParseException` | image ✓ |
| db2 | `docker run -d --name sqlfluff-review-db2 --privileged -e LICENSE=accept -e DB2INSTANCE=db2inst1 -e DB2INST1_PASSWORD=review -e DBNAME=review icr.io/db2_community/db2:latest` (~5–10 min, ~4 GB, accepts the license) | `./sql_run.py db2 $F [setup.sql ...]` (per-statement setup + ROLLBACK, TSV verdicts). Parse-only fallback: `docker cp $F sqlfluff-review-db2:/tmp/t.sql && docker exec sqlfluff-review-db2 su - db2inst1 -c "db2 connect to review && db2 -tvf /tmp/t.sql"` | `SQL0104N` (`SQL0204N`/`SQL0205N`/`SQL0612N` = parsed, semantic) | image ✓ run ✓ (2026-11-13, PR 9141) |
| starrocks | `docker run -d --name sqlfluff-review-starrocks starrocks/allin1-ubuntu:latest` | `docker exec -i sqlfluff-review-starrocks mysql -P9030 -h127.0.0.1 -uroot --force < $F` | `Getting syntax error` / `ERROR 1064` | image ✓ |
| doris | `docker run -d --name sqlfluff-review-doris apache/doris:doris-all-in-one-2.1.0` | same mysql-protocol pattern as starrocks (port 9030) | `ERROR 1105 ... Syntax error` | image ✓, exec unverified |
| exasol | `docker run -d --name sqlfluff-review-exasol --privileged exasol/docker-db:latest` (heavy) | client not bundled: `uv run --with pyexasol python -c ...` against `127.0.0.1:8563` after publishing the port | `syntax error, unexpected` | image ✓, exec unverified |
| flink | none (one-shot) | `docker run --rm -i -v "$(realpath "$F")":/t.sql:ro flink:1.20 bin/sql-client.sh -f /t.sql`. DDL/DML parse without a cluster; execution fails | `SqlParseException` | image ✓, exec unverified |

### Not runnable locally: use docs only

bigquery*, snowflake, redshift, databricks (beyond Spark OSS), athena (beyond
trino/hive), teradata (Vantage Express is a VM), soql, vertica (no maintained
public image), greenplum (no official image), impala, ansi.

\* If the user has the `bq` CLI set up, `bq query --dry_run --use_legacy_sql=false`
validates syntax for free. Ask before using any cloud credentials.

**Don't** treat postgres as evidence for redshift/greenplum/duckdb, or mysql as
evidence for starrocks/doris. They diverge too much. Only a statement that fails
on the parent too is a useful signal.

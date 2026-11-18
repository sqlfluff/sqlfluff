# Live-check backends

Read only when the user asks for a live database check. Everything here is a **candidate**
backend, not proof it's available: check the engine, version and supported operations first.
Never upload sensitive SQL or data. If nothing suitable is available, report the check as not
performed.

**Default order:** a playground that covers the engine; otherwise a disposable local container
from the tables below.

**Syntax vs. semantic errors.** Fixtures refer to tables that don't exist. "Relation does not
exist", "invalid object name" and the like mean the database **parsed** the statement. Only
syntax errors count against the grammar.

## Online playgrounds

| Service | Useful coverage | Limitation |
|---|---|---|
| [db<>fiddle](https://dbfiddle.uk/) | SQL Server, PostgreSQL, MySQL, MariaDB, Oracle, SQLite, Db2, DuckDB | Check the exact engine/version and operation restrictions |
| [ClickHouse Playground](https://clickhouse.com/docs/getting-started/playground) | ClickHouse queries | Read-only: no DDL or INSERT |
| [DuckDB Web Shell](https://shell.duckdb.org/) | Browser-local DuckDB WASM | Check version and feature availability |

## Local containers

Name containers `sqlfluff-review-<dialect>`. Reuse an existing one only if its image matches the
row below. Publish no ports unless the client runs on the host, and then bind to `127.0.0.1`.
Only stop or remove containers you started. The table commands run a whole file against one
mutable database; for per-statement verdicts, run each statement from a fresh state (`SKILL.md` step 4).

### Tier 1: small and quick (seconds to ~1 min)

| Dialect | Start | Run file `$F` | Syntax-error signature | Status |
|---|---|---|---|---|
| sqlite | none (host `sqlite3`) | `F="$(realpath "$F")"; (cd "$(mktemp -d)" && sqlite3 -safe :memory: < "$F")`. Always `-safe`: fixture dot-commands (`.shell`) would otherwise run on your machine. It also blocks `ATTACH` | `syntax error`, `incomplete input` or `unrecognized token`. sqlite prefixes *every* error with "Parse error", even "table already exists" | verified (host binary may lag upstream) |
| duckdb | none | `docker run --rm -i duckdb/duckdb:latest < $F` | `Parser Error:`. `Catalog Error` = parsed OK | verified |
| clickhouse | none: **parse-only**, no server | `docker run --rm -i --entrypoint clickhouse-format clickhouse/clickhouse-server:latest --multiquery < $F` | `Syntax error` | image exists, unverified |
| postgres | `docker run -d --name sqlfluff-review-postgres -e POSTGRES_PASSWORD=review postgres:17` | `docker exec -i sqlfluff-review-postgres psql -U postgres < $F` | `syntax error at or near` (42601) | image exists, unverified |
| mysql | `docker run -d --name sqlfluff-review-mysql -e MYSQL_ROOT_PASSWORD=review -e MYSQL_DATABASE=review mysql:8.4` | `docker exec -i sqlfluff-review-mysql mysql -uroot -preview review --force < $F` | `ERROR 1064` | image exists, unverified |
| mariadb | `docker run -d --name sqlfluff-review-mariadb -e MARIADB_ROOT_PASSWORD=review -e MARIADB_DATABASE=review mariadb:11.4` | `docker exec -i sqlfluff-review-mariadb mariadb -uroot -preview review --force < $F` | `ERROR 1064` | image exists, unverified |
| materialize | `docker run -d --name sqlfluff-review-materialize -p 127.0.0.1:6875:6875 materialize/materialized:latest` | `psql -h 127.0.0.1 -p 6875 -U materialize < $F` (host psql) | `syntax error` | image exists, unverified |
| trino (+ athena DML) | `docker run -d --name sqlfluff-review-trino trinodb/trino:latest` (~30s to ready) | `docker cp $F sqlfluff-review-trino:/tmp/t.sql && docker exec sqlfluff-review-trino trino --file /tmp/t.sql --ignore-errors` | `mismatched input` / `SYNTAX_ERROR` | image exists, unverified |

### Tier 2: heavier (1–10 min startup, GBs). Say so before starting one.

| Dialect | Start | Run file `$F` | Syntax-error signature | Status |
|---|---|---|---|---|
| tsql | `docker run -d --name sqlfluff-review-tsql -e ACCEPT_EULA=Y -e MSSQL_SA_PASSWORD='Review_Passw0rd!' mcr.microsoft.com/mssql/server:2022-latest` (accepts the Developer-edition EULA, so tell the user) | `docker cp $F sqlfluff-review-tsql:/tmp/t.sql && docker exec sqlfluff-review-tsql /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa -P 'Review_Passw0rd!' -i /tmp/t.sql`. Prepend `SET PARSEONLY ON;\nGO\n` for a parse-only run. Statements need `GO` separators where batches matter | `Msg 102` / `Msg 156` `Incorrect syntax near` | image exists, unverified |
| oracle | `docker run -d --name sqlfluff-review-oracle -e ORACLE_PASSWORD=review gvenzl/oracle-free:23-slim-faststart` | `docker exec -i sqlfluff-review-oracle sqlplus -s system/review@localhost/FREEPDB1 < $F`. Add `SET SQLBLANKLINES ON` and end PL/SQL blocks with `/` | `ORA-00900`, `-00907`, `-00911`, `-00921`, `-00922`, `-00933`, `-00936`, `PLS-00103`. `SP2-0734` = SQL*Plus doesn't accept it as a top-level command (e.g. a bare PL/SQL `IF`). Note `ORA-00904`/`-00942` are semantic (= parsed OK) | verified. Work in a scratch `CREATE USER`; wrap PL/SQL probes in `DECLARE…BEGIN…END;` + `/`; `DROP USER … CASCADE` after |
| sparksql (+ databricks, partial) | none (one-shot, ~20s JVM start) | `docker run --rm -i -v "$(realpath "$F")":/t.sql:ro apache/spark:3.5.3 /opt/spark/bin/spark-sql -f /t.sql`. Use a 4.x tag for newer syntax | `PARSE_SYNTAX_ERROR` / `ParseException`. `AnalysisException` = parsed OK | Databricks-only syntax (Delta, Unity Catalog, `IDENTIFIER()`…) will fail here: docs only |
| hive (+ athena DDL) | `docker run -d --name sqlfluff-review-hive -e SERVICE_NAME=hiveserver2 apache/hive:4.0.0` | `docker cp $F sqlfluff-review-hive:/tmp/t.sql && docker exec sqlfluff-review-hive beeline -u jdbc:hive2://localhost:10000/ -f /tmp/t.sql` | `ParseException` | image exists, unverified |
| db2 | `docker run -d --name sqlfluff-review-db2 --privileged -e LICENSE=accept -e DB2INSTANCE=db2inst1 -e DB2INST1_PASSWORD=review -e DBNAME=review icr.io/db2_community/db2:latest` (~5–10 min, ~4 GB, accepts the license) | `docker cp $F sqlfluff-review-db2:/tmp/t.sql && docker exec sqlfluff-review-db2 su - db2inst1 -c "db2 connect to review && db2 -tvf /tmp/t.sql"` | `SQL0104N` (`SQL0204N`/`SQL0205N`/`SQL0612N` = parsed, semantic) | verified |
| starrocks | `docker run -d --name sqlfluff-review-starrocks starrocks/allin1-ubuntu:latest` | `docker exec -i sqlfluff-review-starrocks mysql -P9030 -h127.0.0.1 -uroot --force < $F` | `Getting syntax error` / `ERROR 1064` | image exists, unverified |
| doris | `docker run -d --name sqlfluff-review-doris apache/doris:doris-all-in-one-2.1.0` | same mysql-protocol pattern as starrocks (port 9030) | `ERROR 1105 ... Syntax error` | unverified |
| exasol | `docker run -d --name sqlfluff-review-exasol --privileged exasol/docker-db:latest` (heavy) | client not bundled: `uv run --with pyexasol python -c ...` against `127.0.0.1:8563` after publishing the port | `syntax error, unexpected` | unverified |
| flink | none (one-shot) | `docker run --rm -i -v "$(realpath "$F")":/t.sql:ro flink:1.20 bin/sql-client.sh -f /t.sql`. DDL/DML parse without a cluster; execution fails | `SqlParseException` | unverified |

### Not runnable locally: use docs only

bigquery*, snowflake, redshift, databricks (beyond Spark OSS), athena (beyond
trino/hive), teradata (Vantage Express is a VM), soql, vertica (no maintained
public image), greenplum (no official image), impala, ansi.

\* If the user has the `bq` CLI set up, `bq query --dry_run --use_legacy_sql=false` validates syntax.
Ask before using any cloud credentials.

**Don't** treat postgres as evidence for redshift/greenplum/duckdb, or mysql as
evidence for starrocks/doris. They diverge too much. Only a statement that fails
on the parent too is a useful signal.

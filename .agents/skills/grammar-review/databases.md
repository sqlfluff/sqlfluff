# Live-check backends

Read only when the user asks for a live database check. Everything here is a **candidate**
backend, not proof it's available: check the engine, version and supported operations first.
Never upload sensitive SQL or data. If nothing suitable is available, report the check as not
performed.

**Default order:** a playground that covers the engine; otherwise a disposable local container.
Name containers `sqlfluff-review-<dialect>`, reuse one only if its image matches, publish ports
only to `127.0.0.1`, and only stop or remove containers you started.

**Syntax vs. semantic errors.** Fixtures refer to tables that don't exist. "Relation does not
exist", "invalid object name" and the like mean the database **parsed** the statement. Only
syntax errors count against the grammar.

## Online playgrounds

| Service | Useful coverage | Limitation |
|---|---|---|
| [db<>fiddle](https://dbfiddle.uk/) | SQL Server, PostgreSQL, MySQL, MariaDB, Oracle, SQLite, Db2, DuckDB | Check the exact engine/version and operation restrictions |
| [ClickHouse Playground](https://clickhouse.com/docs/getting-started/playground) | ClickHouse queries | Read-only: no DDL or INSERT |
| [DuckDB Web Shell](https://shell.duckdb.org/) | Browser-local DuckDB WASM | Check version and feature availability |

## Local engines

Heavy images (1–10 min startup, GBs) are marked; say so before starting one, along with any
licence or EULA the image accepts.

| Dialect | Image or tool | Notes | Syntax error | Parsed (semantic error) |
|---|---|---|---|---|
| sqlite | host `sqlite3` | Always run with `-safe` from a temp dir: otherwise fixture dot-commands (`.shell`) run on your machine. `-safe` also blocks `ATTACH` | `syntax error`, `incomplete input`, `unrecognized token` | Everything else; every error starts with "Parse error" |
| duckdb | `duckdb/duckdb` | One-shot, no server | `Parser Error` | `Catalog Error` |
| clickhouse | `clickhouse-format` in `clickhouse/clickhouse-server` | Parse-only, no server needed | `Syntax error` | — |
| postgres | `postgres:17` | | `syntax error at or near` (42601), `unterminated …` | `does not exist` |
| mysql / mariadb | `mysql:8.4` / `mariadb:11.4` | | `ERROR 1064` | other `ERROR` codes |
| materialize | `materialize/materialized` | psql protocol on port 6875 | `syntax error` | |
| trino (+ athena DML) | `trinodb/trino` | ~30 s to ready | `mismatched input`, `SYNTAX_ERROR` | |
| tsql | `mcr.microsoft.com/mssql/server:2022-latest` | Heavy; accepts the Developer-edition EULA. `SET PARSEONLY ON` gives a parse-only run; mind `GO` batches | `Msg 102`, `Msg 156` | `Msg 208` (invalid object) |
| oracle | `gvenzl/oracle-free:23-slim-faststart` | Heavy. Work in a scratch user, `DROP USER … CASCADE` after. Wrap PL/SQL probes in `DECLARE … BEGIN … END;` plus `/`; `SET SQLBLANKLINES ON` | `ORA-00900`, `-00907`, `-00911`, `-00921`, `-00922`, `-00933`, `-00936`, `PLS-00103`; `SP2-0734` = SQL\*Plus rejects it as a top-level command | `ORA-00904`, `ORA-00942` |
| sparksql (+ databricks, partial) | `apache/spark` (4.x for newer syntax) | One-shot `spark-sql`, ~20 s JVM start. Databricks-only syntax (Delta, Unity Catalog, `IDENTIFIER()`) fails here: docs only | `PARSE_SYNTAX_ERROR`, `ParseException` | `AnalysisException` |
| hive (+ athena DDL) | `apache/hive:4.0.0` | Heavy; `beeline` against HiveServer2 | `ParseException` | |
| db2 | `icr.io/db2_community/db2` | Heavy (~5–10 min, ~4 GB); needs `--privileged`; accepts the licence | `SQL0104N`, `SQL0007N` | `SQL0204N`, `SQL0205N`, `SQL0612N` |
| starrocks / doris | `starrocks/allin1-ubuntu` / `apache/doris` all-in-one | Heavy; MySQL protocol on port 9030. Unverified | `ERROR 1064` / `Syntax error` | |
| exasol | `exasol/docker-db` | Heavy; needs `--privileged`; no bundled client. Unverified | `syntax error, unexpected` | |
| flink | `flink:1.20` | One-shot `sql-client.sh`; DDL/DML parse without a cluster. Unverified | `SqlParseException` | |

## Not runnable locally: docs only

bigquery\*, snowflake, redshift, databricks (beyond Spark OSS), athena (beyond trino/hive),
teradata (Vantage Express is a VM), soql, vertica (no maintained public image), greenplum (no
official image), impala, ansi.

\* With the `bq` CLI set up, `bq query --dry_run --use_legacy_sql=false` validates syntax. Ask
before using any cloud credentials.

Don't treat postgres as evidence for redshift/greenplum/duckdb, or mysql as evidence for
starrocks/doris: they diverge too much. Only a statement that fails on the parent too is a
useful signal.

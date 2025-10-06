/* This is a generated file! */

pub mod parser;

/* dialect mods */
pub mod ansi;
use crate::dialect::ansi::matcher::ANSI_KEYWORDS;
use crate::dialect::ansi::matcher::ANSI_LEXERS;
pub mod athena;
use crate::dialect::athena::matcher::ATHENA_KEYWORDS;
use crate::dialect::athena::matcher::ATHENA_LEXERS;
pub mod bigquery;
use crate::dialect::bigquery::matcher::BIGQUERY_KEYWORDS;
use crate::dialect::bigquery::matcher::BIGQUERY_LEXERS;
pub mod clickhouse;
use crate::dialect::clickhouse::matcher::CLICKHOUSE_KEYWORDS;
use crate::dialect::clickhouse::matcher::CLICKHOUSE_LEXERS;
pub mod databricks;
use crate::dialect::databricks::matcher::DATABRICKS_KEYWORDS;
use crate::dialect::databricks::matcher::DATABRICKS_LEXERS;
pub mod db2;
use crate::dialect::db2::matcher::DB2_KEYWORDS;
use crate::dialect::db2::matcher::DB2_LEXERS;
pub mod doris;
use crate::dialect::doris::matcher::DORIS_KEYWORDS;
use crate::dialect::doris::matcher::DORIS_LEXERS;
pub mod duckdb;
use crate::dialect::duckdb::matcher::DUCKDB_KEYWORDS;
use crate::dialect::duckdb::matcher::DUCKDB_LEXERS;
pub mod exasol;
use crate::dialect::exasol::matcher::EXASOL_KEYWORDS;
use crate::dialect::exasol::matcher::EXASOL_LEXERS;
pub mod flink;
use crate::dialect::flink::matcher::FLINK_KEYWORDS;
use crate::dialect::flink::matcher::FLINK_LEXERS;
pub mod greenplum;
use crate::dialect::greenplum::matcher::GREENPLUM_KEYWORDS;
use crate::dialect::greenplum::matcher::GREENPLUM_LEXERS;
pub mod hive;
use crate::dialect::hive::matcher::HIVE_KEYWORDS;
use crate::dialect::hive::matcher::HIVE_LEXERS;
pub mod impala;
use crate::dialect::impala::matcher::IMPALA_KEYWORDS;
use crate::dialect::impala::matcher::IMPALA_LEXERS;
pub mod mariadb;
use crate::dialect::mariadb::matcher::MARIADB_KEYWORDS;
use crate::dialect::mariadb::matcher::MARIADB_LEXERS;
pub mod materialize;
use crate::dialect::materialize::matcher::MATERIALIZE_KEYWORDS;
use crate::dialect::materialize::matcher::MATERIALIZE_LEXERS;
pub mod mysql;
use crate::dialect::mysql::matcher::MYSQL_KEYWORDS;
use crate::dialect::mysql::matcher::MYSQL_LEXERS;
pub mod oracle;
use crate::dialect::oracle::matcher::ORACLE_KEYWORDS;
use crate::dialect::oracle::matcher::ORACLE_LEXERS;
pub mod postgres;
use crate::dialect::postgres::matcher::POSTGRES_KEYWORDS;
use crate::dialect::postgres::matcher::POSTGRES_LEXERS;
pub mod redshift;
use crate::dialect::redshift::matcher::REDSHIFT_KEYWORDS;
use crate::dialect::redshift::matcher::REDSHIFT_LEXERS;
pub mod snowflake;
use crate::dialect::snowflake::matcher::SNOWFLAKE_KEYWORDS;
use crate::dialect::snowflake::matcher::SNOWFLAKE_LEXERS;
pub mod soql;
use crate::dialect::soql::matcher::SOQL_KEYWORDS;
use crate::dialect::soql::matcher::SOQL_LEXERS;
pub mod sparksql;
use crate::dialect::sparksql::matcher::SPARKSQL_KEYWORDS;
use crate::dialect::sparksql::matcher::SPARKSQL_LEXERS;
pub mod sqlite;
use crate::dialect::sqlite::matcher::SQLITE_KEYWORDS;
use crate::dialect::sqlite::matcher::SQLITE_LEXERS;
pub mod starrocks;
use crate::dialect::starrocks::matcher::STARROCKS_KEYWORDS;
use crate::dialect::starrocks::matcher::STARROCKS_LEXERS;
pub mod teradata;
use crate::dialect::teradata::matcher::TERADATA_KEYWORDS;
use crate::dialect::teradata::matcher::TERADATA_LEXERS;
pub mod trino;
use crate::dialect::trino::matcher::TRINO_KEYWORDS;
use crate::dialect::trino::matcher::TRINO_LEXERS;
pub mod tsql;
use crate::dialect::tsql::matcher::TSQL_KEYWORDS;
use crate::dialect::tsql::matcher::TSQL_LEXERS;
pub mod vertica;
use crate::dialect::vertica::matcher::VERTICA_KEYWORDS;
use crate::dialect::vertica::matcher::VERTICA_LEXERS;

use crate::matcher::LexMatcher;
use std::str::FromStr;

#[derive(Debug, Eq, PartialEq, Hash, Copy, Clone)]
pub enum Dialect {
    Ansi,
    Athena,
    Bigquery,
    Clickhouse,
    Databricks,
    Db2,
    Doris,
    Duckdb,
    Exasol,
    Flink,
    Greenplum,
    Hive,
    Impala,
    Mariadb,
    Materialize,
    Mysql,
    Oracle,
    Postgres,
    Redshift,
    Snowflake,
    Soql,
    Sparksql,
    Sqlite,
    Starrocks,
    Teradata,
    Trino,
    Tsql,
    Vertica
}

impl Dialect {
    pub(crate) fn get_reserved_keywords(&self) -> &'static Vec<String> {
        match self {
            Dialect::Ansi => &ANSI_KEYWORDS,
            Dialect::Athena => &ATHENA_KEYWORDS,
            Dialect::Bigquery => &BIGQUERY_KEYWORDS,
            Dialect::Clickhouse => &CLICKHOUSE_KEYWORDS,
            Dialect::Databricks => &DATABRICKS_KEYWORDS,
            Dialect::Db2 => &DB2_KEYWORDS,
            Dialect::Doris => &DORIS_KEYWORDS,
            Dialect::Duckdb => &DUCKDB_KEYWORDS,
            Dialect::Exasol => &EXASOL_KEYWORDS,
            Dialect::Flink => &FLINK_KEYWORDS,
            Dialect::Greenplum => &GREENPLUM_KEYWORDS,
            Dialect::Hive => &HIVE_KEYWORDS,
            Dialect::Impala => &IMPALA_KEYWORDS,
            Dialect::Mariadb => &MARIADB_KEYWORDS,
            Dialect::Materialize => &MATERIALIZE_KEYWORDS,
            Dialect::Mysql => &MYSQL_KEYWORDS,
            Dialect::Oracle => &ORACLE_KEYWORDS,
            Dialect::Postgres => &POSTGRES_KEYWORDS,
            Dialect::Redshift => &REDSHIFT_KEYWORDS,
            Dialect::Snowflake => &SNOWFLAKE_KEYWORDS,
            Dialect::Soql => &SOQL_KEYWORDS,
            Dialect::Sparksql => &SPARKSQL_KEYWORDS,
            Dialect::Sqlite => &SQLITE_KEYWORDS,
            Dialect::Starrocks => &STARROCKS_KEYWORDS,
            Dialect::Teradata => &TERADATA_KEYWORDS,
            Dialect::Trino => &TRINO_KEYWORDS,
            Dialect::Tsql => &TSQL_KEYWORDS,
            Dialect::Vertica => &VERTICA_KEYWORDS,
        }
    }



    pub fn get_lexers(&self) -> &'static Vec<LexMatcher> {
        match self {
            Dialect::Ansi => &ANSI_LEXERS,
            Dialect::Athena => &ATHENA_LEXERS,
            Dialect::Bigquery => &BIGQUERY_LEXERS,
            Dialect::Clickhouse => &CLICKHOUSE_LEXERS,
            Dialect::Databricks => &DATABRICKS_LEXERS,
            Dialect::Db2 => &DB2_LEXERS,
            Dialect::Doris => &DORIS_LEXERS,
            Dialect::Duckdb => &DUCKDB_LEXERS,
            Dialect::Exasol => &EXASOL_LEXERS,
            Dialect::Flink => &FLINK_LEXERS,
            Dialect::Greenplum => &GREENPLUM_LEXERS,
            Dialect::Hive => &HIVE_LEXERS,
            Dialect::Impala => &IMPALA_LEXERS,
            Dialect::Mariadb => &MARIADB_LEXERS,
            Dialect::Materialize => &MATERIALIZE_LEXERS,
            Dialect::Mysql => &MYSQL_LEXERS,
            Dialect::Oracle => &ORACLE_LEXERS,
            Dialect::Postgres => &POSTGRES_LEXERS,
            Dialect::Redshift => &REDSHIFT_LEXERS,
            Dialect::Snowflake => &SNOWFLAKE_LEXERS,
            Dialect::Soql => &SOQL_LEXERS,
            Dialect::Sparksql => &SPARKSQL_LEXERS,
            Dialect::Sqlite => &SQLITE_LEXERS,
            Dialect::Starrocks => &STARROCKS_LEXERS,
            Dialect::Teradata => &TERADATA_LEXERS,
            Dialect::Trino => &TRINO_LEXERS,
            Dialect::Tsql => &TSQL_LEXERS,
            Dialect::Vertica => &VERTICA_LEXERS,
        }
    }
}

impl FromStr for Dialect {
    type Err = ();
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s {
            "ansi" => Ok(Dialect::Ansi),
            "athena" => Ok(Dialect::Athena),
            "bigquery" => Ok(Dialect::Bigquery),
            "clickhouse" => Ok(Dialect::Clickhouse),
            "databricks" => Ok(Dialect::Databricks),
            "db2" => Ok(Dialect::Db2),
            "doris" => Ok(Dialect::Doris),
            "duckdb" => Ok(Dialect::Duckdb),
            "exasol" => Ok(Dialect::Exasol),
            "flink" => Ok(Dialect::Flink),
            "greenplum" => Ok(Dialect::Greenplum),
            "hive" => Ok(Dialect::Hive),
            "impala" => Ok(Dialect::Impala),
            "mariadb" => Ok(Dialect::Mariadb),
            "materialize" => Ok(Dialect::Materialize),
            "mysql" => Ok(Dialect::Mysql),
            "oracle" => Ok(Dialect::Oracle),
            "postgres" => Ok(Dialect::Postgres),
            "redshift" => Ok(Dialect::Redshift),
            "snowflake" => Ok(Dialect::Snowflake),
            "soql" => Ok(Dialect::Soql),
            "sparksql" => Ok(Dialect::Sparksql),
            "sqlite" => Ok(Dialect::Sqlite),
            "starrocks" => Ok(Dialect::Starrocks),
            "teradata" => Ok(Dialect::Teradata),
            "trino" => Ok(Dialect::Trino),
            "tsql" => Ok(Dialect::Tsql),
            "vertica" => Ok(Dialect::Vertica),
            _ => Err(()),
        }
    }
}

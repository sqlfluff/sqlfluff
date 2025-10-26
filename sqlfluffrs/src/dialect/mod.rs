/* This is a generated file! */

use std::sync::Arc;

/* dialect mods */
pub mod ansi;
use crate::dialect::ansi::matcher::{ANSI_KEYWORDS, ANSI_LEXERS};
pub mod athena;
use crate::dialect::athena::matcher::{ATHENA_KEYWORDS, ATHENA_LEXERS};
pub mod bigquery;
use crate::dialect::bigquery::matcher::{BIGQUERY_KEYWORDS, BIGQUERY_LEXERS};
pub mod clickhouse;
use crate::dialect::clickhouse::matcher::{CLICKHOUSE_KEYWORDS, CLICKHOUSE_LEXERS};
pub mod databricks;
use crate::dialect::databricks::matcher::{DATABRICKS_KEYWORDS, DATABRICKS_LEXERS};
pub mod db2;
use crate::dialect::db2::matcher::{DB2_KEYWORDS, DB2_LEXERS};
pub mod doris;
use crate::dialect::doris::matcher::{DORIS_KEYWORDS, DORIS_LEXERS};
pub mod duckdb;
use crate::dialect::duckdb::matcher::{DUCKDB_KEYWORDS, DUCKDB_LEXERS};
pub mod exasol;
use crate::dialect::exasol::matcher::{EXASOL_KEYWORDS, EXASOL_LEXERS};
pub mod flink;
use crate::dialect::flink::matcher::{FLINK_KEYWORDS, FLINK_LEXERS};
pub mod greenplum;
use crate::dialect::greenplum::matcher::{GREENPLUM_KEYWORDS, GREENPLUM_LEXERS};
pub mod hive;
use crate::dialect::hive::matcher::{HIVE_KEYWORDS, HIVE_LEXERS};
pub mod impala;
use crate::dialect::impala::matcher::{IMPALA_KEYWORDS, IMPALA_LEXERS};
pub mod mariadb;
use crate::dialect::mariadb::matcher::{MARIADB_KEYWORDS, MARIADB_LEXERS};
pub mod materialize;
use crate::dialect::materialize::matcher::{MATERIALIZE_KEYWORDS, MATERIALIZE_LEXERS};
pub mod mysql;
use crate::dialect::mysql::matcher::{MYSQL_KEYWORDS, MYSQL_LEXERS};
pub mod oracle;
use crate::dialect::oracle::matcher::{ORACLE_KEYWORDS, ORACLE_LEXERS};
pub mod postgres;
use crate::dialect::postgres::matcher::{POSTGRES_KEYWORDS, POSTGRES_LEXERS};
pub mod redshift;
use crate::dialect::redshift::matcher::{REDSHIFT_KEYWORDS, REDSHIFT_LEXERS};
pub mod snowflake;
use crate::dialect::snowflake::matcher::{SNOWFLAKE_KEYWORDS, SNOWFLAKE_LEXERS};
pub mod soql;
use crate::dialect::soql::matcher::{SOQL_KEYWORDS, SOQL_LEXERS};
pub mod sparksql;
use crate::dialect::sparksql::matcher::{SPARKSQL_KEYWORDS, SPARKSQL_LEXERS};
pub mod sqlite;
use crate::dialect::sqlite::matcher::{SQLITE_KEYWORDS, SQLITE_LEXERS};
pub mod starrocks;
use crate::dialect::starrocks::matcher::{STARROCKS_KEYWORDS, STARROCKS_LEXERS};
pub mod teradata;
use crate::dialect::teradata::matcher::{TERADATA_KEYWORDS, TERADATA_LEXERS};
pub mod trino;
use crate::dialect::trino::matcher::{TRINO_KEYWORDS, TRINO_LEXERS};
pub mod tsql;
use crate::dialect::tsql::matcher::{TSQL_KEYWORDS, TSQL_LEXERS};
pub mod vertica;
use crate::dialect::vertica::matcher::{VERTICA_KEYWORDS, VERTICA_LEXERS};

use crate::parser::Grammar;
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
    Vertica,
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

    pub fn get_segment_grammar(&self, name: &str) -> Option<Arc<Grammar>> {
        match self {
            Dialect::Ansi => crate::dialect::ansi::parser::get_ansi_segment_grammar(name),
            Dialect::Athena => crate::dialect::athena::parser::get_athena_segment_grammar(name),
            Dialect::Bigquery => crate::dialect::bigquery::parser::get_bigquery_segment_grammar(name),
            Dialect::Clickhouse => crate::dialect::clickhouse::parser::get_clickhouse_segment_grammar(name),
            Dialect::Databricks => crate::dialect::databricks::parser::get_databricks_segment_grammar(name),
            Dialect::Db2 => crate::dialect::db2::parser::get_db2_segment_grammar(name),
            Dialect::Doris => crate::dialect::doris::parser::get_doris_segment_grammar(name),
            Dialect::Duckdb => crate::dialect::duckdb::parser::get_duckdb_segment_grammar(name),
            Dialect::Exasol => crate::dialect::exasol::parser::get_exasol_segment_grammar(name),
            Dialect::Flink => crate::dialect::flink::parser::get_flink_segment_grammar(name),
            Dialect::Greenplum => crate::dialect::greenplum::parser::get_greenplum_segment_grammar(name),
            Dialect::Hive => crate::dialect::hive::parser::get_hive_segment_grammar(name),
            Dialect::Impala => crate::dialect::impala::parser::get_impala_segment_grammar(name),
            Dialect::Mariadb => crate::dialect::mariadb::parser::get_mariadb_segment_grammar(name),
            Dialect::Materialize => crate::dialect::materialize::parser::get_materialize_segment_grammar(name),
            Dialect::Mysql => crate::dialect::mysql::parser::get_mysql_segment_grammar(name),
            Dialect::Oracle => crate::dialect::oracle::parser::get_oracle_segment_grammar(name),
            Dialect::Postgres => crate::dialect::postgres::parser::get_postgres_segment_grammar(name),
            Dialect::Redshift => crate::dialect::redshift::parser::get_redshift_segment_grammar(name),
            Dialect::Snowflake => crate::dialect::snowflake::parser::get_snowflake_segment_grammar(name),
            Dialect::Soql => crate::dialect::soql::parser::get_soql_segment_grammar(name),
            Dialect::Sparksql => crate::dialect::sparksql::parser::get_sparksql_segment_grammar(name),
            Dialect::Sqlite => crate::dialect::sqlite::parser::get_sqlite_segment_grammar(name),
            Dialect::Starrocks => crate::dialect::starrocks::parser::get_starrocks_segment_grammar(name),
            Dialect::Teradata => crate::dialect::teradata::parser::get_teradata_segment_grammar(name),
            Dialect::Trino => crate::dialect::trino::parser::get_trino_segment_grammar(name),
            Dialect::Tsql => crate::dialect::tsql::parser::get_tsql_segment_grammar(name),
            Dialect::Vertica => crate::dialect::vertica::parser::get_vertica_segment_grammar(name),
        }
    }

    pub fn get_segment_type(&self, name: &str) -> Option<&'static str> {
        match self {
            Dialect::Ansi => crate::dialect::ansi::parser::get_ansi_segment_type(name),
            Dialect::Athena => crate::dialect::athena::parser::get_athena_segment_type(name),
            Dialect::Bigquery => crate::dialect::bigquery::parser::get_bigquery_segment_type(name),
            Dialect::Clickhouse => crate::dialect::clickhouse::parser::get_clickhouse_segment_type(name),
            Dialect::Databricks => crate::dialect::databricks::parser::get_databricks_segment_type(name),
            Dialect::Db2 => crate::dialect::db2::parser::get_db2_segment_type(name),
            Dialect::Doris => crate::dialect::doris::parser::get_doris_segment_type(name),
            Dialect::Duckdb => crate::dialect::duckdb::parser::get_duckdb_segment_type(name),
            Dialect::Exasol => crate::dialect::exasol::parser::get_exasol_segment_type(name),
            Dialect::Flink => crate::dialect::flink::parser::get_flink_segment_type(name),
            Dialect::Greenplum => crate::dialect::greenplum::parser::get_greenplum_segment_type(name),
            Dialect::Hive => crate::dialect::hive::parser::get_hive_segment_type(name),
            Dialect::Impala => crate::dialect::impala::parser::get_impala_segment_type(name),
            Dialect::Mariadb => crate::dialect::mariadb::parser::get_mariadb_segment_type(name),
            Dialect::Materialize => crate::dialect::materialize::parser::get_materialize_segment_type(name),
            Dialect::Mysql => crate::dialect::mysql::parser::get_mysql_segment_type(name),
            Dialect::Oracle => crate::dialect::oracle::parser::get_oracle_segment_type(name),
            Dialect::Postgres => crate::dialect::postgres::parser::get_postgres_segment_type(name),
            Dialect::Redshift => crate::dialect::redshift::parser::get_redshift_segment_type(name),
            Dialect::Snowflake => crate::dialect::snowflake::parser::get_snowflake_segment_type(name),
            Dialect::Soql => crate::dialect::soql::parser::get_soql_segment_type(name),
            Dialect::Sparksql => crate::dialect::sparksql::parser::get_sparksql_segment_type(name),
            Dialect::Sqlite => crate::dialect::sqlite::parser::get_sqlite_segment_type(name),
            Dialect::Starrocks => crate::dialect::starrocks::parser::get_starrocks_segment_type(name),
            Dialect::Teradata => crate::dialect::teradata::parser::get_teradata_segment_type(name),
            Dialect::Trino => crate::dialect::trino::parser::get_trino_segment_type(name),
            Dialect::Tsql => crate::dialect::tsql::parser::get_tsql_segment_type(name),
            Dialect::Vertica => crate::dialect::vertica::parser::get_vertica_segment_type(name),
        }
    }

    pub fn get_root_grammar(&self) -> Arc<Grammar> {
        match self {
            Dialect::Ansi => crate::dialect::ansi::parser::get_ansi_root_grammar(),
            Dialect::Athena => crate::dialect::athena::parser::get_athena_root_grammar(),
            Dialect::Bigquery => crate::dialect::bigquery::parser::get_bigquery_root_grammar(),
            Dialect::Clickhouse => crate::dialect::clickhouse::parser::get_clickhouse_root_grammar(),
            Dialect::Databricks => crate::dialect::databricks::parser::get_databricks_root_grammar(),
            Dialect::Db2 => crate::dialect::db2::parser::get_db2_root_grammar(),
            Dialect::Doris => crate::dialect::doris::parser::get_doris_root_grammar(),
            Dialect::Duckdb => crate::dialect::duckdb::parser::get_duckdb_root_grammar(),
            Dialect::Exasol => crate::dialect::exasol::parser::get_exasol_root_grammar(),
            Dialect::Flink => crate::dialect::flink::parser::get_flink_root_grammar(),
            Dialect::Greenplum => crate::dialect::greenplum::parser::get_greenplum_root_grammar(),
            Dialect::Hive => crate::dialect::hive::parser::get_hive_root_grammar(),
            Dialect::Impala => crate::dialect::impala::parser::get_impala_root_grammar(),
            Dialect::Mariadb => crate::dialect::mariadb::parser::get_mariadb_root_grammar(),
            Dialect::Materialize => crate::dialect::materialize::parser::get_materialize_root_grammar(),
            Dialect::Mysql => crate::dialect::mysql::parser::get_mysql_root_grammar(),
            Dialect::Oracle => crate::dialect::oracle::parser::get_oracle_root_grammar(),
            Dialect::Postgres => crate::dialect::postgres::parser::get_postgres_root_grammar(),
            Dialect::Redshift => crate::dialect::redshift::parser::get_redshift_root_grammar(),
            Dialect::Snowflake => crate::dialect::snowflake::parser::get_snowflake_root_grammar(),
            Dialect::Soql => crate::dialect::soql::parser::get_soql_root_grammar(),
            Dialect::Sparksql => crate::dialect::sparksql::parser::get_sparksql_root_grammar(),
            Dialect::Sqlite => crate::dialect::sqlite::parser::get_sqlite_root_grammar(),
            Dialect::Starrocks => crate::dialect::starrocks::parser::get_starrocks_root_grammar(),
            Dialect::Teradata => crate::dialect::teradata::parser::get_teradata_root_grammar(),
            Dialect::Trino => crate::dialect::trino::parser::get_trino_root_grammar(),
            Dialect::Tsql => crate::dialect::tsql::parser::get_tsql_root_grammar(),
            Dialect::Vertica => crate::dialect::vertica::parser::get_vertica_root_grammar()
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

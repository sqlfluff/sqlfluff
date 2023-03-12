"""A list of all Athena keywords.

Presto List: https://prestodb.io/docs/0.217/language/reserved.html
Hive List: https://cwiki.apache.org/confluence/display/Hive/LanguageManual+DDL
"""

athena_reserved_keywords = [
    "ALL",
    "ALTER",
    "AND",
    "ARRAY",
    "AS",
    "AUTHORIZATION",
    "BETWEEN",
    "BIGINT",
    "BINARY",
    "BOOLEAN",
    "BOTH",
    "BY",
    "CACHE",
    "CASE",
    "CAST",
    "CHAR",
    "COLUMN",
    "COMMIT",
    "CONF",
    "CONSTRAINT",
    "CREATE",
    "CROSS",
    "CUBE",
    "CURRENT_DATE",
    "CURRENT_TIMESTAMP",
    "CURRENT",
    "CURSOR",
    "DATABASE",
    "DECIMAL",
    "DELETE",
    "DESCRIBE",
    "DISTINCT",
    "DOUBLE",
    "DROP",
    "ELSE",
    "END",
    "EXCHANGE",
    "EXISTS",
    "EXTENDED",
    "EXTERNAL",
    "EXTRACT",
    "FALSE",
    "FETCH",
    "FLOAT",
    "FLOOR",
    "FOLLOWING",
    "FOR",
    "FOREIGN",
    "FROM",
    "FULL",
    "FUNCTION",
    "GRANT",
    "GROUP",
    "GROUPING",
    "HAVING",
    "IF",
    "IMPORT",
    "IN",
    "INNER",
    "INSERT",
    "INT",
    "INTEGER",
    "INTERSECT",
    "INTERVAL",
    "INTO",
    "IS",
    "JOIN",
    "LATERAL",
    "LEFT",
    "LESS",
    "LIKE",
    "LOCAL",
    "MACRO",
    "MAP",
    "MORE",
    "NONE",
    "NOT",
    "NULL",
    "NUMERIC",
    "OF",
    "ON",
    "ONLY",
    "OR",
    "ORDER",
    "OUT",
    "OUTER",
    "OVER",
    "PARTIALSCAN",
    "PARTITION",
    "PERCENT",
    "PRECEDING",
    "PRECISION",
    "PREPARE",
    "PRESERVE",
    "PRIMARY",
    "PROCEDURE",
    "RANGE",
    "READS",
    "REDUCE",
    "REFERENCES",
    "REGEXP",
    "REVOKE",
    "RIGHT",
    "RLIKE",
    "ROLLBACK",
    "ROLLUP",
    "SELECT",
    "SET",
    "SMALLINT",
    "START",
    "SYNC",
    "TABLE",
    "TABLESAMPLE",
    "THEN",
    "TO",
    "TRANSFORM",
    "TRIGGER",
    "TRUE",
    "TRUNCATE",
    "UNBOUNDED",
    "UNION",
    "UNIQUEJOIN",
    "UPDATE",
    "USING",
    "UTC_TMESTAMP",
    "VALUES",
    "VARCHAR",
    "WHEN",
    "WHERE",
    "WITH",
]

athena_unreserved_keywords = [
    "ABORT",
    "ADD",
    "ADMIN",
    "AFTER",
    "ANALYZE",
    "ARCHIVE",
    "ASC",
    "AUTOCOMMIT",
    "BEFORE",
    "BUCKET_COUNT",
    "BUCKET",
    "BUCKETED_BY",
    "BUCKETS",
    "CASCADE",
    "CHANGE",
    "CLUSTER",
    "CLUSTERED",
    "CLUSTERSTATUS",
    "COLLECTION",
    "COLUMNS",
    "COMMENT",
    "COMPACT",
    "COMPACTIONS",
    "COMPRESSION",
    "COMPUTE",
    "CONCATENATE",
    "CONTINUE",
    "DATA",
    "DATABASES",
    "DATE",
    "DATETIME",
    "DAY",
    "DAYOFWEEK",
    "DBPROPERTIES",
    "DEFERRED",
    "DEFINED",
    "DELIMITED",
    "DEPENDENCY",
    "DESC",
    "DIRECTORIES",
    "DIRECTORY",
    "DISABLE",
    "DISTRIBUTE",
    "ELEM_TYPE",
    "ENABLE",
    "ESCAPED",
    "EXCLUSIVE",
    "EXPLAIN",
    "EXPORT",
    "EXTERNAL_LOCATION",
    "FIELD_DELIMITER",
    "FIELDS",
    "FILE",
    "FILEFORMAT",
    "FIRST",
    "FORMAT",
    "FORMATTED",
    "FUNCTIONS",
    "HOLD_DDLTIME",
    "HOUR",
    "HYPERLOGLOG",
    "IDXPROPERTIES",
    "IGNORE",
    "INDEX",
    "INDEXES",
    "INPATH",
    "INPUTDRIVER",
    "INPUTFORMAT",
    "IPADDRESS",
    "IS_EXTERNAL",
    "ISOLATION",
    "ITEMS",
    "JAR",
    "KEY_TYPE",
    "KEY",
    "KEYS",
    "LAST",
    "LEVEL",
    "LIMIT",
    "LINES",
    "LOAD",
    "LOCATION",
    "LOCK",
    "LOCKS",
    "LOGICAL",
    "LONG",
    "MAPJOIN",
    "MATERIALIZED",
    "METADATA",
    "MINUS",
    "MINUTE",
    "MONTH",
    "MSCK",
    "NO_DROP",
    "NORELY",
    "NOSCAN",
    "NOVALIDATE",
    "NULLS",
    "OFFLINE",
    "OFFSET",
    "OPTION",
    "ORC_COMPRESSION",
    "OUTPUTDRIVER",
    "OUTPUTFORMAT",
    "OVERWRITE",
    "OWNER",
    "P4HYPERLOGLOG",
    "PARQUET_COMPRESSION",
    "PARTITIONED_BY",
    "PARTITIONED",
    "PARTITIONING",
    "PARTITIONS",
    "PLUS",
    "PRETTY",
    "PRINCIPALS",
    "PROTECTION",
    "PURGE",
    "QDIGEST",
    "READ",
    "READONLY",
    "REBUILD",
    "RECORDREADER",
    "RECORDWRITER",
    "REGEXP",
    "RELOAD",
    "RELY",
    "RENAME",
    "REPAIR",
    "REPLACE",
    "REPLICATION",
    "RESTRICT",
    "REWRITE",
    "RLIKE",
    "ROLE",
    "ROLES",
    "ROW",
    "ROWS",
    "SCHEMA",
    "SCHEMAS",
    "SECOND",
    "SEMI",
    "SERDE",
    "SERDEPROPERTIES",
    "SERVER",
    "SETS",
    "SHARED",
    "SHOW_DATABASE",
    "SHOW",
    "SKEWED",
    "SNAPSHOT",
    "SORT",
    "SORTED",
    "SSL",
    "STATISTICS",
    "STORED",
    "STREAMTABLE",
    "STRING",
    "STRUCT",
    "TABLE_TYPE",
    "TABLES",
    "TBLPROPERTIES",
    "TEMPORARY",
    "TERMINATED",
    "TIME",
    "TIMESTAMP",
    "TIMESTAMPTZ",
    "TINYINT",
    "TOUCH",
    "TRANSACTION",
    "TRANSACTIONS",
    "UNARCHIVE",
    "UNDO",
    "UNIONTYPE",
    "UNLOAD",
    "UNLOCK",
    "UNSET",
    "UNSIGNED",
    "URI",
    "USE",
    "USER",
    "UTC",
    "UTCTIMESTAMP",
    "VACUUM_MAX_SNAPSHOT_AGE_MS",
    "VACUUM_MIN_SNAPSHOTS_TO_KEEP",
    "VALIDATE",
    "VALUE_TYPE",
    "VIEW",
    "VIEWS",
    "WINDOW",
    "WHILE",
    "WRITE_COMPRESSION",
    "YEAR",
    "ZONE",
]

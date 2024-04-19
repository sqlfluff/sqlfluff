"""A List of Spark SQL keywords.

https://spark.apache.org/docs/latest/sql-ref-ansi-compliance.html#sql-keywords
"""

RESERVED_KEYWORDS = [
    "ALL",
    "AND",
    "ANY",
    "AS",
    "AUTHORIZATION",
    "BOTH",
    "CASE",
    "CAST",
    "CHECK",
    "COLLATE",
    "COLUMN",
    "CONSTRAINT",
    "CREATE",
    "CROSS",
    "CURRENT_DATE",
    "CURRENT_TIME",
    "CURRENT_TIMESTAMP",
    "CURRENT_USER",
    "ELSE",
    "END",
    "ESCAPE",
    "EXCEPT",
    "FALSE",
    "FETCH",
    "FILTER",
    "FOR",
    "FOREIGN",
    "FROM",
    "FULL",
    "GRANT",
    "GROUP",
    "HAVING",
    "IN",
    "INNER",
    "INTERSECT",
    "INTO",
    "IS",
    "JOIN",
    "LEADING",
    "LEFT",
    "NATURAL",
    "NOT",
    "NULL",
    "ON",
    "ONLY",
    "OR",
    "ORDER",
    "OUTER",
    "OVERLAPS",
    "PRIMARY",
    "REFERENCES",
    "RIGHT",
    "SELECT",
    "SESSION_USER",
    "SOME",
    "TABLE",
    "THEN",
    "TO",
    "TRAILING",
    "UNION",
    "UNIQUE",
    "UNKNOWN",
    "USER",
    "USING",
    "WHEN",
    "WHERE",
    "WITH",
]

UNRESERVED_KEYWORDS = [
    "ADD",
    "AFTER",
    "ALTER",
    "ANALYZE",
    "ANTI",
    "ARCHIVE",
    "ARRAY",
    "ASC",
    "AT",
    "BERNOULLI",
    "BETWEEN",
    "BUCKET",
    "BUCKETS",
    "BY",
    "CACHE",
    "CASCADE",
    "CHANGE",
    "CLEAR",
    "CLUSTER",
    "CLUSTERED",
    "CODEGEN",
    "COLLECTION",
    "COLUMNS",
    "COMMENT",
    "COMMIT",
    "COMPACT",
    "COMPACTIONS",
    "COMPUTE",
    "CONCATENATE",
    "COST",
    "CUBE",
    "CURRENT",
    "DATA",
    "DATE",
    "DATE_HOUR",
    "DATABASE",
    "DATABASES",
    "DAY",
    "DAYS",
    "DBPROPERTIES",
    "DEFINED",
    "DELETE",
    "DELIMITED",
    "DESC",
    "DESCRIBE",
    "DFS",
    "DIRECTORIES",
    "DIRECTORY",
    "DISTINCT",
    "DISTRIBUTE",
    "DISTRIBUTED",
    "DIV",
    "DROP",
    "ESCAPED",
    "EXCHANGE",
    "EXISTS",
    "EXPLAIN",
    "EXPORT",
    "EXTENDED",
    "EXTERNAL",
    "EXTRACT",
    "FIELD",
    "FIELDS",
    "FILEFORMAT",
    "FIRST",
    "FOLLOWING",
    "FORMAT",
    "FORMATTED",
    "FUNCTION",
    "FUNCTIONS",
    "GLOBAL",
    "GROUPING",
    "HOUR",
    "HOURS",
    "IDENTIFIER",
    "IF",
    "IGNORE",
    "ILIKE",
    "IMPORT",
    "INDEX",
    "INDEXES",
    "INPATH",
    "INPUTFORMAT",
    "INSERT",
    "INTERVAL",
    "ITEMS",
    "KEYS",
    "LAST",
    "LAZY",
    "LIKE",
    "LIMIT",
    "LINES",
    "LIST",
    "LOAD",
    "LOCAL",
    "LOCALLY",
    "LOCATION",
    "LOCK",
    "LOCKS",
    "LOGICAL",
    "MACRO",
    "MAP",
    "MATCHED",
    "MERGE",
    "MINUTE",
    "MONTH",
    "MONTHS",
    "MSCK",
    "NAMESPACE",
    "NAMESPACES",
    "NO",
    "NULLS",
    "OF",
    "OPTION",
    "OPTIONS",
    "ORDERED",
    "OUT",
    "OUTPUTFORMAT",
    "OVER",
    "OVERLAY",
    "OVERWRITE",
    "PARTITION",
    "PARTITIONED",
    "PARTITIONS",
    "PERCENTLIT",
    "PIVOT",
    "PLACING",
    "POSITION",
    "PRECEDING",
    "PRINCIPALS",
    "PROPERTIES",
    "PURGE",
    "QUALIFY",
    "QUERY",
    "RANGE",
    "RECORDREADER",
    "RECORDWRITER",
    "RECOVER",
    "REDUCE",
    "REFRESH",
    "RENAME",
    "REPAIR",
    "REPEATABLE",
    "REPLACE",
    "RESET",
    "RESPECT",
    "RESTRICT",
    "REVOKE",
    "RLIKE",
    "ROLE",
    "ROLES",
    "ROLLBACK",
    "ROLLUP",
    "ROW",
    "ROWS",
    "SCHEMA",
    "SECOND",
    "SEMI",
    "SEPARATED",
    "SERDE",
    "SERDEPROPERTIES",
    "SET",
    "SETMINUS",
    "SETS",
    "SHOW",
    "SKEWED",
    "SORT",
    "SORTED",
    "START",
    "STATISTICS",
    "STORED",
    "STRATIFY",
    "STRUCT",
    "SUBSTR",
    "SUBSTRING",
    "SYNC",
    "SYSTEM",
    "TABLES",
    "TABLESAMPLE",
    "TBLPROPERTIES",
    "TEMP",
    "TEMPORARY",
    "TERMINATED",
    "TIME",
    "TIMESTAMP_LTZ",
    "TIMESTAMP_NTZ",
    "TOUCH",
    "TRANSACTION",
    "TRANSACTIONS",
    "TRANSFORM",
    "TRIM",
    "TRUE",
    "TRUNCATE",
    "TRY_CAST",
    "TYPE",
    "UNARCHIVE",
    "UNBOUNDED",
    "UNCACHE",
    "UNLOCK",
    "UNPIVOT",
    "UNSET",
    "UPDATE",
    "USE",
    "VALUES",
    "VIEW",
    "VIEWS",
    "WRITE",
    "WINDOW",
    "YEAR",
    "YEARS",
    "ZONE",
    # Spark Core Data Sources
    # https://spark.apache.org/docs/latest/sql-data-sources.html
    "AVRO",
    "CSV",
    "JSON",
    "PARQUET",
    "ORC",
    "JDBC",
    # Community Contributed Data Sources
    "DELTA",  # https://github.com/delta-io/delta
    "XML",  # https://github.com/databricks/spark-xml
    "ICEBERG",
    # Delta Lake
    "DETAIL",
    "DRY",
    "GENERATE",
    "HISTORY",
    "RETAIN",
    "RUN",
    # Databricks - Delta Live Tables
    "CHANGES",
    "DELETES",
    "EXPECT",
    "FAIL",
    "LIVE",
    "SCD",
    "STREAMING",
    "UPDATES",
    "VIOLATION",
    # Databricks widget
    "WIDGET",
    "DROPDOWN",
    "TEXT",
    "CHOICES",
    "REMOVE",
]

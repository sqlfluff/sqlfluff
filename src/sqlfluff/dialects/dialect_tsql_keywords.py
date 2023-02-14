"""A list of all SQL key words.

https://docs.microsoft.com/en-us/sql/t-sql/language-elements/reserved-keywords-transact-sql?view=sql-server-ver15
"""

RESERVED_KEYWORDS = [
    "ADD",
    "ALL",
    "ALTER",
    "AND",
    "ANY",
    "APPEND",
    "AS",
    "ASC",
    "AUTHORIZATION",
    "BACKUP",
    "BATCHSIZE",
    "BEGIN",
    "BETWEEN",
    "BREAK",
    "BROWSE",
    "BULK",
    "BY",
    "CASCADE",
    "CASE",
    "CHECK",
    "CHECK_CONSTRAINTS",
    "CHECKPOINT",
    "CLOSE",
    "CLUSTERED",
    "COALESCE",
    "COLLATE",
    "COLUMN",
    "COMMIT",
    "COMPUTE",
    "CONSTRAINT",
    "CONTAINS",
    "CONTAINSTABLE",
    "CONTINUE",
    "CONVERT",
    "CREATE",
    "CROSS",
    "CURRENT_DATE",
    "CURRENT_TIME",
    "CURRENT_TIMESTAMP",
    "CURRENT_USER",
    "CURRENT",
    "CURSOR",
    "DATABASE",
    "DAY",
    "DBCC",
    "DEALLOCATE",
    "DECLARE",
    "DEFAULT",
    "DELETE",
    "DENY",
    "DESC",
    "DISTINCT",
    "DISTRIBUTED",
    "DOUBLE",
    "DROP",
    "DYNAMIC",
    "ELSE",
    "END",
    "ERRLVL",
    "ESCAPE",
    "EXCEPT",
    "EXEC",
    "EXECUTE",
    "EXISTS",
    "EXIT",
    "EXTERNAL",
    "FAST_FORWARD",
    "FETCH",
    "FILE",
    "FILLFACTOR",
    "FOR",
    "FORWARD_ONLY",
    "FOREIGN",
    "FREETEXT",
    "FREETEXTTABLE",
    "FROM",
    "FULL",
    "FULLSCAN",
    "FUNCTION",
    "GLOBAL",
    "GO",
    "GOTO",
    "GRANT",
    "GROUP",
    "HAVING",
    "HOLDLOCK",
    "IDENTITY_INSERT",
    "IDENTITY",
    "IDENTITYCOL",
    "IF",
    "IN",
    "INDEX",
    "INNER",
    "INSERT",
    "INTERSECT",
    "INTO",
    "IS",
    "JOIN",
    "KEY",
    "KEYSET",
    "KILL",
    "LEFT",
    "LIKE",
    "LINENO",
    "LOCAL",
    "MERGE",
    "NATIONAL",
    "NATIVE_COMPILATION",
    "NOCHECK",
    "NONCLUSTERED",
    "NOT",
    "NULL",
    "NULLIF",
    "OF",
    "OFF",
    "OFFSETS",
    "ON",
    "OPEN",
    "OPENDATASOURCE",
    "OPENQUERY",
    "OPENROWSET",
    "OPENXML",
    "OPTIMISTIC",
    "OPTION",
    "OR",
    "ORDER",
    "OUTER",
    "OVER",
    "PERCENT",
    "PIVOT",
    "PLAN",
    "PRIMARY",
    "PRINT",
    "PROC",
    "PROCEDURE",
    "PUBLIC",
    "RAISERROR",
    "READ",
    "READ_ONLY",
    "READTEXT",
    "RECONFIGURE",
    "REFERENCES",
    "REPLICATION",
    "RESAMPLE",
    "RESTORE",
    "RESTRICT",
    "RETURN",
    "REVERT",
    "REVOKE",
    "RIGHT",
    "ROLLBACK",
    "ROWCOUNT",
    "ROWGUIDCOL",
    "RULE",
    "SAVE",
    "SCHEMA",
    "SCROLL",
    "SCROLL_LOCKS",
    "SELECT",
    "SEMANTICKEYPHRASETABLE",
    "SEMANTICSIMILARITYDETAILSTABLE",
    "SEMANTICSIMILARITYTABLE",
    "SESSION_USER",
    "SET",
    "SETUSER",
    "SHUTDOWN",
    "SOME",
    "STATIC",
    "STATISTICS",
    "SYSTEM_USER",
    "TABLE",
    "TABLESAMPLE",
    "TEXTSIZE",
    "THEN",
    "TO",
    "TOP",
    "TRAN",
    "TRANSACTION",
    "TRAN",
    "TRIGGER",
    "TRUNCATE",
    "TRY_CONVERT",
    "TSEQUAL",
    "TYPE_WARNING",
    "UNION",
    "UNIQUE",
    "UNPIVOT",
    "UPDATE",
    "UPDATETEXT",
    "USE",
    "USER",
    "VALUES",
    "VARYING",
    "VIEW",
    "WAITFOR",
    "WHEN",
    "WHERE",
    "WHILE",
    "WITH",
    "WRITETEXT",
]


UNRESERVED_KEYWORDS = [
    "ABORT",
    "ABORT_AFTER_WAIT",
    "AFTER",
    "ALGORITHM",
    "ALLOW_PAGE_LOCKS",
    "ALLOW_ROW_LOCKS",
    "ALWAYS",
    "ANSI_DEFAULTS",
    "ANSI_NULL_DFLT_OFF",
    "ANSI_NULL_DFLT_ON",
    "ANSI_NULLS",
    "ANSI_PADDING",
    "ANSI_WARNINGS",
    "APPEND_ONLY",
    "APPLY",
    "ARITHABORT",
    "ARITHIGNORE",
    "AT",
    "AUTO",
    "BERNOULLI",
    "BLOCKERS",
    "BREAK",
    "CACHE",
    "CALLED",
    "CALLER",
    "CAST",
    "CATCH",
    "CODEPAGE",
    "COLUMN_ENCRYPTION_KEY",
    "COLUMNSTORE",
    "COLUMNSTORE_ARCHIVE",
    "COMMITTED",
    "CONCAT",
    "CONCAT_NULL_YIELDS_NULL",
    "CONTAINED",
    "CONTINUE",
    "CONTROL",
    "COMPRESS_ALL_ROW_GROUPS",
    "COMPRESSION_DELAY",
    "CURSOR_CLOSE_ON_COMMIT",
    "CYCLE",
    "DATA_CONSISTENCY_CHECK",
    "DATA_COMPRESSION",
    "DATA_DELETION",
    "DATA_SOURCE",
    "DATAFILETYPE",
    "DATASOURCE",
    "DATE",
    "DATEFIRST",
    "DATEFORMAT",
    "DEADLOCK_PRIORITY",
    "DELAY",
    "DENSE_RANK",
    "DETERMINISTIC",
    "DISABLE",
    "DISK",  # listed as reserved but functionally unreserved
    "DISTRIBUTION",  # Azure Synapse Analytics specific
    "DROP_EXISTING",
    "DUMP",  # listed as reserved but functionally unreserved
    "DURABILITY",
    "ENCRYPTED",
    "ENCRYPTION",
    "ENCRYPTION_TYPE",
    "ERRORFILE",
    "ERRORFILE_DATA_SOURCE",
    "EXPAND",
    "EXPLAIN",  # Azure Synapse Analytics specific
    "EXPLICIT",
    "EXTERNALPUSHDOWN",
    "FAST",
    "FIELDQUOTE",
    "FIELDTERMINATOR",
    "FILESTREAM",
    "FILESTREAM_ON",
    "FILETABLE_DIRECTORY",
    "FILETABLE_COLLATE_FILENAME",
    "FILETABLE_FULLPATH_UNIQUE_CONSTRAINT_NAME",
    "FILETABLE_PRIMARY_KEY_CONSTRAINT_NAME",
    "FILETABLE_STREAMID_UNIQUE_CONSTRAINT_NAME",
    "FILTER",
    "FILTER_PREDICATE",
    "FILTER_COLUMN",
    "FIPS_FLAGGER",
    "FIRST",
    "FIRSTROW",
    "FIRE_TRIGGERS",
    "FMTONLY",
    "FOLLOWING",
    "FOR",
    "FORCE",
    "FORCEPLAN",
    "FORCESCAN",
    "FORCESEEK",
    "FORMAT",
    "FORMATFILE",
    "FORMATFILE_DATA_SOURCE",
    "HASH",
    "HEAP",  # Azure Synapse Analytics specific
    "HIDDEN",
    "HINT",
    "HISTORY_TABLE",
    "IGNORE",
    "IGNORE_CONSTRAINTS",
    "IGNORE_DUP_KEY",
    "IGNORE_NONCLUSTERED_COLUMNSTORE_INDEX",
    "IGNORE_TRIGGERS",
    "IMPLICIT_TRANSACTIONS",
    "INBOUND",
    "INCLUDE",
    "INCREMENT",
    "INLINE",
    "INSTEAD",
    "INTERVAL",
    "IO",
    "ISOLATION",
    "GENERATED",
    "KEEP",
    "KEEPDEFAULTS",
    "KEEPFIXED",
    "KEEPIDENTITY",
    "KEEPNULLS",
    "KILOBYTES_PER_BATCH",
    # LABEL is an Azure Synapse Analytics specific reserved keyword
    # but could break TSQL parsing to add there
    "LABEL",
    "LANGUAGE",
    "LAST",
    "LASTROW",
    "LEDGER",
    "LEDGER_VIEW",
    "LEVEL",
    "LOAD",  # listed as reserved but functionally unreserved
    "LOB_COMPACTION",
    "LOCATION",
    "LOCK_TIMEOUT",
    "LOG",
    "LOGIN",
    "LOOP",
    "MAX_DURATION",
    "MAX_GRANT_PERCENT",
    "MASKED",
    "MATCHED",
    "MAX",
    "MAXDOP",
    "MAXERRORS",
    "MAXRECURSION",
    "MAXVALUE",
    "MEMORY_OPTIMIZED",
    "MIGRATION_STATE",
    "MIN_GRANT_PERCENT",
    "MINUTES",
    "MINVALUE",
    "NEXT",
    "NO",
    "NO_PERFORMANCE_SPOOL",
    "NOCOUNT",
    "NOEXEC",
    "NOEXPAND",
    "NOLOCK",
    "NONE",
    "NOWAIT",
    "NTILE",
    "NUMERIC_ROUNDABORT",
    "OBJECT",
    "OFFSET",
    "ONLINE",
    "OPERATION_TYPE_COLUMN_NAME",
    "OPERATION_TYPE_DESC_COLUMN_NAME",
    "OPTIMIZE",
    "OPTIMIZE_FOR_SEQUENTIAL_KEY",
    "OUT",
    "OUTBOUND",
    "OUTPUT",
    "OWNER",
    "PAD_INDEX",
    "PAGE",
    "PAGLOCK",
    "PARAMETER",
    "PARAMETERIZATION",
    "PARSEONLY",
    "PARTITION",
    "PARTITIONS",
    "PATH",
    "PAUSE",
    "PAUSED",
    "PERCENTILE_CONT",
    "PERCENTILE_DISC",
    "PERSISTED",
    "PRECEDING",
    "PRECISION",  # listed as reserved but functionally unreserved
    "PRIOR",
    "PROFILE",
    "QUERY_GOVERNOR_COST_LIMIT",
    "QUERYTRACEON",
    "QUOTED_IDENTIFIER",
    "RANDOMIZED",
    "RANGE",
    "RANK",
    "RAW",
    "REBUILD",
    "READCOMMITTED",
    "READCOMMITTEDLOCK",
    "READONLY",
    "READPAST",
    "READUNCOMMITTED",
    "RECEIVE",
    "RECOMPILE",
    "RECURSIVE",
    "REMOTE_DATA_ARCHIVE",
    "REMOTE_PROC_TRANSACTIONS",
    "RENAME",  # Azure Synapse Analytics specific
    "REORGANIZE",
    "REPEATABLE",
    "REPEATABLEREAD",
    "REPLACE",
    "REPLICATE",  # Azure Synapse Analytics
    "RESPECT",
    "RESULT_SET_CACHING",  # Azure Synapse Analytics specific
    "RESUMABLE",
    "RESUME",
    "RETENTION_PERIOD",
    "RETURNS",
    "ROBUST",
    "ROLE",
    "ROUND_ROBIN",  # Azure Synapse Analytics specific
    "ROW",
    "ROW_NUMBER",
    "ROWGUIDCOL",
    "ROWLOCK",
    "ROWS",
    "ROWS_PER_BATCH",
    "ROWTERMINATOR",
    "S",
    "SCALEOUTEXECUTION",
    "SCHEMA_ONLY",
    "SCHEMA_AND_DATA",
    "SCHEMABINDING",
    "SECURITYAUDIT",  # listed as reserved but functionally unreserved
    "SELF",
    "SETERROR",
    "SEQUENCE",
    "SEQUENCE_NUMBER",
    "SEQUENCE_NUMBER_COLUMN_NAME",
    "SERIALIZABLE",
    "SERVER",
    "SHOWPLAN_ALL",
    "SHOWPLAN_TEXT",
    "SHOWPLAN_XML",
    "SINGLE_BLOB",
    "SINGLE_CLOB",
    "SINGLE_NCLOB",
    "SNAPSHOT",
    "SORT_IN_TEMPDB",
    "SOURCE",
    "SPARSE",
    "SPATIAL_WINDOW_MAX_CELLS",
    "START",
    "STATISTICS_INCREMENTAL",
    "STATISTICS_NORECOMPUTE",
    "STRING_AGG",
    "SYNONYM",
    "SWITCH",
    "SYSTEM",
    "SYSTEM_TIME",
    "SYSTEM_VERSIONING",
    "TABLOCK",
    "TABLOCKX",
    "TAKE",
    "TARGET",
    "TEXTIMAGE_ON",
    "THROW",
    "TIES",
    "TIME",
    "TIMEOUT",
    "TIMESTAMP",
    "TRANSACTION_ID",
    "TRANSACTION_ID_COLUMN_NAME",
    "TRUNCATE_TARGET",  # Azure Synapse Analytics specific
    "TRY",
    "TYPE",
    "UPDLOCK",
    "UNBOUNDED",
    "UNCOMMITTED",
    "UNKNOWN",
    "USER_DB",  # Azure Synapse Analytics specific, deprecated
    "USING",
    "VALUE",
    "VIEW_METADATA",
    "WAITFOR",
    "WAIT_AT_LOW_PRIORITY",
    "WITHIN",
    "WHILE",
    "WORK",
    "XACT_ABORT",
    "XLOCK",
    "XML",
    "XML_COMPRESSION",
    "ZONE",
]

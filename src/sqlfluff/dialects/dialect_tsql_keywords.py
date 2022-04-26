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
    "BEGIN",
    "BETWEEN",
    "BREAK",
    "BROWSE",
    "BULK",
    "BY",
    "CASCADE",
    "CASE",
    "CHECK",
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
    "APPLY",
    "ARITHABORT",
    "ARITHIGNORE",
    "AT",
    "BERNOULLI",
    "BLOCKERS",
    "BREAK",
    "CACHE",
    "CALLED",
    "CALLER",
    "CAST",
    "CATCH",
    "COLUMN_ENCRYPTION_KEY",
    "COLUMNSTORE",
    "COLUMNSTORE_ARCHIVE",
    "COMMITTED",
    "CONCAT",
    "CONCAT_NULL_YIELDS_NULL",
    "CONTINUE",
    "CONTROL",
    "COMPRESSION_DELAY",
    "CURSOR_CLOSE_ON_COMMIT",
    "CYCLE",
    "DATA_COMPRESSION",
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
    "ENCRYPTED",
    "ENCRYPTION",
    "ENCRYPTION_TYPE",
    "EXPAND",
    "EXPLAIN",  # Azure Synapse Analytics specific
    "EXTERNALPUSHDOWN",
    "FAST",
    "FILESTREAM",
    "FILESTREAM_ON",
    "FILTER",
    "FIPS_FLAGGER",
    "FIRST",
    "FMTONLY",
    "FOLLOWING",
    "FORCE",
    "FORCEPLAN",
    "FORCESCAN",
    "FORCESEEK",
    "HASH",
    "HEAP",  # Azure Synapse Analytics specific
    "HIDDEN",
    "HINT",
    "IGNORE",
    "IGNORE_CONSTRAINTS",
    "IGNORE_DUP_KEY",
    "IGNORE_NONCLUSTERED_COLUMNSTORE_INDEX",
    "IGNORE_TRIGGERS",
    "IMPLICIT_TRANSACTIONS",
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
    # LABEL is an Azure Synapse Analytics specific reserved keyword
    # but could break TSQL parsing to add there
    "LABEL",
    "LANGUAGE",
    "LAST",
    "LEVEL",
    "LOAD",  # listed as reserved but functionally unreserved
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
    "MAXRECURSION",
    "MAXVALUE",
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
    "OPTIMIZE",
    "OPTIMIZE_FOR_SEQUENTIAL_KEY",
    "OUT",
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
    "READCOMMITTED",
    "READCOMMITTEDLOCK",
    "READONLY",
    "READPAST",
    "READUNCOMMITTED",
    "RECEIVE",
    "RECOMPILE",
    "RECURSIVE",
    "REMOTE_PROC_TRANSACTIONS",
    "RENAME",  # Azure Synapse Analytics specific
    "REPEATABLE",
    "REPEATABLEREAD",
    "REPLACE",
    "REPLICATE",  # Azure Synapse Analytics
    "RESPECT",
    "RESULT_SET_CACHING",  # Azure Synapse Analytics specific
    "RESUMABLE",
    "RETURNS",
    "ROBUST",
    "ROLE",
    "ROUND_ROBIN",  # Azure Synapse Analytics specific
    "ROW",
    "ROW_NUMBER",
    "ROWGUIDCOL",
    "ROWLOCK",
    "ROWS",
    "S",
    "SCALEOUTEXECUTION",
    "SCHEMABINDING",
    "SECURITYAUDIT",  # listed as reserved but functionally unreserved
    "SELF",
    "SETERROR",
    "SEQUENCE",
    "SEQUENCE_NUMBER",
    "SERIALIZABLE",
    "SERVER",
    "SHOWPLAN_ALL",
    "SHOWPLAN_TEXT",
    "SHOWPLAN_XML",
    "SNAPSHOT",
    "SORT_IN_TEMPDB",
    "SOURCE",
    "SPARSE",
    "SPATIAL_WINDOW_MAX_CELLS",
    "START",
    "STATISTICS_INCREMENTAL",
    "STATISTICS_NORECOMPUTE",
    "STRING_AGG",
    "SWITCH",
    "SYSTEM",
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
    "ZONE",
]

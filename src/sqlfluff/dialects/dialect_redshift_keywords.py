"""A list of all SQL key words."""

redshift_reserved_keywords = """AES128
AES256
ALL
ALLOWOVERWRITE
ANALYSE
ANALYZE
AND
ANY
ARRAY
AS
ASC
AUTHORIZATION
AZ64
BETWEEN
BINARY
BLANKSASNULL
BOTH
BYTEDICT
CASE
CAST
CHECK
COLLATE
COLUMN
COMPROWS
COMPUPDATE
CONSTRAINT
CREATE
CREDENTIALS
CROSS
CURRENT_DATE
CURRENT_TIME
CURRENT_TIMESTAMP
CURRENT_USER
CURRENT_USER_ID
DATETIME
DEFAULT
DEFERRABLE
DEFRAG
DELIMITERS
DELTA
DELTA32K
DESC
DISABLE
DISTINCT
DO
ELSE
EMPTYASNULL
ENABLE
ENCRYPT
ENCRYPTION
END
EXCEPT
EXPLICIT_IDS
FALSE
FILLRECORD
FOR
FOREIGN
FREEZE
FROM
FULL
GLOBALDICT256
GLOBALDICT64K
GRANT
GROUP
HAVING
IDENTITY
IGNORE
IGNOREBLANKLINES
IGNOREHEADER
ILIKE
IN
INITIALLY
INNER
INTERSECT
INTO
IS
ISNULL
JOIN
LEADING
LEFT
LIKE
LIMIT
LOCALTIME
LOCALTIMESTAMP
LUN
LUNS
LZO
MINUS
MOSTLY16
MOSTLY32
MOSTLY8
NATURAL
NEW
NOT
NOTNULL
NULL
NULLS
OFF
OFFSET
OID
OLD
ON
ONLY
OPEN
OR
ORDER
OUTER
OVERLAPS
PARALLEL
PARTITION
PERCENT
PERMISSIONS
PIVOT
PLACING
PRIMARY
RAW
READRATIO
RECOVER
REFERENCES
RESPECT
REJECTLOG
RESORT
RESTORE
RIGHT
RUNLENGTH
SELECT
SESSION_USER
SIMILAR
SNAPSHOT
SOME
SYSDATE
SYSTEM
TABLE
TAG
TDES
TEXT255
TEXT32K
THEN
TIMESTAMP
TO
TOP
TRAILING
TRUE
TRUNCATECOLUMNS
UNION
UNIQUE
UNNEST
UNPIVOT
USER
USING
VERBOSE
WHEN
WHERE
WITH
WITHIN
WITHOUT"""

redshift_unreserved_keywords = """A
ABORT
ABS
ABSENT
ABSOLUTE
ACCEPTANYDATE
ACCEPTINVCHARS
ACCESS
ACCESS_KEY_ID
ACCORDING
ACCOUNT
ACOS
ACTION
ADA
ADD
ADDQUOTES
ADMIN
AFTER
AGGREGATE
ALLOCATE
ALSO
ALTER
ALWAYS
APPLY
ARE
ARRAY_AGG
ARRAY_MAX_CARDINALITY
ASENSITIVE
ASIN
ASSERTION
ASSIGNMENT
ASYMMETRIC
AT
ATAN
ATOMIC
ATTACH
ATTRIBUTE
ATTRIBUTES
AUTO
AUTO_INCREMENT
AVG
AVRO
BACKUP
BACKWARD
BASE64
BEFORE
BEGIN
BEGIN_FRAME
BEGIN_PARTITION
BERNOULLI
BIGINT
BINARY_CLASSIFICATION
BINDING
BIT
BIT_LENGTH
BLANKSASNULL
BLOB
BLOCKED
BOM
BOOL
BOOLEAN
BOOST
BPCHAR
BREADTH
BUFFERS
BY
BYPASSRLS
BZIP2
C
CACHE
CALL
CALLED
CARDINALITY
CASCADE
CASCADED
CASE_INSENSITIVE
CASE_SENSITIVE
CATALOG
CATALOG_NAME
CATALOG_ROLE
CEIL
CEILING
CHAIN
CHAINING
CHAR
CHARACTER
CHARACTERISTICS
CHARACTERS
CHARACTER_LENGTH
CHARACTER_SET_CATALOG
CHARACTER_SET_NAME
CHARACTER_SET_SCHEMA
CHAR_LENGTH
CHECKPOINT
CLASS
CLASSIFIER
CLASS_ORIGIN
CLEANPATH
CLOB
CLOSE
CLUSTER
COALESCE
COBOL
COLLATION
COLLATION_CATALOG
COLLATION_NAME
COLLATION_SCHEMA
COLLECT
COLUMNS
COLUMN_NAME
COMMAND_FUNCTION
COMMAND_FUNCTION_CODE
COMMENT
COMMENTS
COMMIT
COMMITTED
COMPOUND
COMPRESSION
CONCURRENTLY
CONDITION
CONDITIONAL
CONDITION_NUMBER
CONFIGURATION
CONFLICT
CONNECT
CONNECTION
CONNECTION_NAME
CONSTRAINTS
CONSTRAINT_CATALOG
CONSTRAINT_NAME
CONSTRAINT_SCHEMA
CONSTRUCTOR
CONTAINS
CONTENT
CONTINUE
CONTROL
CONVERSION
CONVERT
COPY
CORR
CORRESPONDING
COS
COSH
COST
COSTS
COUNT
COVAR_POP
COVAR_SAMP
CREATEDB
CREATEUSER
CREATEROLE
CSV
CUBE
CUME_DIST
CURRENT
CURRENT_CATALOG
CURRENT_DEFAULT_TRANSFORM_GROUP
CURRENT_PATH
CURRENT_ROLE
CURRENT_ROW
CURRENT_SCHEMA
CURRENT_TRANSFORM_GROUP_FOR_TYPE
CURSOR
CURSOR_NAME
CYCLE
DATA
DATABASE
DATALINK
DATASHARE
DATASHARES
DATE
DATEFORMAT
DATETIME_INTERVAL_CODE
DATETIME_INTERVAL_PRECISION
DAY
DAYOFYEAR
DB
DEALLOCATE
DEC
DECFLOAT
DECIMAL
DECLARE
DEFAULTS
DEFERRED
DEFINE
DEFINED
DEFINER
DEFLATE
DEGREE
DELETE
DELIMITED
DELIMITER
DENSE_RANK
DEPENDS
DEPTH
DEREF
DERIVED
DESCRIBE
DESCRIPTOR
DETACH
DETERMINISTIC
DIAGNOSTICS
DICTIONARY
DISCARD
DISCONNECT
DISPATCH
DISTKEY
DISTSTYLE
DLNEWCOPY
DLPREVIOUSCOPY
DLURLCOMPLETE
DLURLCOMPLETEONLY
DLURLCOMPLETEWRITE
DLURLPATH
DLURLPATHONLY
DLURLPATHWRITE
DLURLSCHEME
DLURLSERVER
DLVALUE
DOCUMENT
DOMAIN
DOUBLE
DROP
DYNAMIC
DYNAMIC_FUNCTION
DYNAMIC_FUNCTION_CODE
EACH
ELEMENT
EMPTY
ENCODE
ENCODING
ENCRYPTED
END-EXEC
END_FRAME
END_PARTITION
ENFORCED
ENUM
EPOCH
EPOCHSECS
EPOCHMILLISECS
EQUALS
ERROR
ESCAPE
EVEN
EVENT
EVERY
EXCEPTION
EXCLUDE
EXCLUDING
EXCLUSIVE
EXEC
EXECUTE
EXECUTION
EXISTS
EXP
EXPLAIN
EXPLICIT
EXPRESSION
EXTENDED
EXTENSION
EXTERNAL
EXTRACT
FAMILY
FETCH
FIELDS
FILE
FILTER
FINAL
FINALIZE
FINISH
FIRST
FIRST_VALUE
FIXEDWIDTH
FLAG
FLOAT
FLOAT4
FLOAT8
FLOOR
FOLLOWING
FORCE
FORMAT
FORTRAN
FORWARD
FOUND
FRAME_ROW
FREE
FS
FULFILL
FUNCTION
FUNCTIONS
FUSION
FUTURE
G
GB
GENERAL
GENERATED
GEOGRAPHY
GEOMETRY
GET
GLOBAL
GO
GOTO
GRANTED
GRANTS
GREATEST
GROUPING
GROUPS
GZIP
HANDLER
HASH
HEADER
HEX
HIERARCHY
HIVE
HLLSKETCH
HOLD
HOUR
HYPERPARAMETERS
IAM_ROLE
ID
IF
IMMEDIATE
IMMEDIATELY
IMMUTABLE
IMPLEMENTATION
IMPLICIT
IMPORT
IMPORTED
INCLUDE
INCLUDENEW
INCLUDING
INCREMENT
INDENT
INDEX
INDEXES
INDICATOR
INHERIT
INHERITS
INITIAL
INLINE
INOUT
INPUT
INPUTFORMAT
INSENSITIVE
INSERT
INSTANCE
INSTANTIABLE
INSTEAD
INT
INT2
INT4
INT8
INTEGER
INTEGRATION
INTEGRITY
INTERLEAVED
INTERSECTION
INTERVAL
INVOKER
ISOLATION
JSON
JSON_ARRAY
JSON_ARRAYAGG
JSON_EXISTS
JSON_OBJECT
JSON_OBJECTAGG
JSON_QUERY
JSON_TABLE
JSON_TABLE_PRIMITIVE
JSON_VALUE
K
KEEP
KEY
KEYS
KEY_MEMBER
KEY_TYPE
KINESIS
KMEANS
KMS_KEY_ID
LABEL
LAG
LANGUAGE
LARGE
LAST
LAST_VALUE
LATERAL
LEAD
LEAKPROOF
LEAST
LENGTH
LEVEL
LIBRARY
LIKE_REGEX
LINES
LINK
LIST
LISTAGG
LISTEN
LN
LOAD
LOCAL
LOCATION
LOCATOR
LOCK
LOCKED
LOG
LOG10
LOGGED
LOGIN
LOWER
LZOP
M
MAIN
MANAGE
MANIFEST
MAP
MAPPING
MASKING
MASTER_SYMMETRIC_KEY
MATCH
MATCHED
MATCHES
MATCH_NUMBER
MATCH_RECOGNIZE
MATERIALIZED
MAX
MAXERROR
MAXFILESIZE
MAXVALUE
MAX_CELLS
MAX_RUNTIME
MB
MEASURES
MEMBER
MERGE
MESSAGE_LENGTH
MESSAGE_OCTET_LENGTH
MESSAGE_TEXT
METASTORE
METHOD
MILLISECOND
MIN
MINUTE
MINVALUE
ML
MLP
MOD
MODE
MODEL
MODEL_TYPE
MODIFIES
MODIFY
MODULE
MODULUS
MONITOR
MONTH
MORE
MOVE
MULTICLASS_CLASSIFICATION
MULTISET
MYSQL
MUMPS
NAME
NAMES
NAMESPACE
NAN
NATIONAL
NCHAR
NCLOB
NESTED
NESTING
NEXT
NFC
NFD
NFKC
NFKD
NIL
NO
NOBYPASSRLS
NOCACHE
NOCREATEDB
NOCREATEROLE
NOCREATEUSER
NOCYCLE
NOINHERIT
NOLOAD
NOLOGIN
NOREPLICATION
NOSUPERUSER
NONE
NOORDER
NORMALIZE
OUTPUTFORMAT
NORMALIZED
NOTHING
NOTIFY
NOWAIT
NTH_VALUE
NTILE
NULLABLE
NULLIF
NUMBER
NUMERIC
NVARCHAR
OBJECT
OBJECTIVE
OCCURRENCES_REGEX
OCTET_LENGTH
OCTETS
OF
OFFLINE
OIDS
OMIT
ONE
OPERATE
OPERATOR
OPTION
OPTIONS
ORC
ORDERING
ORDINALITY
OTHERS
OUT
OUTPUT
OVER
OVERFLOW
OVERLAY
OVERRIDING
OVERWRITE
OWNED
OWNER
OWNERSHIP
P
PAD
PARAMETER
PARAMETER_MODE
PARAMETER_NAME
PARAMETER_ORDINAL_POSITION
PARAMETER_SPECIFIC_CATALOG
PARAMETER_SPECIFIC_NAME
PARAMETER_SPECIFIC_SCHEMA
PARQUET
PARSER
PARTIAL
PARTITIONED
PASCAL
PASS
PASSING
PASSTHROUGH
PASSWORD
PAST
PATH
PATTERN
PER
PERCENT_RANK
PERCENTILE_CONT
PERCENTILE_DISC
PERIOD
PERMISSION
PERMUTE
PIPE
PLAIN
PLAN
PLANS
PLI
POLICY
PORT
PORTION
POSITION
POSITION_REGEX
POSTGRES
POWER
PRECEDES
PRECEDING
PRECISION
PREPARE
PREPARED
PREPROCESSORS
PRESERVE
PRESET
PRIOR
PRIVATE
PRIVILEGES
PROBLEM_TYPE
PROCEDURAL
PROCEDURE
PROCEDURES
PROGRAM
PROPERTIES
PRUNE
PTF
PUBLIC
PUBLICACCESSIBLE
PUBLICATION
PLPYTHONU
QUALIFY
QUARTER
QUOTA
QUOTE
QUOTES
RANGE
RANK
RCFILE
READ
READRATIO
READS
REAL
REASSIGN
RECHECK
RECLUSTER
RECOVERY
RECURSIVE
REDSHIFT
REF
REFCURSOR
REFERENCE_USAGE
REFERENCING
REFRESH
REGION
REGR_AVGX
REGR_AVGY
REGR_COUNT
REGR_INTERCEPT
REGR_R2
REGR_SLOPE
REGR_SXX
REGR_SXY
REGR_SYY
REGRESSION
REINDEX
RELATIVE
RELEASE
REMAINDER
REMOVE
REMOVEQUOTES
RENAME
REPEATABLE
REPLACE
REPLICA
REPLICATION
REQUIRING
RESET
RESOURCE
RESTART
RESTRICT
RESTRICTED
RESULT
RETURN
RETURNED_CARDINALITY
RETURNED_LENGTH
RETURNED_OCTET_LENGTH
RETURNED_SQLSTATE
RETURNING
RETURNS
REVOKE
RLIKE
ROLE
ROLLBACK
ROLLUP
ROUNDEC
ROUTINE
ROUTINE_CATALOG
ROUTINE_NAME
ROUTINE_SCHEMA
ROUTINES
ROW
ROW_COUNT
ROW_NUMBER
ROWGROUPSIZE
ROWS
RULE
RUNNING
S3_BUCKET
S3_GARBAGE_COLLECT
SAFE
SAGEMAKER
SAVEPOINT
SCALAR
SCALE
SCHEMA
SCHEMA_NAME
SCHEMAS
SCOPE
SCOPE_CATALOG
SCOPE_NAME
SCOPE_SCHEMA
SCROLL
SEARCH
SECOND
SECRET_ACCESS_KEY
SECRET_ARN
SECTION
SECURITY
SEEK
SELECTIVE
SELF
SENSITIVE
SEPARATOR
SEQUENCE
SEQUENCEFILE
SEQUENCES
SERDE
SERDEPROPERTIES
SERIALIZABLE
SERVER
SERVER_NAME
SESSION
SESSION_TOKEN
SET
SETTINGS
SETOF
SETS
SHAPEFILE
SHARE
SHOW
SIMPLE
SIMPLIFY
SIN
SINH
SIZE
SKIP
SMALLINT
SORT
SORTKEY
SOURCE
SPACE
SPECIFIC
SPECIFIC_NAME
SPECIFICTYPE
SQL
SQLCODE
SQLERROR
SQLEXCEPTION
SQLSTATE
SQLWARNING
SQRT
STABLE
STAGE
STAGES
STANDALONE
START
STATE
STATEMENT
STATIC
STATISTICS
STATUPDATE
STDDEV_POP
STDDEV_SAMP
STDIN
STDOUT
STORAGE
STORED
STREAM
STREAMS
STRICT
STRING
STRIP
STRUCTURE
STYLE
SUBCLASS_ORIGIN
SUBMULTISET
SUBSCRIPTION
SUBSET
SUBSTRING
SUBSTRING_REGEX
SUCCEEDS
SUM
SUPER
SUPERUSER
SUPPORT
SYMMETRIC
SYSID
SYSLOG
SYSTEM_TIME
SYSTEM_USER
T
TABLE_NAME
TABLES
TABLESAMPLE
TABLESPACE
TAN
TANH
TARGET
TASK
TASKS
TB
TEMP
TEMPLATE
TEMPORARY
TERMINATED
TEXT
TEXTFILE
THROUGH
TIES
TIME
TIMEFORMAT
TIMEOUT
TIMETZ
TIMESTAMPTZ
TIMEZONE_HOUR
TIMEZONE_MINUTE
TOKEN
TOP_LEVEL_COUNT
TRANSACTION
TRANSACTION_ACTIVE
TRANSACTIONS_COMMITTED
TRANSACTIONS_ROLLED_BACK
TRANSFORM
TRANSFORMS
TRANSIENT
TRANSLATE
TRANSLATE_REGEX
TRANSLATION
TREAT
TRIGGER
TRIGGER_CATALOG
TRIGGER_NAME
TRIGGER_SCHEMA
TRIM
TRIMBLANKS
TRIM_ARRAY
TRUNCATE
TRUNCATECOLUMNS
TRUSTED
TYPE
TYPES
UESCAPE
UNBOUNDED
UNCOMMITTED
UNCONDITIONAL
UNDER
UNENCRYPTED
UNKNOWN
UNLIMITED
UNLINK
UNLISTEN
UNLOAD
UNLOGGED
UNMATCHED
UNNAMED
UNRESTRICTED
UNSAFE
UNSIGNED
UNTIL
UNTYPED
UPDATE
UPPER
URI
USE_ANY_ROLE
USAGE
USE
USER_DEFINED_TYPE_CATALOG
USER_DEFINED_TYPE_CODE
USER_DEFINED_TYPE_NAME
USER_DEFINED_TYPE_SCHEMA
UTF16
UTF16BE
UTF16LE
UTF32
UTF8
VACUUM
VALID
VALIDATE
VALIDATOR
VALUE
VALUE_OF
VALUES
VAR_POP
VAR_SAMP
VARBINARY
VARBYTE
VARCHAR
VARIADIC
VARYING
VERSION
VERSIONING
VIEW
VIEWS
VOLATILE
WALLET
WAREHOUSE
WEEK
WEEKDAY
WHENEVER
WHITESPACE
WIDTH_BUCKET
WINDOW
WORK
WRAPPER
WRITE
XGBOOST
XML
XMLAGG
XMLATTRIBUTES
XMLBINARY
XMLCAST
XMLCOMMENT
XMLCONCAT
XMLDECLARATION
XMLDOCUMENT
XMLELEMENT
XMLEXISTS
XMLFOREST
XMLITERATE
XMLNAMESPACES
XMLPARSE
XMLPI
XMLQUERY
XMLROOT
XMLSCHEMA
XMLSERIALIZE
XMLTABLE
XMLTEXT
XMLVALIDATE
YAML
YEAR
YES
ZONE
ZSTD"""

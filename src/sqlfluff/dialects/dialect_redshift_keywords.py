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
BACKUP
BETWEEN
BINARY
BLANKSASNULL
BOTH
BYTEDICT
BZIP2
CASE
CAST
CHECK
COLLATE
COLUMN
COMPOUND
CONSTRAINT
CREATE
CREDENTIALS
CROSS
CURRENT_DATE
CURRENT_TIME
CURRENT_TIMESTAMP
CURRENT_USER
CURRENT_USER_ID
DEFAULT
DEFAULTS
DEFERRABLE
DEFLATE
DEFRAG
DELTA
DELTA32K
DESC
DISABLE
DISTINCT
DISTKEY
DISTSTYLE
DO
ELSE
EMPTYASNULL
ENABLE
ENCODE
ENCRYPT
ENCRYPTION
END
EXCEPT
EXCLUDING
EXPLICIT
FALSE
FOR
FOREIGN
FREEZE
FROM
FULL
GLOBALDICT256
GLOBALDICT64K
GRANT
GROUP
GZIP
HAVING
IDENTITY
IGNORE
ILIKE
IN
INCLUDING
INITIALLY
INNER
INTERLEAVED
INTERSECT
INTO
IS
ISNULL
JOIN
LANGUAGE
LEADING
LEFT
LIKE
LIMIT
LOCALTIME
LOCALTIMESTAMP
LUN
LUNS
LZO
LZOP
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
OFFLINE
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
SORTKEY
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
USER
USING
VERBOSE
WALLET
WHEN
WHERE
WITH
WITHOUT
ZSTD"""

redshift_unreserved_keywords = """A
ABORT
ABS
ABSENT
ABSOLUTE
ACCESS
ACCORDING
ACCOUNT
ACOS
ACTION
ADA
ADD
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
AVG
BACKUP
BACKWARD
BASE64
BEFORE
BEGIN
BEGIN_FRAME
BEGIN_PARTITION
BERNOULLI
BIGINT
BINDING
BIT
BIT_LENGTH
BLOB
BLOCKED
BOM
BOOLEAN
BREADTH
BUFFERS
BY
C
CACHE
CALL
CALLED
CARDINALITY
CASCADE
CASCADED
CATALOG
CATALOG_NAME
CEIL
CEILING
CHAIN
CHAINING
CHAR
CHAR_LENGTH
CHARACTER
CHARACTER_LENGTH
CHARACTER_SET_CATALOG
CHARACTER_SET_NAME
CHARACTER_SET_SCHEMA
CHARACTERISTICS
CHARACTERS
CHECKPOINT
CLASS
CLASS_ORIGIN
CLASSIFIER
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
COLUMN_NAME
COLUMNS
COMMAND_FUNCTION
COMMAND_FUNCTION_CODE
COMMENT
COMMENTS
COMMIT
COMMITTED
CONCURRENTLY
CONDITION
CONDITION_NUMBER
CONDITIONAL
CONFIGURATION
CONFLICT
CONNECT
CONNECTION
CONNECTION_NAME
CONSTRAINT_CATALOG
CONSTRAINT_NAME
CONSTRAINT_SCHEMA
CONSTRAINTS
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
DATE
DATEADD
DATEDIFF
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
DEGREE
DELETE
DELIMITER
DELIMITERS
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
ENCODING
ENCRYPTED
END_FRAME
END_PARTITION
END-EXEC
ENFORCED
ENUM
EPOCH
EQUALS
ERROR
ESCAPE
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
EXPRESSION
EXTENDED
EXTENSION
EXTERNAL
EXTRACT
FAMILY
FETCH
FILE
FILTER
FINAL
FINALIZE
FINISH
FIRST
FIRST_VALUE
FLAG
FLOAT
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
GENERAL
GENERATED
GET
GLOBAL
GO
GOTO
GRANTED
GRANTS
GREATEST
GROUPING
GROUPS
HANDLER
HASH
HEADER
HEX
HIERARCHY
HOLD
HOUR
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
INSENSITIVE
INSERT
INSTANCE
INSTANTIABLE
INSTEAD
INT
INTEGER
INTEGRATION
INTEGRITY
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
KEY_MEMBER
KEY_TYPE
KEYS
LABEL
LAG
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
LOWER
M
MAIN
MANAGE
MAP
MAPPING
MASKING
MATCH
MATCH_NUMBER
MATCH_RECOGNIZE
MATCHED
MATCHES
MATERIALIZED
MAX
MAXVALUE
MEASURES
MEMBER
MERGE
MESSAGE_LENGTH
MESSAGE_OCTET_LENGTH
MESSAGE_TEXT
METHOD
MILLISECOND
MIN
MINUTE
MINVALUE
ML
MOD
MODE
MODEL
MODIFIES
MODIFY
MODULE
MODULUS
MONITOR
MONTH
MORE
MOVE
MULTISET
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
NOCACHE
NOCYCLE
NONE
NOORDER
NORMALIZE
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
OBJECT
OCCURRENCES_REGEX
OCTET_LENGTH
OCTETS
OF
OIDS
OMIT
ONE
OPERATE
OPERATOR
OPTION
OPTIONS
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
PARSER
PARTIAL
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
PORTION
POSITION
POSITION_REGEX
POWER
PRECEDES
PRECEDING
PRECISION
PREPARE
PREPARED
PRESERVE
PRIOR
PRIVATE
PRIVILEGES
PROCEDURAL
PROCEDURE
PROCEDURES
PROGRAM
PRUNE
PTF
PUBLIC
PUBLICATION
QUALIFY
QUARTER
QUOTE
QUOTES
RANGE
RANK
READ
READS
REAL
REASSIGN
RECHECK
RECOVERY
RECURSIVE
REF
REFERENCING
REFRESH
REGR_AVGX
REGR_AVGY
REGR_COUNT
REGR_INTERCEPT
REGR_R2
REGR_SLOPE
REGR_SXX
REGR_SXY
REGR_SYY
REINDEX
RELATIVE
RELEASE
REMAINDER
RENAME
REPEATABLE
REPLACE
REPLICA
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
ROUTINE
ROUTINE_CATALOG
ROUTINE_NAME
ROUTINE_SCHEMA
ROUTINES
ROW
ROW_COUNT
ROW_NUMBER
ROWS
RULE
RUNNING
SAFE
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
SECTION
SECURITY
SEEK
SELECTIVE
SELF
SENSITIVE
SEPARATOR
SEQUENCE
SEQUENCES
SERIALIZABLE
SERVER
SERVER_NAME
SESSION
SET
SETOF
SETS
SHARE
SHOW
SIMPLE
SIN
SINH
SIZE
SKIP
SMALLINT
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
STANDALONE
START
STATE
STATEMENT
STATIC
STATISTICS
STDDEV_POP
STDDEV_SAMP
STDIN
STDOUT
STORAGE
STORED
STREAM
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
SUPPORT
SYMMETRIC
SYSID
SYSTEM_TIME
SYSTEM_USER
T
TABLE_NAME
TABLES
TABLESAMPLE
TABLESPACE
TAN
TANH
TASK
TEMP
TEMPLATE
TEMPORARY
TEXT
THROUGH
TIES
TIME
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
TRIM_ARRAY
TRUNCATE
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
UNLINK
UNLISTEN
UNLOGGED
UNMATCHED
UNNAMED
UNNEST
UNSAFE
UNSIGNED
UNTIL
UNTYPED
UPDATE
UPPER
URI
USAGE
USE
USER_DEFINED_TYPE_CATALOG
USER_DEFINED_TYPE_CODE
USER_DEFINED_TYPE_NAME
USER_DEFINED_TYPE_SCHEMA
UTF16
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
VARCHAR
VARIADIC
VARYING
VERSION
VERSIONING
VIEW
VIEWS
VOLATILE
WAREHOUSE
WEEK
WEEKDAY
WHENEVER
WHITESPACE
WIDTH_BUCKET
WINDOW
WITHIN
WITHOUT
WORK
WRAPPER
WRITE
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
ZONE"""

"""A list of all Snowflake SQL key words."""

snowflake_reserved_keywords = """ALL
ALTER
AND
ANY
AS
BETWEEN
BY
CASE
CAST
CHECK
CONNECT
CONNECTION
CONSTRAINT
CREATE
CROSS
CURRENT
CURRENT_DATE
CURRENT_TIME
CURRENT_TIMESTAMP
CURRENT_USER
DATABASE
DELETE
DISTINCT
DROP
ELSE
EXISTS
FOLLOWING
FOR
FROM
FULL
GRANT
GROUP
GSCLUSTER
HAVING
ILIKE
IN
INCREMENT
INNER
INSERT
INSERT_ONLY
INTERSECT
INTO
IS
ISSUE
JOIN
LATERAL
LEFT
LIKE
LOCALTIME
LOCALTIMESTAMP
MATCH_RECOGNIZE
MINUS
NATURAL
NOT
NULL
OF
ON
OR
ORDER
PARTITION
QUALIFY
REGEXP
REVOKE
RIGHT
RLIKE
ROW
ROWS
SAMPLE
SCHEMA
SELECT
SET
SOME
START
STRICT
TABLE
TABLESAMPLE
THEN
TO
TRIGGER
TRY_CAST
UNION
UNIQUE
UPDATE
UNPIVOT
USING
VALUES
WHEN
WHENEVER
WHERE
WITH
"""

snowflake_unreserved_keywords = """ABORT
ABORT_STATEMENT
ACCESS
ACCOUNT
ACCOUNTS
ADD
ADMIN
AFTER
ALLOW_OVERLAPPING_EXECUTION
API
API_INTEGRATION
APPEND_ONLY
APPLY
ARRAY
ASC
AT
AUTHORIZATION
AUTHORIZATIONS
AUTO
AUTO_INCREMENT
AUTO_INGEST
AUTO_REFRESH
AUTO_RESUME
AUTO_SUSPEND
AUTOINCREMENT
AVRO
AWS_KEY_ID
AWS_ROLE
AWS_SECRET_KEY
AWS_SNS_TOPIC
AWS_TOKEN
AZURE
AZURE_SAS_TOKEN
AZURE_TENANT_ID
BEFORE
BEGIN
BERNOULLI
BINARY
BINDING
BLOCK
CACHE
CALL
CALLED
CALLER
CASCADE
CASE_INSENSITIVE
CASE_SENSITIVE
CHAIN
CHANGE_TRACKING
CHANGES
CHARACTER
CLONE
CLUSTER
CLUSTERING
COLLATE
COLUMN
COLUMNS
COMMENT
COMMIT
COMPRESSION
CONCURRENTLY
CONNECT_BY_ROOT
CONTEXT_HEADERS
CONTINUE
COPY
COPY_OPTIONS
CREDENTIALS
CSV
CUBE
CURRENT_ACCOUNT
CURRENT_CLIENT
CURRENT_DATABASE
CURRENT_IP_ADDRESS
CURRENT_REGION
CURRENT_ROLE
CURRENT_SCHEMA
CURRENT_SCHEMAS
CURRENT_SESSION
CURRENT_STATEMENT
CURRENT_TRANSACTION
CURRENT_VERSION
CURRENT_WAREHOUSE
CYCLE
DATA
DATA_RETENTION_TIME_IN_DAYS
DATABASES
DATE
DEFAULT
DEFAULT_DDL_COLLATION
DEFERRABLE
DEFERRED
DEFINE
DEFLATE
DELEGATED
DESC
DESCRIBE
DIRECTORY
DISABLE
DOMAIN
DOUBLE
ECONOMY
EMPTY
ENABLE
ENABLED
ENCRYPTION
END
ENFORCE_LENGTH
ENFORCED
ENUM
ESCAPE
EXCEPT
EXECUTE
EXECUTION
EXPLAIN
EXTENSION
EXTERNAL
EXTERNAL_STAGE
FETCH
FILE
FILE_FORMAT
FILES
FILTER
FINAL
FIRST
FORCE
FOREIGN
FORMAT
FORMAT_NAME
FORMATS
FUNCTION
FUNCTIONS
FUTURE
GCS
GLOBAL
GRANTED
GRANTS
GROUPING
GZIP
HEADERS
HISTORY
IDENTITY
IF
IGNORE
IMMEDIATE
IMMUTABLE
IMPORTED
INDEX
INITIALLY
INITIALLY_SUSPENDED
INFORMATION
INPUT
INTEGRATION
INTEGRATIONS
INTERVAL
JAVASCRIPT
JSON
KEY
KMS_KEY_ID
LANGUAGE
LARGE
LAST
LAST_QUERY_ID
LAST_TRANSACTION
LIMIT
LOCAL
LOCATION
LOCKS
M
MANAGE
MANAGED
MASKING
MASTER_KEY
MATCH
MATCH_BY_COLUMN_NAME
MATCHED
MATCHES
MATERIALIZED
MAX_BATCH_ROWS
MAX_CLUSTER_COUNT
MAX_CONCURRENCY_LEVEL
MAX_DATA_EXTENSION_TIME_IN_DAYS
MAX_SIZE
MAXVALUE
MEASURES
MERGE
MIN_CLUSTER_COUNT
MINVALUE
ML
MODEL
MODIFY
MONITOR
NAME
NAN
NETWORK
NEXT
NEXTVAL
NO
NOCACHE
NOCYCLE
NONE
NOORDER
NOTIFICATION
NOTIFICATION_INTEGRATION
NULLS
OBJECT
OBJECTS
OFFSET
OMIT
ON_ERROR
ONE
ONLY
OPERATE
OPTIMIZATION
OPTION
OPTIONS
ORC
ORGANIZATION
OUTER
OVER
OVERLAPS
OVERWRITE
OWNER
OWNERSHIP
PARAMETERS
PARQUET
PASSWORD
PAST
PATTERN
PER
PERMUTE
PIPE
PIPES
PIVOT
POLICIES
POLICY
PRECEDING
PRECISION
PRIMARY
PRIOR
PRIVILEGES
PROCEDURE
PROCEDURES
PUBLIC
PURGE
QUERIES
RANGE
READ
RECLUSTER
RECURSIVE
REFERENCE_USAGE
REFERENCES
REFRESH
REFRESH_ON_CREATE
REGIONS
REMOVE
RENAME
REPEATABLE
REPLACE
REPLICATION
RESET
RESOURCE
RESOURCE_MONITOR
RESPECT
RESPONSE_TRANSLATOR
RESTRICT
RESULT
RESUME
RETURN_ALL_ERRORS
RETURN_ERRORS
RETURN_FAILED_ONLY
RETURNS
RM
ROLE
ROLES
ROLLBACK
ROLLUP
ROUTINE
ROUTINES
REQUEST_TRANSLATOR
RUNNING
S3
SCALING_POLICY
SCHEDULE
SCHEMAS
SEARCH
SECONDARY
SECURE
SECURITY
SEED
SEPARATOR
SEQUENCE
SEQUENCES
SERVER
SESSION
SESSION_USER
SETS
SHARE
SHARES
SHOW
SHOW_INITIAL_ROWS
SIZE_LIMIT
SKIP
SKIP_FILE
SNOWFLAKE_FULL
SNOWFLAKE_SSE
SQL
STAGE
STAGE_COPY_OPTIONS
STAGE_FILE_FORMAT
STAGES
STANDARD
STARTS
STATEMENT
STATEMENT_QUEUED_TIMEOUT_IN_SECONDS
STATEMENT_TIMEOUT_IN_SECONDS
STORAGE
STORAGE_ALLOWED_LOCATIONS
STORAGE_AWS_OBJECT_ACL
STORAGE_AWS_ROLE_ARN
STORAGE_BLOCKED_LOCATIONS
STORAGE_INTEGRATION
STORAGE_PROVIDER
STREAM
STREAMS
SUBPATH
SUSPEND
SUSPENDED
SWAP
SYSDATE
SYSTEM
TABLES
TABLESPACE
TABULAR
TAG
TASK
TASKS
TEMP
TEMPLATE
TEMPORARY
TERSE
TEXT
TIME
TIMESTAMP
TOP
TRANSACTION
TRANSACTIONS
TRANSIENT
TRUNCATE
TRUNCATECOLUMNS
TYPE
UNBOUNDED
UNDROP
UNMATCHED
UNSET
UNSIGNED
URL
US
USAGE
USE
USE_ANY_ROLE
USER
USER_TASK_MANAGED_INITIAL_WAREHOUSE_SIZE
USER_TASK_TIMEOUT_MS
USERS
VALIDATION_MODE
VALUE
VARIABLES
VARIANT
VARYING
VERSION
VIEW
VIEWS
VOLATILE
WAIT_FOR_COMPLETION
WAREHOUSE
WAREHOUSE_SIZE
WAREHOUSES
WINDOW
WITH
WITHIN
WITHOUT
WORK
WOY
WRAPPER
WRITE
XML
ZONE"""

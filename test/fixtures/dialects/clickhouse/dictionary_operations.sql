-- Basic dictionary creation
-- Basic dictionary with minimal configuration
CREATE DICTIONARY simple_dict (id Int64)
PRIMARY KEY id
SOURCE (CLICKHOUSE (HOST 'localhost'))
LIFETIME (300)
LAYOUT (FLAT());

-- Dictionary with explicit cluster name
CREATE DICTIONARY cluster_dict ON CLUSTER cluster_name (id Int64)
PRIMARY KEY id
SOURCE (CLICKHOUSE (HOST 'localhost'))
LIFETIME (300)
LAYOUT (FLAT());

-- Dictionary with cluster placeholder
CREATE DICTIONARY placeholder_dict ON CLUSTER '{cluster}' (id Int64)
PRIMARY KEY id
SOURCE (CLICKHOUSE (HOST 'localhost'))
LIFETIME (300)
LAYOUT (FLAT());

-- Dictionary with OR REPLACE clause
CREATE OR REPLACE DICTIONARY replaceable_dict (id Int64)
PRIMARY KEY id
SOURCE (CLICKHOUSE (HOST 'localhost'))
LIFETIME (300)
LAYOUT (FLAT());

-- Dictionary with full ClickHouse source configuration including query
CREATE DICTIONARY IF NOT EXISTS full_config_dict (
    key_column UInt64 DEFAULT 0,
    second_column String DEFAULT 'default_value'
)
PRIMARY KEY key_column
SOURCE (CLICKHOUSE (
    HOST 'localhost'
    PORT 9000
    USER 'default'
    PASSWORD ''
    DB 'default'
    TABLE 'source_table'
    WHERE 'id=10'
    SECURE 1
    QUERY 'SELECT id, value_1, value_2 FROM source_table'
))
LIFETIME(MIN 1 MAX 10)
LAYOUT(HASHED());

-- Dictionary with FILE source and settings
CREATE DICTIONARY file_dict (id Int64)
PRIMARY KEY id
SOURCE(FILE(
    path './data/source.tsv'
    format 'TabSeparated'
))
SETTINGS(format_csv_allow_single_quotes = 0)
LIFETIME(300)
LAYOUT(FLAT());

-- Dictionary with HTTP source including authentication
CREATE DICTIONARY http_dict (id Int64)
PRIMARY KEY id
SOURCE(HTTP(
    url 'http://api.example.com/data.tsv'
    format 'TabSeparated'
    credentials(user 'api_user' password 'api_password')
    headers(header(name 'API-KEY' value 'secret_key'))
))
LIFETIME(300)
LAYOUT(FLAT());

-- Dictionary with ODBC source and query
CREATE DICTIONARY odbc_dict (id Int64)
PRIMARY KEY id
SOURCE(ODBC(
    db 'ExternalDB'
    table 'Schema.Table'
    connection_string 'DSN=external_source'
    invalidate_query 'SELECT MAX(updated_at) FROM Schema.Table'
    query 'SELECT id, value_1, value_2 FROM Schema.Table'
))
LIFETIME(300)
LAYOUT(FLAT());

-- Dictionary with MySQL source and replicas
CREATE DICTIONARY mysql_dict (id Int64)
PRIMARY KEY id
SOURCE(MYSQL(
    port 3306
    user 'replication_user'
    password 'secret'
    replica(host 'replica-1' priority 1)
    replica(host 'replica-2' priority 1)
    db 'source_db'
    table 'source_table'
    where 'active=1'
    invalidate_query 'SELECT MAX(updated_at) FROM source_table'
    fail_on_connection_loss 'true'
    query 'SELECT id, value_1, value_2 FROM source_table'
))
LIFETIME(300)
LAYOUT(FLAT());

-- Dictionary with MongoDB source
CREATE DICTIONARY dict8 (id Int64)
PRIMARY KEY id
SOURCE(MONGODB(
    host 'localhost'
    port 27017
    user ''
    password ''
    db 'test'
    collection 'dictionary_source'
    options 'ssl=true'
))
LIFETIME(300)
LAYOUT(FLAT());

-- Dictionary with Redis source
CREATE DICTIONARY dict9 (id Int64)
PRIMARY KEY id
SOURCE(REDIS(
    host 'localhost'
    port 6379
    storage_type 'simple'
    db_index 0
))
LIFETIME(300)
LAYOUT(FLAT());

-- Dictionary with PostgreSQL source
CREATE DICTIONARY dict10 (id Int64)
PRIMARY KEY id
SOURCE(POSTGRESQL(
    port 5432
    host 'postgresql-hostname'
    user 'postgres_user'
    password 'postgres_password'
    db 'db_name'
    table 'table_name'
    replica(host 'example01-1' port 5432 priority 1)
    replica(host 'example01-2' port 5432 priority 2)
    where 'id=10'
    invalidate_query 'SQL_QUERY'
    query 'SELECT id, value_1, value_2 FROM db_name.table_name'
))
LIFETIME(300)
LAYOUT(FLAT());

-- Dictionary with NULL source
CREATE DICTIONARY dict11 (id Int64)
PRIMARY KEY id
SOURCE(NULL())
LIFETIME(300)
LAYOUT(FLAT());

-- Test all layout types

-- FLAT layout
CREATE DICTIONARY flat_dict
(
    key_field String,
    value_field UInt64
)
PRIMARY KEY key_field
SOURCE(CLICKHOUSE(HOST 'localhost' PORT 9000 USER 'default' PASSWORD '' DB 'db' TABLE 'table'))
LIFETIME(MIN 1 MAX 10)
LAYOUT(FLAT(INITIAL_ARRAY_SIZE 50000 MAX_ARRAY_SIZE 5000000));

-- HASHED layout
CREATE DICTIONARY hashed_dict
(
    key_field String,
    value_field UInt64
)
PRIMARY KEY key_field
SOURCE(CLICKHOUSE(HOST 'localhost' PORT 9000 USER 'default' PASSWORD '' DB 'db' TABLE 'table'))
LIFETIME(MIN 1 MAX 10)
LAYOUT(HASHED(SHARDS 1 SHARD_LOAD_QUEUE_BACKLOG 10000 MAX_LOAD_FACTOR 0.5));

-- SPARSE_HASHED layout
CREATE DICTIONARY sparse_hashed_dict
(
    key_field String,
    value_field UInt64
)
PRIMARY KEY key_field
SOURCE(CLICKHOUSE(HOST 'localhost' PORT 9000 USER 'default' PASSWORD '' DB 'db' TABLE 'table'))
LIFETIME(MIN 1 MAX 10)
LAYOUT(SPARSE_HASHED(SHARDS 1 SHARD_LOAD_QUEUE_BACKLOG 10000 MAX_LOAD_FACTOR 0.5));

-- COMPLEX_KEY_HASHED layout
CREATE DICTIONARY complex_key_hashed_dict
(
    key1 String,
    key2 UInt64,
    value_field UInt64
)
PRIMARY KEY (key1, key2)
SOURCE(CLICKHOUSE(
    HOST 'localhost'
    PORT 9000
    USER 'default'
    PASSWORD ''
    DB 'db'
    TABLE 'table'
))
LIFETIME(MIN 1 MAX 10)
LAYOUT(COMPLEX_KEY_HASHED());

-- COMPLEX_KEY_SPARSE_HASHED layout
CREATE DICTIONARY complex_key_sparse_hashed_dict
(
    key_field String,
    value_field UInt64
)
PRIMARY KEY key_field
SOURCE(CLICKHOUSE(HOST 'localhost' PORT 9000 USER 'default' PASSWORD '' DB 'db' TABLE 'table'))
LIFETIME(MIN 1 MAX 10)
LAYOUT(COMPLEX_KEY_SPARSE_HASHED(SHARDS 1 SHARD_LOAD_QUEUE_BACKLOG 10000 MAX_LOAD_FACTOR 0.5));

-- HASHED_ARRAY layout
CREATE DICTIONARY hashed_array_dict
(
    key_field String,
    value_field UInt64
)
PRIMARY KEY key_field
SOURCE(CLICKHOUSE(HOST 'localhost' PORT 9000 USER 'default' PASSWORD '' DB 'db' TABLE 'table'))
LIFETIME(MIN 1 MAX 10)
LAYOUT(HASHED_ARRAY(SHARDS 1));

-- COMPLEX_KEY_HASHED_ARRAY layout
CREATE DICTIONARY complex_key_hashed_array_dict
(
    key_field String,
    value_field UInt64
)
PRIMARY KEY key_field
SOURCE(CLICKHOUSE(HOST 'localhost' PORT 9000 USER 'default' PASSWORD '' DB 'db' TABLE 'table'))
LIFETIME(MIN 1 MAX 10)
LAYOUT(COMPLEX_KEY_HASHED_ARRAY(SHARDS 1));

-- RANGE_HASHED layout with max strategy
CREATE DICTIONARY range_hashed_max_dict
(
    key_field UInt64,
    range_start Date,
    range_end Date,
    value_field UInt64
)
PRIMARY KEY key_field
SOURCE(CLICKHOUSE(
    HOST 'localhost'
    PORT 9000
    USER 'default'
    PASSWORD ''
    DB 'db'
    TABLE 'table'
))
LIFETIME(MIN 1 MAX 10)
LAYOUT(RANGE_HASHED(RANGE_LOOKUP_STRATEGY 'max'))
RANGE(MIN range_start MAX range_end);


-- COMPLEX_KEY_RANGE_HASHED layout
CREATE DICTIONARY complex_key_range_hashed_dict
(
    key_field String,
    value_field UInt64
)
PRIMARY KEY key_field
SOURCE(CLICKHOUSE(HOST 'localhost' PORT 9000 USER 'default' PASSWORD '' DB 'db' TABLE 'table'))
LIFETIME(MIN 1 MAX 10)
LAYOUT(COMPLEX_KEY_RANGE_HASHED());

-- CACHE layout
CREATE DICTIONARY cache_dict
(
    key_field String,
    value_field UInt64
)
PRIMARY KEY key_field
SOURCE(CLICKHOUSE(HOST 'localhost' PORT 9000 USER 'default' PASSWORD '' DB 'db' TABLE 'table'))
LIFETIME(MIN 1 MAX 10)
LAYOUT(CACHE(SIZE_IN_CELLS 1000000000));

-- SSD_CACHE layout
CREATE DICTIONARY ssd_cache_dict
(
    key_field String,
    value_field UInt64
)
PRIMARY KEY key_field
SOURCE(CLICKHOUSE(HOST 'localhost' PORT 9000 USER 'default' PASSWORD '' DB 'db' TABLE 'table'))
LIFETIME(MIN 1 MAX 10)
LAYOUT(SSD_CACHE(
    BLOCK_SIZE 4096,
    FILE_SIZE 16777216,
    READ_BUFFER_SIZE 1048576,
    PATH '/var/lib/clickhouse/user_files/test_dict'
));

-- DIRECT layout
CREATE DICTIONARY direct_dict
(
    key_field String,
    value_field UInt64
)
PRIMARY KEY key_field
SOURCE(CLICKHOUSE(HOST 'localhost' PORT 9000 USER 'default' PASSWORD '' DB 'db' TABLE 'table'))
LAYOUT(DIRECT());

-- IP_TRIE layout
CREATE DICTIONARY ip_trie_dict
(
    key_field IPv4,
    value_field UInt64
)
PRIMARY KEY key_field
SOURCE(CLICKHOUSE(
    HOST 'localhost'
    PORT 9000
    USER 'default'
    PASSWORD ''
    DB 'db'
    TABLE 'table'
))
LIFETIME(MIN 1 MAX 10)
LAYOUT(IP_TRIE());


CREATE DICTIONARY id_value_dictionary
(
    id UInt64,
    value String
)
PRIMARY KEY id
SOURCE(CLICKHOUSE(TABLE 'source_table'))
LAYOUT(FLAT())
LIFETIME(MIN 0 MAX 1000);

CREATE DICTIONARY foo_db.id_value_dictionary
(
    id UInt64,
    value String
)
PRIMARY KEY id
SOURCE(CLICKHOUSE(
    TABLE 'source_table'
    USER 'clickhouse_admin'
    PASSWORD 'passworD43$x'
    DB 'foo_db'
))
LAYOUT(FLAT())
LIFETIME(MIN 0 MAX 1000);

CREATE DICTIONARY default.taxi_zone_dictionary
(
    `LocationID` UInt16 DEFAULT 0,
    `Borough` String,
    `Zone` String,
    `service_zone` String
)
PRIMARY KEY LocationID
SOURCE(HTTP(URL 'https://datasets-documentation.s3.eu-west-3.amazonaws.com/nyc-taxi/taxi_zone_lookup.csv' FORMAT 'CSVWithNames'))
LIFETIME(MIN 0 MAX 0)
LAYOUT(HASHED());

CREATE DICTIONARY discounts_dict (
    advertiser_id UInt64,
    discount_start_date Date,
    discount_end_date Date,
    amount Float64
)
PRIMARY KEY id
SOURCE(CLICKHOUSE(TABLE 'discounts'))
LIFETIME(MIN 1 MAX 1000)
LAYOUT(RANGE_HASHED(range_lookup_strategy 'max'))
RANGE(MIN discount_start_date MAX discount_end_date);

CREATE DICTIONARY range_dictionary
(
  CountryID UInt64,
  CountryKey String,
  StartDate Date,
  EndDate Date,
  Tax Float64 DEFAULT 0.2
)
PRIMARY KEY CountryID, CountryKey
SOURCE(CLICKHOUSE(TABLE 'date_table'))
LIFETIME(MIN 1 MAX 1000)
LAYOUT(COMPLEX_KEY_RANGE_HASHED())
RANGE(MIN StartDate MAX EndDate);

CREATE DICTIONARY range_dictionary ON CLUSTER '{cluster_name}'
(
  CountryID UInt64,
  CountryKey String,
  StartDate Date,
  EndDate Date,
  Tax Float64 DEFAULT 0.2
)
PRIMARY KEY CountryID, CountryKey
SOURCE(CLICKHOUSE(TABLE 'date_table'))
LIFETIME(MIN 1 MAX 1000)
LAYOUT(COMPLEX_KEY_RANGE_HASHED())
RANGE(MIN StartDate MAX EndDate);

CREATE DICTIONARY my_ip_trie_dictionary (
    prefix String,
    asn UInt32,
    cca2 String DEFAULT '??'
)
PRIMARY KEY prefix
SOURCE(CLICKHOUSE(TABLE 'my_ip_addresses'))
LAYOUT(IP_TRIE)
LIFETIME(3600);

CREATE DICTIONARY table_name (
    id UInt64,
    some_column UInt64 DEFAULT 0
)
PRIMARY KEY id
SOURCE(ODBC(connection_string 'DSN=myconnection' table 'postgresql_table'))
LAYOUT(HASHED())
LIFETIME(MIN 300 MAX 360);

CREATE DICTIONARY polygons_test_dictionary
(
    key Array(Array(Array(Tuple(Float64, Float64)))),
    name String
)
PRIMARY KEY key
SOURCE(CLICKHOUSE(TABLE 'polygons_test_table'))
LAYOUT(POLYGON(STORE_POLYGON_KEY_COLUMN 1))
LIFETIME(0);

CREATE DICTIONARY dictionary_with_comment
(
    id UInt64,
    value String
)
PRIMARY KEY id
SOURCE(CLICKHOUSE(TABLE 'source_table'))
LAYOUT(FLAT())
LIFETIME(MIN 0 MAX 1000)
COMMENT 'The temporary dictionary';

CREATE DICTIONARY votes_dict
(
  `PostId` UInt64,
  `UpVotes` UInt32,
  `DownVotes` UInt32
)
PRIMARY KEY PostId
SOURCE(CLICKHOUSE(QUERY 'SELECT PostId, countIf(VoteTypeId = 2) AS UpVotes, countIf(VoteTypeId = 3) AS DownVotes FROM votes GROUP BY PostId'))
LIFETIME(MIN 600 MAX 900)
LAYOUT(HASHED());

CREATE DICTIONARY users_dict
(
  `Id` Int32,
  `Location` String
)
PRIMARY KEY Id
SOURCE(CLICKHOUSE(QUERY 'SELECT Id, Location FROM stackoverflow.users'))
LIFETIME(MIN 600 MAX 900)
LAYOUT(HASHED());

CREATE DICTIONARY users_dict
(
    `Id` UInt64,
    `Location` String
)
PRIMARY KEY Id
SOURCE(CLICKHOUSE(QUERY 'SELECT Id, Location FROM users WHERE Id >= 0'))
LIFETIME(MIN 600 MAX 900)
LAYOUT(HASHED());

CREATE DICTIONARY stations_dict
(
 `station_id` String,
 `state` String,
 `country_code` String,
 `name` String,
 `lat` Float64,
 `lon` Float64,
 `elevation` Float32
)
PRIMARY KEY station_id
SOURCE(CLICKHOUSE(TABLE 'stations'))
LIFETIME(MIN 0 MAX 0)
LAYOUT(complex_key_hashed_array());

-- Dictionary with update field and complex key hashed layout
CREATE OR REPLACE DICTIONARY dict_complex_key ON CLUSTER '{cluster}'
(
    `key` String,
    `valid_from` DateTime64(3),
    `valid_to` DateTime64(3),
    `amount` Float64,
    `modified_at` DateTime64(3)
)
PRIMARY KEY key
SOURCE(CLICKHOUSE(
      update_field modified_at
      QUERY 'SELECT * FROM data_table'
      ))
LIFETIME(MIN 0 MAX 1000)
LAYOUT(COMPLEX_KEY_HASHED());

-- Dictionary with range lookup and update field
CREATE OR REPLACE DICTIONARY dict_range_lookup ON CLUSTER '{cluster}'
(
    `key` String,
    `valid_from` DateTime64(3),
    `valid_to` DateTime64(3),
    `amount` Float64,
    `modified_at` DateTime64(3)
)
PRIMARY KEY key
SOURCE(CLICKHOUSE(
        UPDATE_FIELD modified_at
        QUERY 'SELECT * FROM data_table'
      ))
LIFETIME(MIN 0 MAX 1000)
LAYOUT(RANGE_HASHED())
RANGE(MIN valid_from MAX valid_to);

-- Dictionary with range lookup and short lifetime
CREATE OR REPLACE DICTIONARY dict_short_lifetime ON CLUSTER '{cluster}'
(
    `key` String,
    `valid_from` DateTime64(3),
    `valid_to` DateTime64(3),
    `amount` Float64,
    `modified_at` DateTime64(3)
)
PRIMARY KEY key
SOURCE(CLICKHOUSE(
        QUERY 'SELECT * FROM data_table'
      ))
LIFETIME(MIN 60 MAX 300)
LAYOUT(RANGE_HASHED())
RANGE(MIN start_time MAX end_time);

-- Dictionary with update field and complex key hashed layout
CREATE OR REPLACE DICTIONARY dict_update_field ON CLUSTER '{cluster}'
(
    `key` String,
    `key2` String,
    `valid_from` DateTime64(3),
    `valid_to` DateTime64(3),
    `amount` Float64,
    `modified_at` DateTime64(3)
)
PRIMARY KEY key, key2
SOURCE(CLICKHOUSE(
      update_field modified_at
      QUERY 'SELECT * FROM data_table'
      ))
LIFETIME(MIN 0 MAX 1000)
LAYOUT(COMPLEX_KEY_HASHED());

-- Dictionary with range lookup and update field
CREATE OR REPLACE DICTIONARY dict_range_lookup ON CLUSTER '{cluster}'
(
    `key` String,
    `valid_from` DateTime64(3),
    `valid_to` DateTime64(3),
    `amount` Float64,
    `modified_at` DateTime64(3)
)
PRIMARY KEY key
SOURCE(CLICKHOUSE(
        UPDATE_FIELD modified_at
        QUERY 'SELECT * FROM data_table'
      ))
LIFETIME(MIN 0 MAX 1000)
LAYOUT(RANGE_HASHED())
RANGE(MIN valid_from MAX valid_to);

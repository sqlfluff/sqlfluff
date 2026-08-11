create table example1
(
    a String,
    b String
)
engine = MergeTree()
order by (a, b);

CREATE TABLE table_name
(
    u64 UInt64,
    i32 Int32,
    s String
)
ENGINE = MergeTree()
ORDER BY (CounterID, EventDate)
PARTITION BY toYYYYMM(EventDate)
SETTINGS index_granularity=8192;

CREATE TABLE WatchLog_old(date Date, UserId Int64, EventType String, Cnt UInt64)
    ENGINE=MergeTree(date, (UserId, EventType), 8192);

CREATE TABLE WatchLog_new(date Date, UserId Int64, EventType String, Cnt UInt64)
    ENGINE=MergeTree PARTITION BY date ORDER BY (UserId, EventType) SETTINGS index_granularity=8192;

CREATE TABLE WatchLog as WatchLog_old ENGINE=Merge(currentDatabase(), '^WatchLog');

CREATE TABLE _2 as _1 ENGINE=Merge(currentDatabase(), '^WatchLog');

CREATE TABLE hits_all AS hits
ENGINE = Distributed(logs, default, hits)
SETTINGS
    fsync_after_insert=0,
    fsync_directories=0;

CREATE TABLE IF NOT EXISTS db.table_name AS table_function();

CREATE TABLE t1 (x String) ENGINE = Memory AS SELECT 1;

CREATE TABLE codec_example
(
    timestamp DateTime CODEC(DoubleDelta),
    slow_values Float32 CODEC(Gorilla)
)
ENGINE = MergeTree();

CREATE TABLE mytable
(
    x String Codec(Delta, LZ4, AES_128_GCM_SIV)
)
ENGINE = MergeTree ORDER BY x;

CREATE OR REPLACE TABLE base.t1 (n UInt64, s String) ENGINE = MergeTree ORDER BY n;
CREATE OR REPLACE TABLE base.t1 (n UInt64, s Nullable(String)) ENGINE = MergeTree ORDER BY n;

CREATE TABLE t1 (x String) ENGINE = Memory COMMENT 'The temporary table';

CREATE TABLE IF NOT EXISTS all_hits ON CLUSTER cluster (p Date, i Int32) ENGINE = Distributed(cluster, default, hits);

CREATE TABLE table_name
(
    name1 String,
    CONSTRAINT constraint_name_1 CHECK (name1 = 'test')
) ENGINE = engine;

CREATE TABLE example_table
(
    d DateTime,
    a Int TTL d + INTERVAL 1 MONTH,
    b Int TTL d + INTERVAL 1 MONTH,
    c String
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(d)
ORDER BY d;

CREATE TABLE example_table
(
    d DateTime,
    a Int
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(d)
ORDER BY d
TTL d + INTERVAL 1 MONTH DELETE,
    d + INTERVAL 1 WEEK TO VOLUME 'aaa',
    d + INTERVAL 2 WEEK TO DISK 'bbb';

CREATE TABLE my_table
(
    name1 String,
    CONSTRAINT constraint_name_1 ASSUME (name1 = 'test')
)
ENGINE = MergeTree;

-- https://fiddle.clickhouse.com/642653b0-05ec-437c-b601-996b89700c4b
CREATE TABLE example_1
(
    id UInt64,
    region String,
    user_id UInt32,
    PROJECTION region_proj (select region, user_id order by region)
)
ENGINE = MergeTree
ORDER BY id;

CREATE TABLE example_2
(
    id UInt64,
    region String,
    user_id UInt32,
    PROJECTION region_proj (select region, user_id where region = 'JP' order by user_id)
)
ENGINE = MergeTree
ORDER BY id;

CREATE TABLE example_3
(
    id UInt64,
    region String,
    user_id UInt32,
    PROJECTION region_proj (select region, user_id order by region) WITH SETTINGS (
    index_granularity = 4096,
    index_granularity_bytes = 1048576
)
)
ENGINE = MergeTree
ORDER BY id;

CREATE TABLE example_4
(
    id UInt64,
    region String,
    user_id UInt32,
    PROJECTION region_proj (select region, user_id where region = 'JP' order by user_id)
    WITH SETTINGS (
    index_granularity = 4096
)
)
ENGINE = MergeTree
ORDER BY id;

CREATE TABLE example_5
(
    id UInt64,
    region String,
    user_id UInt32,
    PROJECTION region_proj (select region, count(user_id) group by region)
)
ENGINE = MergeTree
ORDER BY id;

CREATE TABLE example_6
(
    id UInt64,
    region String,
    user_id UInt32,
    PROJECTION region_proj (select region, count(user_id) where region = 'JP' group by region)
)
ENGINE = MergeTree
ORDER BY id;

CREATE TABLE example_7
(
    id UInt64,
    region String,
    user_id UInt32,
    PROJECTION region_proj (select region, count(user_id) group by region) WITH SETTINGS (
    index_granularity = 4096,
    index_granularity_bytes = 1048576
)
)
ENGINE = MergeTree
ORDER BY id;

CREATE TABLE example_8
(
    id UInt64,
    region String,
    user_id UInt32,
    PROJECTION region_proj (select region, count(user_id) where region = 'JP' group by region)
    WITH SETTINGS (
    index_granularity = 4096
)
)
ENGINE = MergeTree
ORDER BY id;

CREATE TABLE example_9
(
    id UInt64,
    region String,
    user_id UInt32,
    PROJECTION region_proj_1 (select region, count(user_id) where region = 'JP' group by region)
    WITH SETTINGS (
    index_granularity = 4096
),
  PROJECTION region_proj_2 (select region, user_id order by region) WITH SETTINGS (
    index_granularity = 4096,
    index_granularity_bytes = 1048576
),
  PROJECTION region_proj_3 (select region, user_id where region = 'JP' order by user_id)
)
ENGINE = MergeTree
ORDER BY id;

CREATE TABLE example_10
(
    id UInt64,
    region String,
    user_id UInt32,
    PROJECTION region_proj INDEX region TYPE basic,
    PROJECTION uid_proj INDEX user_id TYPE basic
)
ENGINE = MergeTree
ORDER BY id;

CREATE TABLE example_11
(
    id UInt64,
    region String,
    user_id UInt32,
    PROJECTION region_proj INDEX region TYPE basic,
    PROJECTION uid_proj INDEX user_id TYPE basic WITH SETTINGS (
    index_granularity = 4096,
    index_granularity_bytes = 1048576
)
)
ENGINE = MergeTree
ORDER BY id;

CREATE TABLE example_12
(
    id UInt64,
    region String,
    user_id UInt32,
    PROJECTION region_proj_1 (select region, count(user_id) where region = 'JP' group by region)
    WITH SETTINGS (
    index_granularity = 4096
),
  PROJECTION region_proj_2 (select region, user_id order by region) WITH SETTINGS (
    index_granularity = 4096,
    index_granularity_bytes = 1048576
),
  PROJECTION region_proj_3 (select region, user_id where region = 'JP' order by user_id),
  PROJECTION region_proj INDEX region TYPE basic,
    PROJECTION uid_proj INDEX user_id TYPE basic WITH SETTINGS (
    index_granularity = 4096,
    index_granularity_bytes = 1048576
)
)
ENGINE = MergeTree
ORDER BY id;

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

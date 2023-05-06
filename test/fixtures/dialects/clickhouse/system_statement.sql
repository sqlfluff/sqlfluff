-- RELOAD DICTIONARY
SELECT name, status FROM system.dictionaries;

-- RELOAD MODELS
SYSTEM RELOAD MODELS;
SYSTEM RELOAD MODELS ON CLUSTER cluster_name;

-- RELOAD MODEL
SYSTEM RELOAD MODEL /model/path;
SYSTEM RELOAD MODEL ON CLUSTER cluster_name /model/path;

-- DROP REPLICA
SYSTEM DROP REPLICA 'replica_name' FROM TABLE table;
SYSTEM DROP REPLICA 'replica_name' FROM TABLE database.table;
SYSTEM DROP REPLICA 'replica_name' FROM DATABASE database;
SYSTEM DROP REPLICA 'replica_name';
SYSTEM DROP REPLICA 'replica_name' FROM ZKPATH '/path/to/table/in/zk';

-- Managing Distributed Tables
-- -- STOP DISTRIBUTED SENDS
SYSTEM STOP DISTRIBUTED SENDS distributed_table_name;
SYSTEM STOP DISTRIBUTED SENDS db.distributed_table_name;
-- -- FLUSH DISTRIBUTED
SYSTEM FLUSH DISTRIBUTED distributed_table_name;
SYSTEM FLUSH DISTRIBUTED db.distributed_table_name;
-- -- START DISTRIBUTED SENDS
SYSTEM START DISTRIBUTED SENDS distributed_table_name;
SYSTEM START DISTRIBUTED SENDS db.distributed_table_name;

-- Managing MergeTree Tables
-- -- STOP MERGES
SYSTEM STOP MERGES ON VOLUME volume_name;
SYSTEM STOP MERGES merge_tree_family_table_name;
SYSTEM STOP MERGES db.merge_tree_family_table_name;
-- -- START MERGES
SYSTEM START MERGES ON VOLUME volume_name;
SYSTEM START MERGES merge_tree_family_table_name;
SYSTEM START MERGES db.merge_tree_family_table_name;
-- -- STOP TTL MERGES
SYSTEM STOP TTL MERGES;
SYSTEM STOP TTL MERGES db.merge_tree_family_table_name;
SYSTEM STOP TTL MERGES merge_tree_family_table_name;
-- -- START TTL MERGES
SYSTEM START TTL MERGES;
SYSTEM START TTL MERGES merge_tree_family_table_name;
SYSTEM START TTL MERGES db.merge_tree_family_table_name;
-- -- STOP MOVES
SYSTEM STOP MOVES;
SYSTEM STOP MOVES merge_tree_family_table_name;
SYSTEM STOP MOVES db.merge_tree_family_table_name;
-- -- START MOVES
SYSTEM START MOVES;
SYSTEM START MOVES merge_tree_family_table_name;
SYSTEM START MOVES db.merge_tree_family_table_name;
-- -- SYSTEM UNFREEZE
SYSTEM UNFREEZE WITH NAME backup_name;

-- Managing ReplicatedMergeTree Tables
-- -- STOP FETCHES
SYSTEM STOP FETCHES;
SYSTEM STOP FETCHES replicated_merge_tree_family_table_name;
SYSTEM STOP FETCHES db.replicated_merge_tree_family_table_name;
-- -- START FETCHES
SYSTEM START FETCHES;
SYSTEM START FETCHES replicated_merge_tree_family_table_name;
SYSTEM START FETCHES db.replicated_merge_tree_family_table_name;
-- -- STOP REPLICATED SENDS
SYSTEM STOP REPLICATED SENDS;
SYSTEM STOP REPLICATED SENDS replicated_merge_tree_family_table_name;
SYSTEM STOP REPLICATED SENDS db.replicated_merge_tree_family_table_name;
-- -- START REPLICATED SENDS
SYSTEM START REPLICATED SENDS;
SYSTEM START REPLICATED SENDS replicated_merge_tree_family_table_name;
SYSTEM START REPLICATED SENDS db.replicated_merge_tree_family_table_name;
-- -- STOP REPLICATION QUEUES
SYSTEM STOP REPLICATION QUEUES;
SYSTEM STOP REPLICATION QUEUES replicated_merge_tree_family_table_name;
SYSTEM STOP REPLICATION QUEUES db.replicated_merge_tree_family_table_name;
-- -- START REPLICATION QUEUES
SYSTEM START REPLICATION QUEUES;
SYSTEM START REPLICATION QUEUES replicated_merge_tree_family_table_name;
SYSTEM START REPLICATION QUEUES db.replicated_merge_tree_family_table_name;
-- -- SYNC REPLICA
SYSTEM SYNC REPLICA replicated_merge_tree_family_table_name;
SYSTEM SYNC REPLICA db.replicated_merge_tree_family_table_name;
SYSTEM SYNC REPLICA replicated_merge_tree_family_table_name STRICT;
SYSTEM SYNC REPLICA ON CLUSTER cluster_name replicated_merge_tree_family_table_name;
SYSTEM SYNC REPLICA ON CLUSTER cluster_name replicated_merge_tree_family_table_name STRICT;
SYSTEM SYNC REPLICA ON CLUSTER cluster_name db.replicated_merge_tree_family_table_name;
SYSTEM SYNC REPLICA ON CLUSTER cluster_name db.replicated_merge_tree_family_table_name STRICT;
-- -- RESTART REPLICA
SYSTEM RESTART REPLICA replicated_merge_tree_family_table_name;
SYSTEM RESTART REPLICA db.replicated_merge_tree_family_table_name;
-- -- RESTORE REPLICA
SYSTEM RESTORE REPLICA replicated_merge_tree_family_table_name;
SYSTEM RESTORE REPLICA db.replicated_merge_tree_family_table_name;
SYSTEM RESTORE REPLICA replicated_merge_tree_family_table_name ON CLUSTER cluster_name;
SYSTEM RESTORE REPLICA db.replicated_merge_tree_family_table_name ON CLUSTER cluster_name;
-- -- DROP FILESYSTEM CACHE
SYSTEM DROP FILESYSTEM CACHE;
-- -- SYNC FILE CACHE
SYSTEM SYNC FILE CACHE;

SELECT /*+ COALESCE(3) */
    a,
    b,
    c
FROM t;

SELECT /*+ REPARTITION(3) */
    a,
    b,
    c
FROM t;

SELECT /*+ REPARTITION(c) */
    a,
    b,
    c
FROM t;

SELECT /*+ REPARTITION(3, c) */
    a,
    b,
    c
FROM t;

SELECT /*+ REPARTITION_BY_RANGE(c) */
    a,
    b,
    c
FROM t;

SELECT /*+ REPARTITION_BY_RANGE(3, c) */
    a,
    b,
    c
FROM t;

SELECT /*+ REBALANCE */
    a,
    b,
    c
FROM t;

SELECT /*+ REBALANCE(c) */
    a,
    b,
    c
FROM t;

-- multiple partitioning hints
SELECT /*+ REPARTITION(100), COALESCE(500), REPARTITION_BY_RANGE(3, c) */
    a,
    b,
    c
FROM t;

-- Join Hints for broadcast join
SELECT /*+ BROADCAST(t1) */
    t1.a,
    t1.b,
    t2.c
FROM t1 INNER JOIN t2 ON t1.key = t2.key;

SELECT /*+ BROADCASTJOIN(t1) */
    t1.a,
    t1.b,
    t2.c
FROM t1 LEFT JOIN t2 ON t1.key = t2.key;

SELECT /*+ MAPJOIN(t2) */
    t1.a,
    t1.b,
    t2.c
FROM t1 LEFT JOIN t2 ON t1.key = t2.key;

-- Join Hints for shuffle sort merge join
SELECT /*+ SHUFFLE_MERGE(t1) */
    t1.a,
    t1.b,
    t2.c
FROM t1 INNER JOIN t2 ON t1.key = t2.key;

SELECT /*+ MERGEJOIN(t2) */
    t1.a,
    t1.b,
    t2.c
FROM t1 INNER JOIN t2 ON t1.key = t2.key;

SELECT /*+ MERGE(t1) */
    t1.a,
    t1.b,
    t2.c
FROM t1 INNER JOIN t2 ON t1.key = t2.key;

-- Join Hints for shuffle hash join
SELECT /*+ SHUFFLE_HASH(t1) */
    t1.a,
    t1.b,
    t2.c
FROM t1 INNER JOIN t2 ON t1.key = t2.key;

-- Join Hints for shuffle-and-replicate nested loop join
SELECT /*+ SHUFFLE_REPLICATE_NL(t1) */
    t1.a,
    t1.b,
    t2.c
FROM t1 INNER JOIN t2 ON t1.key = t2.key;

SELECT /*+ BROADCAST(t1), MERGE(t1, t2) */
    t1.a,
    t1.b,
    t2.c
FROM t1 INNER JOIN t2 ON t1.key = t2.key;

SELECT /*+ BROADCAST(db.t1) */
    t1.a,
    t1.b,
    t2.c
FROM t1 INNER JOIN t2 ON t1.key = t2.key;

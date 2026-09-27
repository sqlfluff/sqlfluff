CREATE TABLE t_recharge_detail2
(
    id BIGINT,
    user_id BIGINT,
    recharge_money DECIMAL(32, 2),
    city VARCHAR(20) NOT NULL,
    dt VARCHAR(20) NOT NULL
)
DUPLICATE KEY(id)
PARTITION BY LIST (city)
(
    PARTITION pLos_Angeles VALUES IN ("Los Angeles", "San Francisco", "San Diego"),
    PARTITION pSan_Francisco VALUES IN ("San Jose", "Fresno")
)
DISTRIBUTED BY HASH(id);

CREATE TABLE t_recharge_detail4
(
    id BIGINT,
    city VARCHAR(20) NOT NULL,
    dt VARCHAR(20) NOT NULL
)
ENGINE=OLAP
DUPLICATE KEY(id)
PARTITION BY LIST (dt, city)
(
    PARTITION p1 VALUES IN (("2022-04-01", "Los Angeles"), ("2022-04-02", "Los Angeles")),
    PARTITION p2 VALUES IN (("2022-04-01", "Houston"), ("2022-04-02", "Houston"))
)
DISTRIBUTED BY HASH(id);

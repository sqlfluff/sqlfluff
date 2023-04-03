CREATE TABLE measurement (
city_id int NOT NULL,
logdate date NOT NULL,
peaktemp int,
unitsales int
) WITH (appendoptimized=true, compresslevel=5)
DISTRIBUTED BY (txn_id);


CREATE TABLE measurement (
city_id int NOT NULL,
logdate date NOT NULL,
peaktemp int,
unitsales int
) WITH (appendoptimized=true)
DISTRIBUTED BY (txn_id);


CREATE TABLE test (
test_id int NOT NULL,
logdate date NOT NULL,
test_text int
)
DISTRIBUTED BY (txn_id);


CREATE TABLE test_randomly (
test_id int NOT NULL,
logdate date NOT NULL,
test_text int
)
DISTRIBUTED RANDOMLY;

CREATE TABLE test_replicated (
test_id int NOT NULL,
logdate date NOT NULL,
test_text int
)
DISTRIBUTED REPLICATED;


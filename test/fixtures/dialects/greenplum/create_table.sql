CREATE TABLE measurement (
city_id int NOT NULL,
logdate date NOT NULL,
peaktemp int,
unitsales int
) WITH (appendoptimized=true, compresslevel=5)
DISTRIBUTED BY (txn_id, other_field);


CREATE TABLE measurement (
city_id int NOT NULL,
logdate date NOT NULL,
peaktemp int,
unitsales int
) WITH (appendoptimized=true, orientation="column")
DISTRIBUTED BY (txn_id);


CREATE TEMP TABLE test (
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

create table table1 (
    column1 int
    , column2 varchar
    , column3 boolean
)
with (appendoptimized = true, compresstype = zstd)
distributed by (column1, column2);

CREATE TABLE sales (id int, year int, qtr int, c_rank int, code char(1), region text)
DISTRIBUTED BY (id)
PARTITION BY LIST (code)
( PARTITION sales VALUES ('S'),
  PARTITION returns VALUES ('R')
);

CREATE TABLE sales (id int, year int, qtr int, c_rank int, code char(1), region text)
DISTRIBUTED BY (id)
PARTITION BY LIST (code)
  SUBPARTITION BY RANGE (c_rank)
    SUBPARTITION by LIST (region)

( PARTITION sales VALUES ('S')
   ( SUBPARTITION cr1 START (1) END (2)
      ( SUBPARTITION ca VALUES ('CA') ),
      SUBPARTITION cr2 START (3) END (4)
        ( SUBPARTITION ca VALUES ('CA') ) ),

 PARTITION returns VALUES ('R')
   ( SUBPARTITION cr1 START (1) END (2)
      ( SUBPARTITION ca VALUES ('CA') ),
     SUBPARTITION cr2 START (3) END (4)
        ( SUBPARTITION ca VALUES ('CA') ) )
);

CREATE TABLE sales1 (id int, year int, qtr int, c_rank int, code char(1), region text)
DISTRIBUTED BY (id)
PARTITION BY LIST (code)

   SUBPARTITION BY RANGE (c_rank)
     SUBPARTITION TEMPLATE (
     SUBPARTITION cr1 START (1) END (2),
     SUBPARTITION cr2 START (3) END (4) )

     SUBPARTITION BY LIST (region)
       SUBPARTITION TEMPLATE (
       SUBPARTITION ca VALUES ('CA') )

( PARTITION sales VALUES ('S'),
  PARTITION  returns VALUES ('R')
);

CREATE TABLE sales (id int, year int, qtr int, c_rank int, code char(1), region text)
DISTRIBUTED BY (id)
PARTITION BY RANGE (year)

  SUBPARTITION BY RANGE (qtr)
    SUBPARTITION TEMPLATE (
    START (1) END (5) EVERY (1),
    DEFAULT SUBPARTITION bad_qtr )

    SUBPARTITION BY LIST (region)
      SUBPARTITION TEMPLATE (
      SUBPARTITION usa VALUES ('usa'),
      SUBPARTITION europe VALUES ('europe'),
      SUBPARTITION asia VALUES ('asia'),
      DEFAULT SUBPARTITION other_regions)

( START (2009) END (2011) EVERY (1),
  DEFAULT PARTITION outlying_years);

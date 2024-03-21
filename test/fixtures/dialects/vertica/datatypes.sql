-- binary
create table a (
  a BINARY,
  b VARBINARY,
  ba LONG VARBINARY
);

-- Boolean
create table b (
    a boolean
);

-- Character / Long
create table c (
    a char,
    aa char(7),
    b varchar,
    bb varchar(10),
    c long varchar,
    cc long varchar(100000)
);

-- Date / Time
create table d (
    a date,
    b TIME,
    c TIME WITH TIME ZONE,
    d TIMESTAMP,
    e DATETIME,
    f SMALLDATETIME,
    g TIMESTAMP WITH TIME ZONE,
    h INTERVAL,
    i INTERVAL DAY TO SECOND,
    j INTERVAL YEAR TO MONTH
);

-- Approximate numeric
create table e(
    a double precision,
    b float,
    bb float(7),
    bbb float (7),
    c float8,
    d real
);

-- Binary
create table f(
    a BINARY,
    b VARBINARY,
    c LONG VARBINARY,
    d BYTEA,
    e RAW
);

-- Exact numeric
create table g(
    a INTEGER,
    b INT,
    c BIGINT,
    d INT8,
    e SMALLINT,
    f TINYINT,
    g DECIMAL,
    gg DECIMAL(5),
    ggg DECIMAL(5, 2),
    h NUMERIC,
    hh NUMERIC(5),
    hhh NUMERIC(5, 2),
    hhhh NUMERIC (5, 2),
    i NUMBER,
    ii NUMBER(5),
    iii NUMBER(5, 2),
    j MONEY,
    jj MONEY(5),
    jjj MONEY(5, 2)
);

-- UUID
create table h(
    a uuid
);

-- Spatial
create table i(
    a GEOMETRY,
    aa GEOMETRY(10),
    b GEOGRAPHY,
    bb GEOGRAPHY(10)
);

-- Arrays
create table p (
    a array[integer],
    b array[varchar(50)]
--     It should be covered in the future
--     bb array[varchar(50), 100],
--     bbb array[varchar(50)](100),
);

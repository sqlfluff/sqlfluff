create table a(
  a smallint,
  b integer,
  ba int2,
  bb int4,
  bc int8,
  bd int,
  c bigint,
  d real,
  e double precision,
  f smallserial,
  g serial,
  ga serial2,
  gb serial4,
  gc serial8,
  h bigserial
);

create table b(
    a float,
    b float(24),
    c float4,
    e float8
);

create table c(
    a numeric,
    aa decimal,
    b numeric(7),
    ba decimal(7),
    c numeric(7,2),
    ca decimal(7,2)
);

create table d(
    a money
);

create table e(
    a char,
    b char(7),
    c character,
    d character(5),
    e character varying,
    f character varying(8),
    g varchar(9),
    h varchar,
    i text
);

create table f(
    a bytea
);

create table g(
    a date,
    b interval(4),
    c time(4),
    d time(4) with time zone,
    e time(4) without time zone,
    f timestamp(4),
    g timestamp(4) with time zone,
    h timestamp(4) without time zone,
    i timetz,
    j timetz(4),
    k timestamptz,
    l timestamptz(4)
);

create table h(
    a boolean,
    b bool
);

create table i(
    a point,
    b line,
    c lseg,
    d box,
    e path,
    f polygon,
    g circle
);

create table j(
    a cidr,
    b inet,
    c macaddr,
    d macaddr8
);

create table k(
    a bit,
    b bit(3),
    c bit varying,
    d bit varying(5)
);

create table l(
    a pg_lsn
);

create table l(
    a tsvector,
    b tsquery
);

create table m(
    a uuid
);

create table n(
    a xml
);

create table o(
    a json,
    b jsonb
);

create table p(
    a integer[],
    b float[][],
    c char[1],
    d jsonb[3][5],
    e money ARRAY,
    f money ARRAY[7]
);

-- user defined data types
CREATE TYPE bar AS ENUM ('foo', 'bar');

create table q(
    a bar
);

-- data type with schema
create type public.c AS ENUM ('foo', 'bar');

create table r(
    a public.c
);

-- DATETIME is a valid datatype, but is not a date_time_identifier; it is only
-- potentially a user-defined type (i.e. a data_type_identifier).
CREATE TABLE a (
    b DATE,
    c DATETIME
);

-- from https://github.com/sqlfluff/sqlfluff/issues/2649
SELECT
    b::DATETIME
FROM a;

SELECT
    b,
    c::DATE
FROM a;

create table test (
    situation bpchar(1) null default 'A'::bpchar
);

create table a(
  a smallint,
  b integer,
  ba int2,
  bb int4,
  bc int8,
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
    e character varying(8),
    f varchar(9),
    g varchar,
    h text
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

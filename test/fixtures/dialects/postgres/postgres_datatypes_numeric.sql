create table a(
  a smallint,
  b integer,
  ba int2,
  bb int4,
  bc int8,
  c bigint,
  d real,

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
    d float4(12),
    e float8,
    f float8(12)
);

create table c(
    a numeric,
    aa decimal,
    b numeric(7),
    ba decimal(7),
    c numeric(7,2),
    ca decimal(7,2)
);

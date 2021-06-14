CREATE TABLE t1(
  a UUID PRIMARY KEY,
  b UUID NOT NULL REFERENCES t2(a),
  c numeric(7,6) NOT NULL,
  d date NOT NULL,
  e timestamp with time zone NOT NULL,
  f character varying NOT NULL
);

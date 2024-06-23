CREATE TABLE t1 (
   a INT,
   b INT,
   c TEXT,
   d INT GENERATED ALWAYS AS (a*abs(b)) VIRTUAL,
   e TEXT GENERATED ALWAYS AS (substr(c,b,b+1)) STORED,
   PRIMARY KEY (a)
);

CREATE TABLE t1 (
   a INT,
   b INT,
   c TEXT,
   d INT AS (a*abs(b)),
   e TEXT AS (substr(c,b,b+1)) STORED COMMENT 'foo',
   PRIMARY KEY (a)
);

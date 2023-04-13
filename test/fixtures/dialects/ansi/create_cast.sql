CREATE CAST (int AS bool) WITH FUNCTION fname;

CREATE CAST (int AS bool) WITH FUNCTION fname AS ASSIGNMENT;

CREATE CAST (int AS bool) WITH FUNCTION fname();

CREATE CAST (int AS bool) WITH FUNCTION fname(bool);

CREATE CAST (int AS bool) WITH FUNCTION sch.fname(int, bool) AS ASSIGNMENT;

CREATE CAST (udt_1 AS udt_2) WITH FUNCTION fname(udt_1, udt_2) FOR udt_3;

CREATE CAST (sch.udt_1 AS sch.udt_2) WITH FUNCTION sch.fname(sch.udt_1, sch.udt_2) FOR sch.udt_3;

CREATE CAST (int AS bool) WITH ROUTINE fname();

CREATE CAST (int AS bool) WITH PROCEDURE fname();

CREATE CAST (int AS bool) WITH METHOD fname();

CREATE CAST (int AS bool) WITH INSTANCE METHOD fname();

CREATE CAST (int AS bool) WITH STATIC METHOD fname();

CREATE CAST (int AS bool) WITH CONSTRUCTOR METHOD fname();

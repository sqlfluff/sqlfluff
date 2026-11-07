SELECT TO_JSON(STRUCT(e.m.*, c.x)) FROM t;

SELECT STRUCT(a.*, b.*, 1 AS c) FROM a, b;

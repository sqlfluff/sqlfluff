WITH foo AS (SELECT a, b FROM t1), bar AS (SELECT c, d FROM t2)

SELECT foo.a, bar.c FROM foo CROSS JOIN bar

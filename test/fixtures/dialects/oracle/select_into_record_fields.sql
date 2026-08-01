CREATE OR REPLACE PROCEDURE test_proc(out_rec OUT SYS_REFCURSOR) IS
  TYPE t_rec IS RECORD (a NUMBER, b NUMBER);
  out_metrics t_rec;
BEGIN
  WITH cte1 AS (
    SELECT 1 AS x FROM dual
  )
  SELECT
    cte1.x,
    cte1.x
  INTO
    out_metrics.a,
    out_metrics.b
  FROM cte1;
END;
/

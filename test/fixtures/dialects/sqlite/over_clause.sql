SELECT x, y, row_number() OVER (ORDER BY y) AS row_number FROM t0 ORDER BY x;

SELECT a, b, group_concat(b, '.') OVER (
  ORDER BY a
  ROWS
  BETWEEN 1 PRECEDING
  AND 1 FOLLOWING
) AS group_concat FROM t1;

SELECT c, a, b, group_concat(b, '.') OVER (
  PARTITION BY c ORDER BY a RANGE BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
) AS group_concat
FROM t1 ORDER BY c, a;

SELECT c, a, b, group_concat(b, '.') OVER (
  PARTITION BY c ORDER BY a RANGE BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
) AS group_concat
FROM t1 ORDER BY a;

SELECT a, b, c,
       group_concat(b, '.') OVER (ORDER BY c) AS group_concat
FROM t1 ORDER BY a;

SELECT c, a, b, group_concat(b, '.') OVER (
  ORDER BY c, a ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
) AS group_concat
FROM t1 ORDER BY c, a;

SELECT c, a, b,
  group_concat(b, '.') OVER (
    ORDER BY c GROUPS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW EXCLUDE NO OTHERS
  ) AS no_others,
  group_concat(b, '.') OVER (
    ORDER BY c GROUPS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW EXCLUDE CURRENT ROW
  ) AS current_row,
  group_concat(b, '.') OVER (
    ORDER BY c GROUPS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW EXCLUDE GROUP
  ) AS grp,
  group_concat(b, '.') OVER (
    ORDER BY c GROUPS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW EXCLUDE TIES
  ) AS ties
FROM t1 ORDER BY c, a;

SELECT c, a, b, group_concat(b, '.') FILTER (WHERE c != 'two') OVER (
  ORDER BY a
) AS group_concat
FROM t1 ORDER BY a;

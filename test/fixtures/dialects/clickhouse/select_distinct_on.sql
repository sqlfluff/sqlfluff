SELECT DISTINCT ON (a,b) * FROM t1;
SELECT DISTINCT ON (a,b) * FROM t1 ORDER BY b ASC;

-- Distinct on clause can contain expressions
SELECT DISTINCT ON (a = b, c) * FROM t1 ORDER BY b ASC;

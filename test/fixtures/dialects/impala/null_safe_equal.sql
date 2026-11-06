SELECT 1 <=> 1, NULL <=> NULL, 1 <=> NULL;

SELECT a <=> b FROM tbl WHERE c <=> NULL;

SELECT *
FROM tbl_a
INNER JOIN tbl_b ON tbl_a.col <=> tbl_b.col;

SELECT * FROM tbl WHERE NOT a <=> b;

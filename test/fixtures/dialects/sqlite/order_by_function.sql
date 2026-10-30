-- Functions and literals in ORDER BY / GROUP BY are expressions, not column
-- references.
SELECT p.diagnosis
FROM patient AS p
GROUP BY p.diagnosis
ORDER BY COUNT(*) DESC;

SELECT a FROM t GROUP BY LOWER(a) ORDER BY LOWER(a), MAX(b);

SELECT a, COUNT(*) FROM t GROUP BY 1 ORDER BY 2 DESC, 1.5;

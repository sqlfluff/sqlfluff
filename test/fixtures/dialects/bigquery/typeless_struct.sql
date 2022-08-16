
SELECT IF(
        TRUE,
        STRUCT('hello' AS greeting, 'world' AS subject),
        STRUCT('hi' AS greeting, 'there' AS subject)
    ) AS salute
FROM (SELECT 1);

SELECT
  CASE
    WHEN a.xxx != b.xxx THEN STRUCT(a.xxx AS M, b.xxx AS N)
  END AS xxx
FROM A
JOIN B ON B.id = A.id;

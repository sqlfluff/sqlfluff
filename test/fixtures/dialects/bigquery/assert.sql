ASSERT (
  (SELECT COUNT(*) FROM UNNEST([1, 2, 3, 4, 5, 6])) > 5
) AS 'Table must contain more than 5 rows.';

ASSERT
  EXISTS(
    SELECT X
    FROM UNNEST([7877, 7879, 7883, 7901, 7907]) AS X
    WHERE X = 7919
  )
AS 'Column X must contain the value 7919';

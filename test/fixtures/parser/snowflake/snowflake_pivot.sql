-- NB This is a pivot expression With and Alias. The alias should be parsed seperately to the pivot.
SELECT * FROM my_tbl
PIVOT (min(f_val) FOR f_id IN (1, 2)) AS f (a, b);

SELECT * FROM my_tbl
UNPIVOT (val FOR col_name IN (a, b));

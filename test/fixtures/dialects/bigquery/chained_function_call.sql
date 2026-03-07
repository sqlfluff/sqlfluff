SELECT (x).UPPER() AS y;
SELECT (x).SUBSTR(1, 3) AS y;
SELECT
  ('one two three four five')
  .REPLACE('one', '1')
  .REPLACE('two', '2')
  .REPLACE('three', '3')
  .REPLACE('four', '4')
  .REPLACE('five', '5');
SELECT (x).STRPOS("pattern string");
SELECT (x).ARRAY_CONCAT(y);
SELECT "Two birds and one mouse"
  .REPLACE("bird", "dog")
  .REPLACE("mouse", "cat") AS result;

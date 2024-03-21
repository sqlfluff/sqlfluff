-- The variant of REGEXP_REPLACE that accepts a function
-- lambda expression as an argument can be tricky to parse.
-- Signature:
--    regexp_replace(string, pattern, function) → varchar
-- Reference:
--     https://trino.io/docs/422/functions/regexp.html

SELECT REGEXP_REPLACE('new york', '(\w)(\w*)', x -> UPPER(x[1]) || LOWER(x[2]));

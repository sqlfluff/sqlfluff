-- file with both parsing and lexing errors.
-- Used for checking ignore functionality and
-- the ability to work around issues.
SELECT
   a.id, -- 3 Spaces
    a.name,
    a.training_spaces,
    some_function(SELECT LIMIT WHERE BY ORDER) AS not_parsable,
    another_function(🤷‍♀️) AS not_lexable
FROM tbl AS a

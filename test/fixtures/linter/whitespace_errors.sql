SELECT
    a.id   , -- Comma with leading spaces
    a.name,    a.training_spaces
,    -- Comma on newline, trailing spaces but with comment!
    a.normal_comma, a.should_work
FROM tbl as a

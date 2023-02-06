SELECT
    a.id, -- 3 Spaces
    a.name,
    a.training_spaces,
    (
        a.under_indented_line
    ) as foo,
    (
        a.over_indented_line
    ) as bar,
    a.line + (
        a.with
        + a.hanging_indent
    ) as actually_ok,
    a.line + (
        a.with
        + a.bad_hanging_indent
    ) as problem,
    a.line + (
        a.something_indented_well
        + least(
            a.good_example,
            a.bad_example,
            a.really_bad_example,
            a.nother_good_example
        )
    ) as some_harder_problems
FROM tbl as a

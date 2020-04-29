SELECT
    a.id1, -- 3 Spaces
    a.name1,
    a.training_spaces,
    (
        a.under_indented_line
    ) as foo,
    (
        a.over_indented_line
    ) as bar,
    a.line + (a.with1
              + a.hanging_indent) as actually_ok,
    a.line + (a.with1
              + a.bad_hanging_indent) as problem,
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

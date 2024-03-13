-- Test cases for some complex functions like explode
-- and mapkeys which allow alias for several columns

select
    col1,
    col2,
    col3,
    mapkeys(complex_col)
        over (
            partition by
                col1,
                col2,
                col3
        )
        as (aliased_complex_col)
from split_docs

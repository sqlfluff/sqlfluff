{% import 'search_a.sql' as search_a_pkg %}
{% import 'subdir/search_a_subdir.sql' as search_a_subdir_pkg %}
{% import 'search_b.sql' as search_b_pkg %}

select
    -- the second expression on each line should evaluate to nothing,
    -- since these macros are not loaded into the global namespace.
    {{ search_a_pkg.search_a() }} {{ search_a() }},
    {{ search_a_subdir_pkg.search_a_subdir() }} {{ search_a_subdir() }},
    {{ search_b_pkg.search_b() }} {{ search_b() }},

    -- these are still being loaded from the global namespace
    {{ macro_load() }},
    {{ macro_load_subdir() }}
from my_table

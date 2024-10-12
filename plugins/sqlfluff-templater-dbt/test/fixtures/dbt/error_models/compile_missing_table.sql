-- This Query triggers an expection at compilation time because it runs
-- a query *at compile time*, which will fail.
{% set results = run_query('select 1 from this_table_does_not_exist') %}
select 1

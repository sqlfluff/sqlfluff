with
hits as (
    select
        hit_id as hit_code,
        string_to_array(coalesce(hit_categories, '[]') using parameters collection_delimiter = ',') as hit_categories_array
    from test.table_name
    where not is_deleted_flg
),

result as (
    select
        hit_code,
        array_find(
            hit_categories_array,
            e -> e not in (
                'Apple', 'Banana', 'Cherry', 'Durian', 'Elderberry', 'Fig'
            )
        ) > -1 as is_unknown_category_flg
    from hits
)
select * from result;

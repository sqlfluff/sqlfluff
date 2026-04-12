select
    struct_column.inner_array[0].foo as inner_array__foo,
    try_element_at(struct_column.inner_array, 1).foo as inner_array__foo2,
    ELEMENT_AT(FROM_JSON('[{"f1":"v1","f2":"v2"}]', 'ARRAY<STRUCT<f1: STRING, f2: STRING>>'), -1).f1 as nested_func_struct_access,
    named_struct('a', 1, 'b', 2).a as named_struct_access,
    get_json_object(col, '$.x').y.z as chained_dot_access
from src;

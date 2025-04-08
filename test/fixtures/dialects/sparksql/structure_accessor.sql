select
    struct_column.inner_array[0].foo as inner_array__foo,
    try_element_at(struct_column.inner_array, 1).foo as inner_array__foo2
from src;

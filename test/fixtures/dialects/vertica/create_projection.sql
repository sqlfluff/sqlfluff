CREATE PROJECTION public.employee_dimension_super
    AS SELECT * FROM public.employee_dimension
    ORDER BY employee_key
    SEGMENTED BY hash(employee_key) ALL NODES;

CREATE PROJECTION store.store_dimension_proj (storekey, name, city, state)
             AS SELECT store_key, store_name, store_city, store_state
             FROM store.store_dimension
             UNSEGMENTED ALL NODES;

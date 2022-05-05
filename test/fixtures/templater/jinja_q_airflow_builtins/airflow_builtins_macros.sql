SELECT
    '{{ ds }}',
    '{{ macros.ds_add(ds, 0) }}',
    '{{ macros.ds_add(ds, 5) }}',
    '{{ macros.ds_format("2015-01-01", "%Y-%m-%d", "%m-%d-%y") }}',
    '{{ macros.ds_format("1/5/2015", "%m/%d/%Y", "%Y-%m-%d") }}',
    '{{ macros.random() }}',
    '{{ macros.uuid.uuid4() }}'

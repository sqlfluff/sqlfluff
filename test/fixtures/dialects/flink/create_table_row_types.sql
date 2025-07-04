CREATE TABLE my_table (
    id INT,
    nested_data ROW<name STRING, age INT>,
    address_info ROW<street STRING, city STRING>
) WITH (
    'connector' = 'kafka'
);

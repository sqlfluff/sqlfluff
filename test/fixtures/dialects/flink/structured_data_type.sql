CREATE TABLE customers (
    id INT,
    customer STRUCTURED<'com.example.Customer', active BOOLEAN, id INT NOT NULL, name STRING, properties MAP<STRING NOT NULL, STRING NOT NULL>>,
    described STRUCTURED<'com.example.Described', id INT 'customer id', name STRING COMMENT 'full name'>,
    empty_obj STRUCTURED<'com.example.Empty'>
) WITH (
    'connector' = 'print'
);

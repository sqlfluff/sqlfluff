CREATE TABLE advanced_aggregate_test
(
    order_id BIGINT,
    customer_id INT,
    product_id INT,
    quantity INT SUM,
    unit_price DECIMAL(10, 2) MAX,
    total_amount DECIMAL(12, 2) SUM,
    order_status STRING REPLACE,
    order_date DATE,
    delivery_address STRING,
    payment_method STRING REPLACE,
    discount_rate DECIMAL(3, 2) MIN,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
)
AGGREGATE KEY (order_id, customer_id, product_id)
DISTRIBUTED BY HASH (order_id)
PROPERTIES (
    'replication_num' = '1',
    'storage_medium' = 'SSD'
); 
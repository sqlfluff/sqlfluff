CREATE TABLE dbo.customer
(
    customer_id BIGINT IDENTITY,
    customer_name VARCHAR(200) NOT NULL,
    region_id INT NULL,
    created_date DATE NOT NULL
)
WITH
(
    CLUSTER BY (customer_id)
);

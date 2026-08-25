CREATE TABLE dbo.customer
(
    customer_id INT NOT NULL,
    customer_name VARCHAR(200) NOT NULL
);

ALTER TABLE dbo.customer
    ADD CONSTRAINT PK_customer PRIMARY KEY NONCLUSTERED (customer_id) NOT ENFORCED;

CREATE TABLE dbo.orders
(
    order_id INT NOT NULL,
    customer_id INT NOT NULL
);

ALTER TABLE dbo.orders
    ADD CONSTRAINT FK_orders_customer FOREIGN KEY (customer_id)
    REFERENCES dbo.customer (customer_id) NOT ENFORCED;

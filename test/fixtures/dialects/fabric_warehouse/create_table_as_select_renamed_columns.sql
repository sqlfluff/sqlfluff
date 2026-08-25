CREATE TABLE dbo.customer_renamed (id, full_name)
WITH
(
    CLUSTER BY (id)
)
AS
SELECT customer_id, customer_name FROM dbo.customer;

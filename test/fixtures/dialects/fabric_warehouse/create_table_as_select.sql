CREATE TABLE dbo.customer_copy
WITH
(
    CLUSTER BY (customer_id)
)
AS
SELECT * FROM dbo.customer;

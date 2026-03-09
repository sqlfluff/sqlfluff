-- CREATE EXTERNAL TABLE AS SELECT (CETAS) - basic form
CREATE EXTERNAL TABLE [dbo].[Product]
WITH (
    LOCATION = 'production/product/',
    DATA_SOURCE = AzureDataLakeStore,
    FILE_FORMAT = TextFileFormat
)
AS
SELECT * FROM dbo.Product;

-- CETAS writing aggregated results to external storage
CREATE EXTERNAL TABLE [export].[SalesSummary]
WITH (
    LOCATION = 'exports/sales/summary/',
    DATA_SOURCE = AzureDataLakeStore,
    FILE_FORMAT = ParquetFormat
)
AS
SELECT
    region,
    product_id,
    SUM(amount) AS total_amount,
    COUNT(*) AS order_count
FROM dbo.Orders
GROUP BY region, product_id;

-- CETAS with a CTE
CREATE EXTERNAL TABLE [export].[TopCustomers]
WITH (
    LOCATION = 'exports/customers/top/',
    DATA_SOURCE = AzureDataLakeStore,
    FILE_FORMAT = ParquetFormat
)
AS
WITH ranked AS (
    SELECT
        customer_id,
        total_spend,
        ROW_NUMBER() OVER (ORDER BY total_spend DESC) AS rn
    FROM dbo.Customers
)
SELECT customer_id, total_spend
FROM ranked
WHERE rn <= 100;

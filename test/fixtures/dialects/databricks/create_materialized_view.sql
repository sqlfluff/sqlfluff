-- Databricks CREATE MATERIALIZED VIEW examples
-- https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-materialized-view
-- https://docs.databricks.com/aws/en/ldp/developer/ldp-sql-ref-create-materialized-view

CREATE MATERIALIZED VIEW my_mv AS
SELECT * FROM my_table;

CREATE OR REPLACE MATERIALIZED VIEW my_mv AS
SELECT id, name FROM my_table;

CREATE MATERIALIZED VIEW IF NOT EXISTS my_mv AS
SELECT * FROM my_table;

CREATE MATERIALIZED VIEW typed_mv (
    id INT NOT NULL COMMENT 'Primary key',
    name STRING COMMENT 'Customer name',
    amount DECIMAL(10, 2)
) AS SELECT id, name, amount FROM orders;

CREATE MATERIALIZED VIEW sales_mv
COMMENT 'Materialized view for sales analytics'
AS SELECT region, SUM(amount) as total FROM sales GROUP BY region;

CREATE MATERIALIZED VIEW partitioned_mv
PARTITIONED BY (region)
AS SELECT region, product, SUM(quantity) as total_qty FROM inventory GROUP BY region, product;

CREATE MATERIALIZED VIEW clustered_mv
CLUSTER BY (customer_id)
AS SELECT customer_id, order_date, total FROM orders;

CREATE MATERIALIZED VIEW props_mv
TBLPROPERTIES ('delta.autoOptimize.optimizeWrite' = 'true')
AS SELECT * FROM large_table;

CREATE MATERIALIZED VIEW collated_mv
DEFAULT COLLATION UTF8_BINARY
AS SELECT name, address FROM customers;

CREATE MATERIALIZED VIEW hourly_mv
SCHEDULE EVERY 1 HOUR
AS SELECT date_trunc('hour', event_time) as hour, COUNT(*) as events
FROM event_log GROUP BY 1;

CREATE MATERIALIZED VIEW daily_mv
SCHEDULE REFRESH EVERY 1 DAY
AS SELECT * FROM daily_aggregates;

CREATE MATERIALIZED VIEW weekly_mv
SCHEDULE EVERY 2 WEEKS
AS SELECT * FROM weekly_report_data;

CREATE MATERIALIZED VIEW cron_mv
SCHEDULE CRON '0 0 * * *'
AS SELECT * FROM nightly_batch;

CREATE MATERIALIZED VIEW cron_tz_mv
SCHEDULE CRON '0 8 * * MON-FRI' AT TIME ZONE 'America/New_York'
AS SELECT * FROM business_hours_data;

CREATE MATERIALIZED VIEW triggered_mv
TRIGGER ON UPDATE
AS SELECT * FROM streaming_source;

CREATE MATERIALIZED VIEW throttled_mv
TRIGGER ON UPDATE AT MOST EVERY INTERVAL 5 MINUTES
AS SELECT * FROM high_frequency_data;

CREATE MATERIALIZED VIEW filtered_mv
WITH ROW FILTER row_filter_func ON (department, salary)
AS SELECT * FROM employees;

-- ROW FILTER with a schema-qualified function and a literal argument
CREATE MATERIALIZED VIEW filtered_literal_mv
WITH ROW FILTER my_schema.my_filter ON (department, 'ACTIVE')
AS SELECT * FROM employees;

-- ROW FILTER with empty column list (zero-parameter UDF)
CREATE MATERIALIZED VIEW filtered_empty_mv
WITH ROW FILTER my_schema.my_filter ON ()
AS SELECT * FROM employees;

CREATE OR REPLACE MATERIALIZED VIEW comprehensive_mv (
    id INT NOT NULL,
    region STRING,
    total DECIMAL(18, 2) COMMENT 'Total amount'
)
PARTITIONED BY (region)
CLUSTER BY (id)
COMMENT 'Comprehensive materialized view example'
TBLPROPERTIES ('quality' = 'gold')
SCHEDULE EVERY 6 HOURS
AS SELECT id, region, SUM(amount) as total FROM transactions GROUP BY id, region;

CREATE OR REPLACE MATERIALIZED VIEW pk_mv (
    col1 BIGINT PRIMARY KEY
)
AS SELECT col1 FROM tableA;

-- DLT: CREATE OR REFRESH MATERIALIZED VIEW
CREATE OR REFRESH MATERIALIZED VIEW dlt_mv
AS SELECT * FROM streaming_table;

-- DLT: CREATE PRIVATE MATERIALIZED VIEW with column definitions
CREATE PRIVATE MATERIALIZED VIEW dlt_private_mat_view (
    a STRING COMMENT 'a',
    b TIMESTAMP COMMENT 'b'
)
COMMENT 'DLT private materialized view'
AS SELECT a, b FROM live.dlt_bronze;

-- DLT: CREATE OR REFRESH PRIVATE MATERIALIZED VIEW
CREATE OR REFRESH PRIVATE MATERIALIZED VIEW dlt_refresh_private_mat_view (
    a STRING COMMENT 'a',
    b TIMESTAMP COMMENT 'b'
)
COMMENT 'DLT refreshed private materialized view'
AS SELECT a, b FROM live.dlt_bronze;

CREATE OR REPLACE MATERIALIZED VIEW view1
(
    col1 BIGINT,
    col2 STRING,
    col3 BOOLEAN,
    CONSTRAINT pk_view1 PRIMARY KEY (col1),
    CONSTRAINT fk_view1_table1 FOREIGN KEY (col2) REFERENCES table1 (col2)
)
AS
SELECT
    col1,
    col2,
    col3
FROM source_table;

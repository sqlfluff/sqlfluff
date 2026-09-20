-- Databricks CREATE VIEW examples
-- https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-view

CREATE VIEW my_view AS
SELECT * FROM my_table;

CREATE OR REPLACE VIEW my_view AS
SELECT id, name FROM my_table;

CREATE TEMPORARY VIEW temp_view AS
SELECT * FROM my_table WHERE active = true;

CREATE TEMP VIEW short_temp_view AS
SELECT 1 AS x;

CREATE VIEW IF NOT EXISTS my_view AS
SELECT * FROM my_table;

CREATE VIEW employee_view (
    emp_id COMMENT 'Employee ID',
    emp_name COMMENT 'Full name'
) AS SELECT id, name FROM employees;

CREATE VIEW sales_summary
COMMENT 'Aggregated sales data by region'
AS SELECT region, SUM(amount) as total FROM sales GROUP BY region;

CREATE VIEW long_comment_view
COMMENT 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer nec dignissim diam, eu consectetur dolor. Aliquam vestibulum hendrerit massa ac dapibus. Duis luctus ut nunc quis mollis. Pellentesque at ultricies justo. Mauris nulla metus, posuere in lorem eget, mattis eleifend dui. In ullamcorper, enim id posuere mattis, urna ex tempus ipsum, ac bibendum neque arcu at mi. Pellentesque ultricies rutrum nibh a accumsan. Morbi non fermentum eros. Sed at nisl et purus suscipit congue. Vestibulum auctor vehicula maximus. In semper felis neque, eu condimentum lacus pharetra ut. Curabitur nibh metus, dapibus sed tellus ac, commodo porta orci.'
AS SELECT 1 AS col;

CREATE VIEW audited_view
TBLPROPERTIES ('created_by' = 'admin', 'purpose' = 'audit')
AS SELECT * FROM transactions;

CREATE VIEW collated_view
DEFAULT COLLATION UTF8_BINARY
AS SELECT name FROM customers;

CREATE VIEW bound_view
WITH SCHEMA BINDING
AS SELECT id, name FROM source_table;

CREATE VIEW compensated_view
WITH SCHEMA COMPENSATION
AS SELECT * FROM evolving_table;

CREATE VIEW type_evolving_view
WITH SCHEMA TYPE EVOLUTION
AS SELECT * FROM typed_table;

CREATE VIEW evolving_view
WITH SCHEMA EVOLUTION
AS SELECT * FROM dynamic_table;

CREATE VIEW metrics_view
WITH METRICS
AS SELECT date, COUNT(*) as count FROM events GROUP BY date;

CREATE VIEW yaml_metric_view
LANGUAGE YAML
AS $$
metrics:
  - name: daily_sales
    type: sum
    expression: amount
$$;

CREATE OR REPLACE VIEW comprehensive_view (
    id COMMENT 'Primary key',
    value COMMENT 'Metric value'
)
COMMENT 'A comprehensive view example'
DEFAULT COLLATION UTF8_BINARY
TBLPROPERTIES ('version' = '1.0')
WITH SCHEMA COMPENSATION
AS SELECT id, metric_value FROM metrics_table;

CREATE TEMPORARY VIEW temp_summary
COMMENT 'Temporary summary for session'
AS SELECT category, AVG(price) as avg_price FROM products GROUP BY category;

-- Pipeline views declared against the legacy LIVE schema.
-- https://docs.databricks.com/aws/en/ldp/live-schema
CREATE LIVE VIEW filtered_data
AS SELECT a, b FROM live.taxi_raw;

CREATE TEMPORARY LIVE VIEW filtered_data
AS SELECT a, b FROM live.taxi_raw;

CREATE TEMPORARY STREAMING LIVE VIEW customers_silver
AS SELECT a, b FROM stream(live.customers_bronze);

CREATE TEMPORARY LIVE VIEW validated_data (
    a COMMENT 'a',
    b COMMENT 'b',
    CONSTRAINT valid_a EXPECT (a IS NOT NULL),
    CONSTRAINT valid_b EXPECT (b > 0) ON VIOLATION DROP ROW
)
AS SELECT a, b FROM live.taxi_raw;

-- The temporary view backed by a data source.
CREATE TEMPORARY VIEW csv_view
USING csv
OPTIONS (path '/data', header 'true');

CREATE TEMPORARY VIEW csv_view_equals
USING csv
OPTIONS (path = '/data');

CREATE OR REPLACE TEMPORARY VIEW csv_view_replaced
USING csv;

-- The with_clause also takes the parenthesised list form.
CREATE VIEW parenthesised_binding_view
WITH (SCHEMA BINDING)
AS SELECT id FROM source_table;

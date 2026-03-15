-- Databricks CREATE VIEW examples
-- https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-view

CREATE VIEW my_view AS
SELECT * FROM my_table;

CREATE OR REPLACE VIEW my_view AS
SELECT id, name FROM my_table;

CREATE TEMPORARY VIEW temp_view AS
SELECT * FROM my_table WHERE active = true;

CREATE VIEW IF NOT EXISTS my_view AS
SELECT * FROM my_table;

CREATE VIEW employee_view (
    emp_id COMMENT 'Employee ID',
    emp_name COMMENT 'Full name'
) AS SELECT id, name FROM employees;

CREATE VIEW sales_summary
COMMENT 'Aggregated sales data by region'
AS SELECT region, SUM(amount) as total FROM sales GROUP BY region;

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

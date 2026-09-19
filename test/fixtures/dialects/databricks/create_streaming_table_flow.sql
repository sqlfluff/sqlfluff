-- Inline flows. A streaming table takes a flow clause instead of an AS query:
-- https://docs.databricks.com/aws/en/ldp/developer/ldp-sql-ref-create-streaming-table
CREATE OR REFRESH STREAMING TABLE events
FLOW INSERT BY NAME
SELECT * FROM STREAM raw_events;

CREATE OR REFRESH STREAMING TABLE archive_events
FLOW INSERT ONCE BY NAME
SELECT * FROM backfill_events;

CREATE OR REFRESH PRIVATE STREAMING TABLE cdc_target
FLOW AUTO CDC
FROM STREAM cdc_source
KEYS (id)
SEQUENCE BY sequence_num
STORED AS SCD TYPE 2;

CREATE OR REFRESH STREAMING TABLE current_events
FLOW REPLACE WHERE event_date >= '2024-01-01' BY NAME
SELECT * FROM STREAM partial_snapshots;

CREATE OR REFRESH STREAMING TABLE payments
FLOW REPLACE USING (payment_id) SEQUENCE BY payment_date BY NAME
SELECT * FROM STREAM payments_snapshot;

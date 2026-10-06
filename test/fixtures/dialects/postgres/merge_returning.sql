-- PostgreSQL 17 added a RETURNING clause to MERGE.
-- https://www.postgresql.org/docs/17/sql-merge.html

MERGE INTO customer_account ca
USING recent_transactions t
ON t.customer_id = ca.customer_id
WHEN MATCHED THEN
    UPDATE SET balance = balance + transaction_value
RETURNING ca.customer_id, ca.balance;

MERGE INTO wines w
USING wine_stock_changes s
ON s.winename = w.winename
WHEN NOT MATCHED AND s.stock_delta > 0 THEN
    INSERT VALUES(s.winename, s.stock_delta)
WHEN MATCHED AND w.stock + s.stock_delta > 0 THEN
    UPDATE SET stock = w.stock + s.stock_delta
WHEN MATCHED THEN
    DELETE
RETURNING merge_action(), w.*;

MERGE INTO t
USING s
ON t.id = s.id
WHEN MATCHED THEN
    UPDATE SET a = s.a
RETURNING *;

MERGE INTO t
USING s
ON t.id = s.id
WHEN MATCHED THEN
    UPDATE SET a = s.a
RETURNING merge_action() AS action, t.id AS ident, t.a * 2;

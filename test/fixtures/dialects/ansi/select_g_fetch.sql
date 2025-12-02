-- More complex select clause without from clause
SELECT
    NULL::INT AS user_id,
    NULL::INT AS is_paid
FETCH FIRST 0 ROWS ONLY

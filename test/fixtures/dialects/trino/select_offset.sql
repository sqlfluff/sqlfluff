-- Offset without ROW/ROWS
SELECT
    user_id,
    user_name,
    user_email
FROM
    users
WHERE
    user_status = 'active'
OFFSET 10
LIMIT 10;

-- Offset with ROW
SELECT user_id FROM users OFFSET 5 ROW LIMIT 10;

-- Offset with ROWS
SELECT user_id FROM users OFFSET 5 ROWS LIMIT 10;

-- Offset with ORDER BY
SELECT user_id FROM users ORDER BY user_id OFFSET 10 LIMIT 20;

-- Offset only (no LIMIT)
SELECT user_id FROM users OFFSET 0;

-- LIMIT with OFFSET (LIMIT before OFFSET, handled by LimitClauseSegment)
SELECT user_id FROM users LIMIT 20 OFFSET 10;

-- Example SQL File - should pass
SELECT
    u.id,    -- Inline Comment
	/* Block Comment*/
	u.code
FROM user AS u
/* Block Comment
Over Multiple Lines */
WHERE u.batch = 3
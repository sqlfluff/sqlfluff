SELECT
    tbl.name,
    b.value,
    /*
    This is a block comment
    */
    d.something,    -- Which a comment after it
    tbl.foo,
    c.val + b.val / -2 AS a_calculation
FROM tbl
INNER JOIN b ON (tbl.common_id = b.common_id)
JOIN c ON (tbl.id = c.id)
LEFT JOIN d ON (tbl.id = d.other_id)
ORDER BY tbl.name ASC

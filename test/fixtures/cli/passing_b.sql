SELECT
    a.name,
    b.value,
    /*
    This is a block comment
    */
    c.val + b.val / -2 as a_calculation
    d.something,    -- Which a comment after it
    a.foo
FROM tbl as a
INNER JOIN b using(common_id)
JOIN c ON (a.id = c.id)
LEFT JOIN d ON (a.id = d.other_id)
ORDER BY a.name ASC

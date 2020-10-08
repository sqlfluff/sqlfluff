SELECT
    u.id,
    c.first_name,
    c.last_name,
    COUNT(o.user_id)
FROM users as u
JOIN customers as c on u.id = c.user_id
JOIN orders as o on u.id = o.user_id;

-- SQLite specific features with indentation issues
SELECT
    data->>'name' AS name,
    data->'age' AS age,
    json_extract(data, '$.city') AS city
FROM users
WHERE
    data IS NOT NULL
    AND json_valid(data)
    AND name IS NOT 'admin'
ORDER BY
    name,
    age;

-- UPSERT with conflict resolution
INSERT INTO users (id, name, email)
VALUES (1, 'John', 'john@example.com')
ON CONFLICT(id) DO UPDATE SET
    name = excluded.name,
    email = excluded.email
WHERE excluded.name IS NOT users.name;

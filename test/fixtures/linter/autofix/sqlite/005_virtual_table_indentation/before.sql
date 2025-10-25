-- CREATE VIRTUAL TABLE with indentation issues
CREATE VIRTUAL TABLE documents USING fts5(
title,
  content,
author,
    tags
);

-- Views with WHEN clause and IS NOT
CREATE VIEW active_users AS
SELECT
user_id,
name,
email
FROM users
WHERE status IS NOT 'inactive'
AND last_login IS NOT NULL
AND email IS NOT '';

CREATE VIRTUAL TABLE email USING fts5;

CREATE VIRTUAL TABLE email USING fts5(sender, title, body);

CREATE VIRTUAL TABLE IF NOT EXISTS email USING fts5(name, phone, email);

CREATE VIRTUAL TABLE sample_schema.email USING fts3(content, date);

CREATE VIRTUAL TABLE email USING fts5(
    'email text',
    user_id,
    100,
    "complex-field@!#"
);

CREATE VIRTUAL TABLE IF NOT EXISTS sample_schema.email USING fts5(
    'email text',
    user_id,
    0,
    "complex-field@!#"
);

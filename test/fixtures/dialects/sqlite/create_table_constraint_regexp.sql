CREATE TABLE colors (
    css_name TEXT,
    rgb TEXT CHECK(rgb REGEXP '^#[0-9A-F]{6}$')
);

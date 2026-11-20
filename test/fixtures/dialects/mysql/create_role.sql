CREATE ROLE IF NOT EXISTS 'example-role';
CREATE ROLE 'admin', 'developer';
CREATE ROLE IF NOT EXISTS 'app_read'@'localhost', app_write;

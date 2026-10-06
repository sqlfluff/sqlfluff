-- MariaDB supports IF NOT EXISTS on CREATE VIEW (right after the VIEW keyword).
-- MySQL does not. https://mariadb.com/kb/en/create-view/

-- CREATE VIEW [IF NOT EXISTS] view_name AS ...
CREATE VIEW IF NOT EXISTS `v` AS SELECT 1;
CREATE VIEW IF NOT EXISTS v2 AS SELECT `a`, `b` FROM `t`;
CREATE VIEW IF NOT EXISTS v3 (a, b) AS SELECT 1, 2;
CREATE ALGORITHM = MERGE VIEW IF NOT EXISTS v4 AS SELECT 1;
CREATE DEFINER = `admin`@`localhost` SQL SECURITY INVOKER
VIEW IF NOT EXISTS `v5` AS SELECT 1;
CREATE VIEW IF NOT EXISTS `v6` AS SELECT `a` FROM `t` WITH CASCADED CHECK OPTION;

-- Regression: the clause is optional; existing forms are unchanged.
CREATE VIEW `v` AS SELECT 1;
CREATE OR REPLACE VIEW `v` AS SELECT 1;

-- MariaDB allows a table-level IF EXISTS on ALTER TABLE, and IF EXISTS on
-- DROP PARTITION. MySQL does not.
-- https://mariadb.com/docs/server/reference/sql-statements/data-definition/alter/alter-table

-- ALTER TABLE [IF EXISTS] tbl_name
ALTER TABLE IF EXISTS `t` ADD COLUMN `c` INT;
ALTER TABLE IF EXISTS `t` DROP COLUMN IF EXISTS `c`;
ALTER TABLE IF EXISTS `t` RENAME TO `t2`;

-- Regression: the clause is optional, so the bare form is unchanged.
ALTER TABLE `t` ADD COLUMN `c` INT;

-- DROP PARTITION [IF EXISTS] p1[, p2 ...]
ALTER TABLE `t` DROP PARTITION IF EXISTS `p1`;
ALTER TABLE `t` DROP PARTITION IF EXISTS `p1`, `p2`, `p3`;

-- Regression: DROP PARTITION without the clause, and a comma-separated list,
-- must still parse. Other partition verbs are unchanged.
ALTER TABLE `t` DROP PARTITION `p1`;
ALTER TABLE `t` DROP PARTITION `p1`, `p2`;
ALTER TABLE `t` TRUNCATE PARTITION `p1`;
ALTER TABLE `t` COALESCE PARTITION 2;

-- Unquoted identifiers (real-world form)
ALTER TABLE orders DROP PARTITION IF EXISTS p1, p2;

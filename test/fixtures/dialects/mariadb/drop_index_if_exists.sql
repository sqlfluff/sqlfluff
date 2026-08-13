-- MariaDB supports IF EXISTS on the standalone DROP INDEX statement. MySQL does
-- not. https://mariadb.com/kb/en/drop-index/

-- DROP INDEX [IF EXISTS] index_name ON tbl_name
DROP INDEX IF EXISTS `idx` ON `t`;
DROP INDEX IF EXISTS idx_name ON orders;
DROP INDEX IF EXISTS `idx` ON `t` ALGORITHM = INPLACE;
DROP INDEX IF EXISTS `idx` ON `t` LOCK = NONE;

-- Regression: the clause is optional, so the bare form is unchanged.
DROP INDEX `idx` ON `t`;
DROP INDEX `idx` ON `t` ALGORITHM = COPY;

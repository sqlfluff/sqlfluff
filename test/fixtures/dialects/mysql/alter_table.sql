ALTER TABLE `users`
    MODIFY COLUMN
    `name` varchar(255) NOT NULL,
    COMMENT "name of user";

ALTER TABLE `users` MODIFY `name` varchar(255) NOT NULL FIRST;

ALTER TABLE `users` RENAME TO `user`;

ALTER TABLE `user` RENAME AS `users`;

ALTER TABLE `users` RENAME `user`;

ALTER TABLE `users` RENAME COLUMN `col_1` TO `del_col_1`;

ALTER TABLE `users`
CHANGE COLUMN `birthday` `date_of_birth` INT(11) NULL DEFAULT NULL;

ALTER TABLE `users`
CHANGE COLUMN `birthday` `date_of_birth` INT(11) NOT NULL;

ALTER TABLE `users`
CHANGE COLUMN `birthday` `date_of_birth` INT(11) FIRST;

ALTER TABLE `users`
CHANGE COLUMN `birthday` `date_of_birth` INT(11) AFTER `name`;

ALTER TABLE `users`
DROP COLUMN `age`;

ALTER TABLE `foo`.`bar`
ADD CONSTRAINT `index_name` UNIQUE(`col_1`, `col_2`, `col_3`);

ALTER TABLE `foo`.`bar` ADD UNIQUE `index_name`(`col_1`, `col_2`, `col_3`);

ALTER TABLE `foo`.`bar`
ADD CONSTRAINT `index_name` UNIQUE INDEX (`col_1`, `col_2`, `col_3`);

ALTER TABLE `foo`.`bar`
ADD UNIQUE INDEX `index_name`(`col_1`, `col_2`, `col_3`);

ALTER TABLE `foo`.`bar` ADD INDEX `index_name`(`col_1`, `col_2`, `col_3`);

ALTER TABLE `foo`.`bar` ADD INDEX `index_name`(`col_1`, `col_2`, `col_3`)
KEY_BLOCK_SIZE = 8;

ALTER TABLE `foo`.`bar` ADD INDEX `index_name`(`col_1`, `col_2`, `col_3`)
KEY_BLOCK_SIZE 8;

ALTER TABLE `foo`.`bar` ADD INDEX `index_name`(`col_1`, `col_2`, `col_3`)
KEY_BLOCK_SIZE 8 COMMENT 'index for col_1, col_2, col_3';

ALTER TABLE `foo`.`bar` DROP INDEX `index_name`;

ALTER TABLE `foo`.`bar` RENAME INDEX `index_name` to `new_index_name`;

ALTER TABLE `foo`.`bar` RENAME KEY `key_name` to `new_key_name`;

ALTER TABLE `x` ADD CONSTRAINT FOREIGN KEY(`xk`) REFERENCES `y`(`yk`);

ALTER TABLE `users`
    ADD COLUMN `active` tinyint(1) DEFAULT '0';

ALTER TABLE `users`
    ADD COLUMN IF NOT EXISTS `active` tinyint(1) DEFAULT '0';

ALTER TABLE `foo` ADD `bar` INT FIRST;

ALTER TABLE `foo` ADD COLUMN d INT GENERATED ALWAYS AS (a*abs(b)) VIRTUAL;

ALTER TABLE `foo` ADD COLUMN e TEXT GENERATED ALWAYS AS (substr(c,b,b+1)) STORED;

ALTER TABLE `foo` ADD COLUMN d INT AS (a*abs(b));

ALTER TABLE `foo` ADD COLUMN e TEXT AS (substr(c,b,b+1)) STORED;

ALTER TABLE `foo` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

ALTER TABLE CUST TRUNCATE PARTITION data_dt;

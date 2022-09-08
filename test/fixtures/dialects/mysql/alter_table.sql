ALTER TABLE `users`
    MODIFY COLUMN
    `name` varchar(255) NOT NULL,
    COMMENT "name of user";

ALTER TABLE `users` RENAME TO `user`;

ALTER TABLE `user` RENAME AS `users`;

ALTER TABLE `users` RENAME `user`;

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

ALTER TABLE `foo`.`bar` DROP INDEX `index_name`

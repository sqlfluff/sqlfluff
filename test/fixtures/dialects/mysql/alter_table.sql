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

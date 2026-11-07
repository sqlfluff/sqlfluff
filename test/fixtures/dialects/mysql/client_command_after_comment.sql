-- The mysql client, unlike the mariadb one, allows a comment before a command.
/* comment */ SOURCE after_comment.sql
/* comment */ DELIMITER $$
SELECT 1 $$
/* comment */ DELIMITER ;

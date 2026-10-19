DELIMITER $$
SELECT 1 $$
SELECT 2; SELECT 3 $$
SELECT 4$$SELECT 5$$
SELECT '$$', "$$", `$$` FROM (SELECT 1 AS `$$`) AS t $$
SELECT 6 -- $$ is in a comment
$$
SELECT 7 # $$ is in a comment
$$
SELECT 8 /* $$ */ $$
SELECT 9 --$$
DELIMITER $$ text the client ignores
SELECT 10 $$
DELIMITER //
SELECT 11 //
delimiter ;;
SELECT 12; SELECT 13;;
DELIMITER '$$'
SELECT 14 $$
DELIMITER	"//"
SELECT 15 //
DELIMITER a\ b
SELECT 16 a b
\d $$ SELECT 17 $$
SELECT 18 $$
SELECT 19 \g
SELECT 20 \G
SELECT 21 --\g
   DELIMITER ;
SELECT 22;
SELECT 23 --;

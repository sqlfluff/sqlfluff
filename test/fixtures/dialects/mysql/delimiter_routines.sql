-- The delimiters routines are usually written with: `$$` (MySQL Workbench),
-- `//` (the MySQL manual) and `;;` (mysqldump).
CREATE TABLE t (a INT);

DELIMITER $$
CREATE PROCEDURE count_to(IN n INT)
BEGIN
    DECLARE i INT DEFAULT 0;
    WHILE i < n DO
        SET i = i + 1;
    END WHILE;
    SELECT i;
END$$
DELIMITER ;

DELIMITER //
CREATE FUNCTION double_it(x INT) RETURNS INT
DETERMINISTIC
BEGIN
    RETURN x * 2;
END //
DELIMITER ;

DELIMITER ;;
CREATE TRIGGER t_before_insert BEFORE INSERT ON t FOR EACH ROW
BEGIN
    SET NEW.a = NEW.a + 1;
END ;;
DELIMITER ;

CALL count_to(3);
SELECT double_it(4);

-- A delimiter that looks like a name is still the delimiter.
DELIMITER $$
DELETE FROM t $$
SET @a = 1 $$
CREATE PROCEDURE p() BEGIN SELECT 1; END $$
DELIMITER go
DELETE FROM t go
SET @b = 2 go
DELIMITER ;
SELECT @a, @b;

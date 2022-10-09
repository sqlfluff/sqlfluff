CREATE TRIGGER delete_members_after_transactions AFTER DELETE ON transactions
FOR EACH ROW DELETE FROM members WHERE username NOT IN
(SELECT UNIQUE(username) FROM transactions);



CREATE TRIGGER some_trigger AFTER DELETE ON some_table
FOR EACH ROW
BEGIN
    DELETE FROM some_table;
    INSERT INTO some_table;
END;


CREATE TRIGGER ins_sum BEFORE INSERT ON account
FOR EACH ROW SET @sum = @sum + NEW.amount;


CREATE TRIGGER some_trigger AFTER DELETE ON some_table FOR EACH ROW DELETE FROM other_table;
CREATE TRIGGER some_trigger BEFORE DELETE ON some_table FOR EACH ROW DELETE FROM other_table;
CREATE TRIGGER some_trigger AFTER UPDATE ON some_table FOR EACH ROW DELETE FROM other_table;
CREATE TRIGGER some_trigger BEFORE UPDATE ON some_table FOR EACH ROW DELETE FROM other_table;
CREATE TRIGGER some_trigger AFTER INSERT ON some_table FOR EACH ROW DELETE FROM other_table;
CREATE TRIGGER some_trigger BEFORE INSERT ON some_table FOR EACH ROW DELETE FROM other_table;

CREATE TRIGGER IF NOT EXISTS some_trigger AFTER DELETE ON some_table
FOR EACH ROW DELETE FROM other_table;

CREATE TRIGGER some_trigger AFTER DELETE ON some_table FOR EACH ROW
FOLLOWS some_other_trigger
DELETE FROM other_table;
CREATE TRIGGER some_trigger AFTER DELETE ON some_table FOR EACH ROW
PRECEDES some_other_trigger
DELETE FROM other_table;


CREATE
DEFINER=`root`@`127.0.0.1`
TRIGGER ins_sum BEFORE INSERT ON account
FOR EACH ROW SET @sum = @sum + NEW.amount;
CREATE
DEFINER=CURRENT_USER
TRIGGER ins_sum BEFORE INSERT ON account
FOR EACH ROW SET @sum = @sum + NEW.amount;

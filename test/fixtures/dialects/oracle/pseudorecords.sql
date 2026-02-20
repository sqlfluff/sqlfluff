CREATE OR REPLACE TRIGGER example_trigger
BEFORE INSERT OR UPDATE ON example_table
FOR EACH ROW
BEGIN
    -- Using pseudorecords in assignments
    :NEW.column_name := :OLD.column_name;

    -- Using pseudorecords in conditions
    IF :NEW.val > :OLD.val THEN
        :NEW.status := 'changed';
    END IF;

    -- PARENT pseudorecord
    :NEW.parent_val := :PARENT.val;
END;

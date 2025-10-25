CREATE TRIGGER update_trigger
BEFORE UPDATE OF name, email ON users
FOR EACH ROW
WHEN
new.name IS NOT old.name
OR new.email IS NOT old.email
BEGIN
UPDATE audit_log
SET last_modified = datetime('now')
WHERE user_id = NEW.id;
INSERT INTO change_history (
user_id,
old_name,
new_name,
change_date
) VALUES (
NEW.id,
OLD.name,
NEW.name,
datetime('now')
);
END;

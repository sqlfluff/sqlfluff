ALTER TRIGGER foo ON table_name RENAME TO new_name;

ALTER TRIGGER foo ON table_name DEPENDS ON EXTENSION extension_name;

ALTER TRIGGER foo ON table_name NO DEPENDS ON EXTENSION extension_name;

ALTER TRIGGER emp_stamp ON emp RENAME TO emp_track_chgs;

ALTER TRIGGER emp_stamp ON emp DEPENDS ON EXTENSION emplib;

-- AlterTableColumnClausesSegment
ALTER TABLE table_name RENAME COLUMN old_column_name TO new_column_name;

-- add_column_clause
ALTER TABLE table_name
ADD (column_name NUMBER(18));

-- modify_column_clauses
ALTER TABLE table_name
MODIFY column_name NUMBER(18);

-- drop_column_clause
ALTER TABLE table_name
DROP COLUMN column_name;

ALTER TABLE table_name
DROP (column_name_one, column_name_two);

-- AlterTableConstraintClauses
ALTER TABLE table_name
ADD CONSTRAINT constraint_name
FOREIGN KEY (column_name) REFERENCES other_table_name (other_column_name);

-- rename_constraint_clause
ALTER TABLE table_name RENAME CONSTRAINT source_constraint_name TO target_constraint_name;

-- drop_constraint_clause
ALTER TABLE table_name DROP CONSTRAINT constraint_name;

ALTER TABLE table_name
MODIFY (column_name NOT NULL ENABLE);

ALTER TABLE table_name MODIFY
(column_name DEFAULT 10);

ALTER TABLE table_name
MODIFY (column_name DEFAULT 10 NOT NULL ENABLE);

ALTER TABLE employees ADD CONSTRAINT salary_check CHECK (salary > 0);

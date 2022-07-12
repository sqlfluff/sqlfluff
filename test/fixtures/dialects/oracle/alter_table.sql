-- AlterTableColumnClausesSegment
ALTER TABLE table_name RENAME COLUMN old_column_name TO new_column_name;

-- drop_column_clause
ALTER TABLE table_name
DROP COLUMN column_name;

ALTER TABLE table_name
DROP (column_name_one, column_name_two);

-- AlterTableConstraintClauses
ALTER TABLE table_name
ADD CONSTRAINT constraint_name
FOREIGN KEY (column_name) REFERENCES other_table_name (other_column_name);
